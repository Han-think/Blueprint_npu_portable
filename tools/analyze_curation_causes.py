"""Analyze keep/reject/hold causes from 30_model/curation/curation_log.jsonl."""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CURATION_LOG = REPO / "30_model" / "curation" / "curation_log.jsonl"
OUT_DIR = REPO / "30_model" / "curation" / "analysis_reports"


def reason_family(reason: str) -> str:
    if not reason:
        return "missing_reason"
    if reason.startswith("LOW-RES"):
        return "low_res_geometry"
    if reason.startswith("incomplete"):
        return "incomplete_blueprint_set"
    if reason.startswith("missing part_tree"):
        return "missing_part_tree"
    if "FoS" in reason and "below" in reason:
        return "structural_fos_below_threshold"
    return reason.split(":")[0][:80]


def iter_rows():
    with CURATION_LOG.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def extract_low_res_parts(reason: str) -> list[str]:
    m = re.search(r"LOW-RES parts \[(.*?)\]", reason or "")
    if not m:
        return []
    return re.findall(r"'([^']+)'", m.group(1))


def collect_pattern_ops(payload: dict) -> Counter:
    counter = Counter()
    for part in payload.get("parts") or []:
        bp = part.get("blueprint") or {}
        for op in bp.get("geometry_ops") or []:
            op_name = op.get("op") or "missing_op"
            counter[op_name] += 1
    return counter


def main() -> int:
    decisions = Counter()
    audit_stages = Counter()
    by_seed_decision = defaultdict(Counter)
    reject_families = Counter()
    reject_family_by_seed = defaultdict(Counter)
    low_res_parts = Counter()
    cad_errors = Counter()
    cad_error_by_seed = defaultdict(Counter)
    cad_error_ops = Counter()
    samples = defaultdict(list)

    for row in iter_rows():
        decision = row.get("decision", "missing_decision")
        seed = row.get("seed", "unknown")
        sc = row.get("engineering_scorecard") or {}
        stage = sc.get("audit_stage") or ""
        reason = sc.get("auto_reason") or ""
        err = sc.get("audit_error") or ""

        decisions[decision] += 1
        audit_stages[stage] += 1
        by_seed_decision[seed][decision] += 1

        if decision == "reject":
            family = reason_family(reason)
            reject_families[family] += 1
            reject_family_by_seed[seed][family] += 1
            for part_id in extract_low_res_parts(reason):
                low_res_parts[(seed, part_id)] += 1
            if len(samples[f"reject:{family}"]) < 8:
                samples[f"reject:{family}"].append({
                    "id": row.get("id"),
                    "seed": seed,
                    "reason": reason[:500],
                })

        if decision == "hold" and stage in ("cad_error", "cad_timeout"):
            key = (err or stage).splitlines()[0][:160]
            cad_errors[key] += 1
            cad_error_by_seed[seed][key] += 1
            cad_error_ops.update(collect_pattern_ops(row.get("payload") or {}))
            if len(samples[f"cad:{key}"]) < 8:
                op_sample = []
                for part in (row.get("payload") or {}).get("parts") or []:
                    bp = part.get("blueprint") or {}
                    for op in bp.get("geometry_ops") or []:
                        if op.get("op") in ("pattern_linear", "pattern_polar", "mirror"):
                            op_sample.append({"part": part.get("id"), "op": op})
                        if len(op_sample) >= 5:
                            break
                    if len(op_sample) >= 5:
                        break
                samples[f"cad:{key}"].append({
                    "id": row.get("id"),
                    "seed": seed,
                    "error": err[:500],
                    "ops": op_sample,
                })

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "schema": "blueprint_curation_cause_analysis_v1",
        "generated_at": datetime.now().isoformat(),
        "source": str(CURATION_LOG.relative_to(REPO)),
        "decisions": dict(decisions),
        "audit_stages": dict(audit_stages),
        "by_seed_decision": {k: dict(v) for k, v in sorted(by_seed_decision.items())},
        "reject_families": dict(reject_families.most_common()),
        "reject_family_by_seed": {k: dict(v) for k, v in sorted(reject_family_by_seed.items())},
        "top_low_res_parts": [
            {"seed": seed, "part_id": part_id, "count": count}
            for (seed, part_id), count in low_res_parts.most_common(80)
        ],
        "cad_errors": dict(cad_errors.most_common()),
        "cad_error_by_seed": {k: dict(v) for k, v in sorted(cad_error_by_seed.items())},
        "cad_error_op_mix": dict(cad_error_ops.most_common()),
        "samples": dict(samples),
        "interpretation": [
            "Rejects are dominated by low_res_geometry: generated parts exist, but many child parts received fewer than the CAD gate minimum ops.",
            "CAD holds are dominated by build_solid/build123d conversion errors, especially ValueError: other must be a list of Locations.",
            "CAD error rows should not be treated as bad design examples until the converter is repaired or the offending ops are normalized.",
            "Keep/reject rows are already sufficient for a trial LoRA; hold rows should become repair/evaluator regression cases.",
        ],
        "recommended_actions": [
            "Generation: strengthen S2 to require 4+ ops per part_tree child and reject/repair sparse child op distribution before persistence.",
            "Generation: avoid emitting mirror until build_solid supports it, or rewrite mirror to explicit duplicated geometry before CAD.",
            "CAD: harden build_solid pattern_linear/pattern_polar/mirror handling with safe fallback markers and never let converter errors classify as reject.",
            "Analysis: create a cad_error regression set from the hold rows and run it after every build_solid change.",
        ],
    }
    json_path = OUT_DIR / "curation_cause_analysis.json"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        "# Curation Cause Analysis",
        "",
        f"Generated: {report['generated_at']}",
        "",
        "## Decision Totals",
        "",
        *[f"- {k}: {v}" for k, v in decisions.most_common()],
        "",
        "## Reject Families",
        "",
        *[f"- {k}: {v}" for k, v in reject_families.most_common()],
        "",
        "## CAD Error Families",
        "",
        *[f"- {k}: {v}" for k, v in cad_errors.most_common()],
        "",
        "## Seed Decision Matrix",
        "",
        "| seed | keep | reject | hold |",
        "|---|---:|---:|---:|",
    ]
    for seed, counts in sorted(by_seed_decision.items()):
        md_lines.append(f"| {seed} | {counts.get('keep', 0)} | {counts.get('reject', 0)} | {counts.get('hold', 0)} |")
    md_lines += [
        "",
        "## Top Low-Res Part IDs",
        "",
        *[f"- {seed} / {part_id}: {count}" for (seed, part_id), count in low_res_parts.most_common(30)],
        "",
        "## Interpretation",
        "",
        *[f"- {item}" for item in report["interpretation"]],
        "",
        "## Recommended Actions",
        "",
        *[f"- {item}" for item in report["recommended_actions"]],
        "",
    ]
    md_path = OUT_DIR / "curation_cause_analysis.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    print(json_path)
    print(md_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
