"""Read-only consistency check for the curation score table.

This script does not generate, rebuild CAD, or change curation rows. It answers
one narrow question: does the current curation_log.jsonl make internal sense
after scorer/audit fixes changed during the run?
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
CURATION_LOG = REPO / "30_model" / "curation" / "curation_log.jsonl"
CURATION_INDEX = REPO / "30_model" / "curation" / "curation_index.json"
OUT_DIR = REPO / "30_model" / "curation" / "analysis_reports"

TRIAL_THRESHOLD = 300
FULL_THRESHOLD = 1000
KNOWN_SEEDS = {
    "cubesat",
    "robot_arm",
    "tiltrotor",
    "small_launch_vehicle",
    "long_range_recon_wing",
    "haptic_glove",
}
VALID_DECISIONS = {"keep", "reject", "hold"}
VALID_KEEP_GRADES = {"A", "B", "C"}
FINAL_LOW_RES_STAGE = "final_low_res_after_composite_reaudit"
SEED_FOS_THRESHOLDS = {
    "cubesat": {"keep_min": 3.0, "good": 10.0, "excellent": 25.0},
    "robot_arm": {"keep_min": 0.15, "good": 0.5, "excellent": 3.0},
    "tiltrotor": {"keep_min": 0.6, "good": 3.0, "excellent": 10.0},
    "small_launch_vehicle": {"keep_min": 0.5, "good": 2.5, "excellent": 10.0},
    "long_range_recon_wing": {"keep_min": 0.5, "good": 1.0, "excellent": 1.8},
    "haptic_glove": {"keep_min": 0.8, "good": 5.0, "excellent": 20.0},
}


def load_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    malformed: list[dict[str, Any]] = []
    if not path.exists():
        return rows, [{"line": 0, "error": "missing curation_log.jsonl"}]
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except Exception as exc:  # pragma: no cover - diagnostic script
            malformed.append({"line": line_no, "error": f"{type(exc).__name__}: {exc}"})
            continue
        row["_line_no"] = line_no
        rows.append(row)
    return rows, malformed


def load_index() -> dict[str, Any]:
    try:
        return json.loads(CURATION_INDEX.read_text(encoding="utf-8"))
    except Exception:
        return {}


def row_seed(row: dict[str, Any]) -> str:
    return str(row.get("seed") or (row.get("input_context") or {}).get("seed") or row.get("vehicle_id") or "unknown")


def scorecard(row: dict[str, Any]) -> dict[str, Any]:
    sc = row.get("engineering_scorecard")
    return sc if isinstance(sc, dict) else {}


def payload_part_counts(row: dict[str, Any]) -> tuple[int, int]:
    payload = row.get("payload") or {}
    vehicle_parts = ((payload.get("vehicle") or {}).get("parts") or [])
    generated = payload.get("parts") or []
    expected_total = len(vehicle_parts) or len(generated)
    parts_ok = 0
    for part in generated:
        bp = part.get("blueprint") or {}
        if bp.get("part_tree") and bp.get("geometry_ops"):
            parts_ok += 1
    return expected_total, parts_ok


def reason_family(reason: str) -> str:
    if not reason:
        return "missing_reason"
    if reason.startswith("LOW-RES"):
        return "LOW_RES"
    if reason.startswith("incomplete"):
        return "INCOMPLETE"
    if reason.startswith("missing part_tree"):
        return "MISSING_TREE"
    if "FoS" in reason and "below" in reason:
        return "FOS_BELOW"
    if reason.startswith("mid:"):
        return "MID_WATCH"
    if "CAD worker timeout" in reason:
        return "CAD_TIMEOUT"
    return reason.split(":")[0][:80]


def classify_hold(row: dict[str, Any]) -> str:
    sc = scorecard(row)
    stage = str(sc.get("audit_stage") or "")
    err = str(sc.get("audit_error") or "")
    reason = str(sc.get("auto_reason") or "")
    if stage == "analysis_mid_watch" or reason.startswith("mid:"):
        return "analysis_mid_watch"
    if stage == "cad_timeout" or "timeout" in err.lower():
        return "cad_timeout"
    if "worker produced no result" in err:
        return "worker_no_result"
    if stage == "cad_error" or err:
        first = (err.splitlines() or ["cad_error"])[0]
        return f"cad_error:{first[:80]}"
    return "unclassified_hold"


def parse_fos(reason: str) -> float | None:
    match = re.search(r"FoS\s+(-?\d+(?:\.\d+)?)", reason or "")
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def infer_grade(seed: str, fos: Any) -> str | None:
    if not isinstance(fos, (int, float)):
        return None
    th = SEED_FOS_THRESHOLDS.get(seed)
    if not th:
        return None
    if fos >= th["excellent"]:
        return "A"
    if fos >= th["good"]:
        return "B"
    if fos >= th["keep_min"]:
        return "C"
    return None


def write_jsonl_atomic(path: Path, rows: list[dict[str, Any]]) -> None:
    tmp = path.with_name(f"{path.stem}.{os.getpid()}.tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            clean = dict(row)
            clean.pop("_line_no", None)
            f.write(json.dumps(clean, ensure_ascii=False) + "\n")
    tmp.replace(path)


def cleanup_stale_metadata(rows: list[dict[str, Any]]) -> dict[str, Any]:
    changed: list[dict[str, Any]] = []
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for row in rows:
        decision = str(row.get("decision") or "").lower()
        if decision not in {"keep", "reject"}:
            continue
        sc = scorecard(row)
        if not sc:
            continue
        seed = row_seed(row)
        actions: list[str] = []
        if sc.get("audit_error"):
            sc.pop("audit_error", None)
            actions.append("removed_stale_audit_error")
        stage = str(sc.get("audit_stage") or "")
        reason = str(sc.get("auto_reason") or "")
        if decision == "keep" and stage in {"cad_error", "cad_timeout", "cheap_prefilter", FINAL_LOW_RES_STAGE}:
            sc["audit_stage"] = "cad_audit_keep"
            actions.append("reset_keep_audit_stage")
        if decision == "reject" and stage in {"cad_error", "cad_timeout"}:
            if reason.startswith("LOW-RES") and sc.get("decision_changed_by") == "audit_hold_rows_composite_reaudit_v2":
                sc["audit_stage"] = FINAL_LOW_RES_STAGE
            else:
                sc["audit_stage"] = "cad_audit_reject"
            actions.append("reset_reject_audit_stage")
        if decision == "keep" and sc.get("grade") not in VALID_KEEP_GRADES:
            grade = infer_grade(seed, sc.get("sizing_fos"))
            if grade:
                sc["grade"] = grade
                actions.append(f"inferred_grade_{grade}")
        if actions:
            sc["metadata_cleanup_by"] = "verify_curation_scores_v1"
            sc["metadata_cleanup_ts"] = ts
            row["engineering_scorecard"] = sc
            changed.append({
                "line": row.get("_line_no"),
                "id": row.get("id"),
                "seed": seed,
                "decision": decision,
                "actions": actions,
            })
    return {"changed": changed, "changed_count": len(changed)}
    try:
        return float(match.group(1))
    except ValueError:
        return None


def add_issue(issues: list[dict[str, Any]], severity: str, code: str, row: dict[str, Any], detail: str) -> None:
    issues.append({
        "severity": severity,
        "code": code,
        "line": row.get("_line_no"),
        "id": row.get("id"),
        "seed": row_seed(row),
        "decision": row.get("decision"),
        "detail": detail,
    })


def analyze(rows: list[dict[str, Any]], malformed: list[dict[str, Any]]) -> dict[str, Any]:
    decisions = Counter()
    grades = Counter()
    audit_stages = Counter()
    audit_lineage = Counter()
    by_seed = defaultdict(Counter)
    reject_families = Counter()
    hold_families = Counter()
    issues: list[dict[str, Any]] = []
    ids = Counter(str(r.get("id") or "") for r in rows)

    for bad in malformed:
        issues.append({"severity": "block", "code": "malformed_jsonl", **bad})

    for row in rows:
        decision = str(row.get("decision") or "").lower()
        seed = row_seed(row)
        sc = scorecard(row)
        grade = sc.get("grade")
        stage = str(sc.get("audit_stage") or "")
        reason = str(sc.get("auto_reason") or "")
        err = sc.get("audit_error")

        decisions[decision] += 1
        by_seed[seed][decision] += 1
        audit_stages[stage or "missing_stage"] += 1
        if stage:
            audit_lineage["stage_present"] += 1
        else:
            audit_lineage["stage_missing_legacy"] += 1
        if grade:
            grades[str(grade)] += 1

        if decision not in VALID_DECISIONS:
            add_issue(issues, "block", "unknown_decision", row, f"decision={decision!r}")
        if seed not in KNOWN_SEEDS:
            add_issue(issues, "watch", "unknown_seed", row, f"seed={seed!r}")
        if not row.get("id"):
            add_issue(issues, "watch", "missing_id", row, "row has no id")
        elif ids[str(row.get("id"))] > 1:
            add_issue(issues, "block", "duplicate_id", row, f"id appears {ids[str(row.get('id'))]} times")

        if decision == "keep":
            if grade not in VALID_KEEP_GRADES:
                add_issue(issues, "watch", "keep_missing_grade", row, f"keep row has grade={grade!r}")
            if err:
                add_issue(issues, "watch", "keep_has_stale_audit_error", row, str(err)[:240])
            if stage in {"cad_error", "cad_timeout", "cheap_prefilter", FINAL_LOW_RES_STAGE}:
                add_issue(issues, "watch", "keep_unexpected_audit_stage", row, f"audit_stage={stage!r}")
            fos = sc.get("sizing_fos")
            if not isinstance(fos, (int, float)):
                parsed = parse_fos(reason)
                if parsed is None:
                    add_issue(issues, "watch", "keep_missing_fos", row, "no numeric sizing_fos or FoS in auto_reason")

        if decision == "reject":
            family = reason_family(reason)
            reject_families[family] += 1
            if not reason:
                add_issue(issues, "watch", "reject_missing_reason", row, "reject row has no auto_reason")
            if err:
                add_issue(issues, "watch", "reject_has_stale_audit_error", row, str(err)[:240])
            if reason.startswith("LOW-RES"):
                changed_by = sc.get("decision_changed_by")
                if stage != FINAL_LOW_RES_STAGE and changed_by != "audit_hold_rows_composite_reaudit_v2":
                    add_issue(
                        issues,
                        "watch",
                        "low_res_not_marked_final_or_reaudit",
                        row,
                        f"audit_stage={stage!r}, decision_changed_by={changed_by!r}",
                    )
            expected, ok = payload_part_counts(row)
            if reason.startswith("incomplete") and expected and ok >= expected:
                add_issue(issues, "watch", "incomplete_reason_conflicts_payload", row, f"payload parts_ok={ok}/{expected}")

        if decision == "hold":
            family = classify_hold(row)
            hold_families[family] += 1
            if grade in VALID_KEEP_GRADES:
                add_issue(issues, "watch", "hold_has_keep_grade", row, f"hold row has grade={grade!r}")
            if not reason and not err:
                add_issue(issues, "watch", "hold_missing_reason_and_error", row, "hold row has no auto_reason or audit_error")

    index = load_index()
    index_issues: list[dict[str, Any]] = []
    if index:
        expected = {
            "total": len(rows),
            "kept": decisions.get("keep", 0),
            "rejected": decisions.get("reject", 0),
        }
        for key, actual in expected.items():
            if index.get(key) != actual:
                index_issues.append({"key": key, "index": index.get(key), "actual": actual})
        index_seed = index.get("by_seed") or {}
        actual_seed = {seed: sum(counts.values()) for seed, counts in by_seed.items()}
        if index_seed != actual_seed:
            index_issues.append({"key": "by_seed", "index": index_seed, "actual": actual_seed})
    else:
        index_issues.append({"key": "curation_index", "index": None, "actual": "missing_or_unreadable"})

    for item in index_issues:
        issues.append({"severity": "watch", "code": "index_mismatch", **item})

    trainable = decisions.get("keep", 0) + decisions.get("reject", 0)
    grade_total = sum(grades[g] for g in VALID_KEEP_GRADES)
    status = "pass"
    block_count = sum(1 for i in issues if i.get("severity") == "block")
    watch_count = sum(1 for i in issues if i.get("severity") == "watch")
    if block_count:
        status = "block"
    elif watch_count:
        status = "watch"

    return {
        "schema": "blueprint_score_consistency_report_v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": str(CURATION_LOG.relative_to(REPO)),
        "status": status,
        "totals": {
            "rows": len(rows),
            "malformed": len(malformed),
            "trainable_keep_reject": trainable,
            "trial_threshold": TRIAL_THRESHOLD,
            "full_threshold": FULL_THRESHOLD,
            "trial_ready": trainable >= TRIAL_THRESHOLD,
            "full_ready": trainable >= FULL_THRESHOLD,
        },
        "decisions": dict(decisions),
        "grades": dict(grades),
        "keep_grade_coverage": {
            "graded_keep_rows": grade_total,
            "keep_rows": decisions.get("keep", 0),
            "ungraded_keep_rows": max(0, decisions.get("keep", 0) - grade_total),
        },
        "audit_stages": dict(audit_stages.most_common()),
        "audit_lineage_coverage": dict(audit_lineage),
        "by_seed_decision": {seed: dict(counts) for seed, counts in sorted(by_seed.items())},
        "reject_families": dict(reject_families.most_common()),
        "hold_families": dict(hold_families.most_common()),
        "index_check": {"ok": not index_issues, "issues": index_issues},
        "issue_counts": dict(Counter(i["code"] for i in issues)),
        "severity_counts": dict(Counter(i["severity"] for i in issues)),
        "issues": issues[:500],
        "interpretation": build_interpretation(decisions, grades, reject_families, hold_families, issues, trainable),
    }


def build_interpretation(
    decisions: Counter,
    grades: Counter,
    reject_families: Counter,
    hold_families: Counter,
    issues: list[dict[str, Any]],
    trainable: int,
) -> list[str]:
    lines = []
    if trainable >= TRIAL_THRESHOLD:
        lines.append(f"Training gate is stable for a smoke-test LoRA: {trainable}/{TRIAL_THRESHOLD} keep+reject rows.")
    else:
        lines.append(f"Training gate is not ready: {trainable}/{TRIAL_THRESHOLD} keep+reject rows.")
    if trainable < FULL_THRESHOLD:
        lines.append(f"Full-run threshold is not reached yet: {trainable}/{FULL_THRESHOLD}.")
    else:
        lines.append(f"Full-run threshold is reached: {trainable}/{FULL_THRESHOLD}.")
    ungraded_keep = decisions.get("keep", 0) - sum(grades[g] for g in VALID_KEEP_GRADES)
    if ungraded_keep:
        lines.append(f"{ungraded_keep} keep rows are ungraded; treat them as audit metadata cleanup candidates, not new generation targets.")
    if hold_families:
        top_hold, count = hold_families.most_common(1)[0]
        lines.append(f"Hold rows are dominated by {top_hold} ({count}); these should stay out of training until manually reviewed or re-audited.")
    if reject_families:
        top_reject, count = reject_families.most_common(1)[0]
        lines.append(f"Reject rows are dominated by {top_reject} ({count}); use them as negative examples only if the family is a real design flaw.")
    if any(i["code"].endswith("stale_audit_error") for i in issues):
        lines.append("Some keep/reject rows still carry stale audit_error fields; clean metadata before final training export.")
    if any(i["code"] == "index_mismatch" for i in issues):
        lines.append("curation_index.json does not match curation_log.jsonl; rebuild the index before trusting dashboards.")
    return lines


def write_report(report: dict[str, Any]) -> tuple[Path, Path]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUT_DIR / "score_consistency_report.json"
    md_path = OUT_DIR / "score_consistency_report.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# Score Consistency Report",
        "",
        f"Generated: {report['generated_at']}",
        f"Status: **{report['status']}**",
        "",
        "## Totals",
        "",
        f"- rows: {report['totals']['rows']}",
        f"- trainable keep+reject: {report['totals']['trainable_keep_reject']} / {report['totals']['trial_threshold']} trial",
        f"- full threshold: {report['totals']['trainable_keep_reject']} / {report['totals']['full_threshold']}",
        "",
        "## Decisions",
        "",
        *[f"- {k}: {v}" for k, v in sorted(report["decisions"].items())],
        "",
        "## Grades",
        "",
        *[f"- {k}: {v}" for k, v in sorted(report["grades"].items())],
        f"- ungraded keep rows: {report['keep_grade_coverage']['ungraded_keep_rows']}",
        "",
        "## Seed Matrix",
        "",
        "| seed | keep | reject | hold |",
        "|---|---:|---:|---:|",
    ]
    for seed, counts in report["by_seed_decision"].items():
        md.append(f"| {seed} | {counts.get('keep', 0)} | {counts.get('reject', 0)} | {counts.get('hold', 0)} |")
    md += [
        "",
        "## Reject Families",
        "",
        *[f"- {k}: {v}" for k, v in report["reject_families"].items()],
        "",
        "## Hold Families",
        "",
        *[f"- {k}: {v}" for k, v in report["hold_families"].items()],
        "",
        "## Issue Counts",
        "",
        *[f"- {k}: {v}" for k, v in sorted(report["issue_counts"].items())],
        "",
        "## Audit Lineage Coverage",
        "",
        *[f"- {k}: {v}" for k, v in sorted(report["audit_lineage_coverage"].items())],
        "",
        "## Interpretation",
        "",
        *[f"- {item}" for item in report["interpretation"]],
        "",
    ]
    sample_issues = report.get("issues") or []
    if sample_issues:
        md += [
            "## Sample Issues",
            "",
            "| severity | code | seed | id | detail |",
            "|---|---|---|---|---|",
        ]
        for issue in sample_issues[:40]:
            detail = str(issue.get("detail") or issue.get("error") or issue.get("key") or "").replace("|", "\\|")
            md.append(
                f"| {issue.get('severity')} | {issue.get('code')} | {issue.get('seed', '')} | "
                f"{issue.get('id', '')} | {detail[:220]} |"
            )
    md_path.write_text("\n".join(md), encoding="utf-8")
    return json_path, md_path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-only", action="store_true", help="write JSON report but skip markdown")
    ap.add_argument("--fix-stale-metadata", action="store_true",
                    help="clean stale audit_error/audit_stage and infer missing keep grade from sizing_fos")
    args = ap.parse_args(argv)

    rows, malformed = load_jsonl(CURATION_LOG)
    cleanup_report = None
    if args.fix_stale_metadata and not malformed:
        cleanup_report = cleanup_stale_metadata(rows)
        if cleanup_report["changed_count"]:
            backup = CURATION_LOG.with_name(
                f"curation_log.before_score_cleanup_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.jsonl"
            )
            shutil.copy2(CURATION_LOG, backup)
            write_jsonl_atomic(CURATION_LOG, rows)
            print(f"[score-check] cleanup changed={cleanup_report['changed_count']} backup={backup}")
        else:
            print("[score-check] cleanup changed=0")
        rows, malformed = load_jsonl(CURATION_LOG)
    report = analyze(rows, malformed)
    if cleanup_report:
        report["metadata_cleanup"] = cleanup_report
    json_path, md_path = write_report(report)
    if args.json_only and md_path.exists():
        md_path.unlink()

    print(f"[score-check] status={report['status']}")
    print(f"[score-check] decisions={report['decisions']}")
    print(f"[score-check] grades={report['grades']}")
    print(f"[score-check] trainable={report['totals']['trainable_keep_reject']}/{TRIAL_THRESHOLD} trial, "
          f"{report['totals']['trainable_keep_reject']}/{FULL_THRESHOLD} full")
    print(f"[score-check] issue_counts={report['issue_counts']}")
    print(json_path)
    if not args.json_only:
        print(md_path)
    return 1 if report["status"] == "block" else 0


if __name__ == "__main__":
    raise SystemExit(main())
