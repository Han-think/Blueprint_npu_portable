"""
assembly_interference_audit.py -- placed assembly AABB/fit audit
================================================================

Reads already generated STEP/print metadata and produces a review-grade
placement/interference report. This is deliberately MRL-0.5 evidence, not a
manufacturing/certification collision guarantee.

Inputs:
  output/<seed>/assembly_structure.json
  output/<seed>/print/assembly_manifest.json
  output/<seed>/print/print_readiness.json

Outputs:
  output/<seed>/assembly_interference_report.json
  output/interference_summary.json

Usage:
  python 10_execution/cad/assembly_interference_audit.py <seed>
  python 10_execution/cad/assembly_interference_audit.py --all
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "10_execution" / "cad" / "output"
SEED_LIST = [
    "cubesat",
    "tiltrotor",
    "robot_arm",
    "small_launch_vehicle",
    "long_range_recon_wing",
    "haptic_glove",
]

NEAR_CLEARANCE_MM = 1.0
MATE_GAP_WARN_MM = 8.0
EXPLODED_PREVIEW_GAP_MM = 80.0


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def clamp(v: float, lo: int = 0, hi: int = 100) -> int:
    return int(round(max(lo, min(hi, v))))


def status_for(blocked: int, warnings: int, missing_inputs: bool = False) -> str:
    if blocked or missing_inputs:
        return "block"
    if warnings:
        return "watch"
    return "pass"


def pair_key(a: str | None, b: str | None) -> str:
    return "::".join(sorted([str(a or ""), str(b or "")]))


def failed_checks(part: dict) -> list[str]:
    checks = part.get("checks") or {}
    failed = [k for k, ok in checks.items() if ok is False]
    if part.get("error"):
        failed.append(str(part["error"]))
    return failed


def part_aabb(center: list[float], size: list[float]) -> dict:
    cx, cy, cz = [float(v or 0) for v in center[:3]]
    sx, sy, sz = [max(0.0, float(v or 0)) for v in size[:3]]
    mn = [cx - sx / 2, cy - sy / 2, cz - sz / 2]
    mx = [cx + sx / 2, cy + sy / 2, cz + sz / 2]
    return {
        "center_mm": [round(cx, 3), round(cy, 3), round(cz, 3)],
        "size_mm": [round(sx, 3), round(sy, 3), round(sz, 3)],
        "min_mm": [round(v, 3) for v in mn],
        "max_mm": [round(v, 3) for v in mx],
    }


def aabb_relation(a: dict, b: dict) -> dict:
    amin, amax = a["aabb_mm"]["min_mm"], a["aabb_mm"]["max_mm"]
    bmin, bmax = b["aabb_mm"]["min_mm"], b["aabb_mm"]["max_mm"]
    overlaps = [min(amax[i], bmax[i]) - max(amin[i], bmin[i]) for i in range(3)]
    separated = [max(bmin[i] - amax[i], amin[i] - bmax[i], 0.0) for i in range(3)]
    intersects = all(v > 0 for v in overlaps)
    clearance = 0.0 if intersects else math.sqrt(sum(v * v for v in separated))
    overlap_volume = overlaps[0] * overlaps[1] * overlaps[2] if intersects else 0.0
    return {
        "intersects": intersects,
        "overlap_axes_mm": [round(max(0.0, v), 3) for v in overlaps],
        "overlap_volume_mm3": round(max(0.0, overlap_volume), 3),
        "clearance_distance_mm": round(clearance, 3),
    }


def collect_parts(structure: dict, manifest: dict) -> list[dict]:
    manifest_parts = {p.get("part_id"): p for p in manifest.get("parts", []) if p.get("part_id")}
    out = []
    for sp in structure.get("parts", []) or []:
        pid = sp.get("part_id")
        mp = manifest_parts.get(pid, {})
        # structure 자체 bbox 우선(분할로 manifest part_id가 어긋나도 정확). 없으면 manifest.
        size = sp.get("bbox_mm") or mp.get("bbox_mm") or [0, 0, 0]
        center = sp.get("placement_translation_mm") or [0, 0, 0]
        aabb = part_aabb(center, size)
        out.append({
            "part_id": pid,
            "label": sp.get("label") or mp.get("label") or pid,
            "qty": sp.get("qty", mp.get("print_count", 1)),
            "step_file": sp.get("step_file"),
            "print_file": mp.get("file"),
            "volume_mm3": mp.get("volume_mm3"),
            "placement_translation_mm": center,
            "placement_rotation_deg": sp.get("placement_rotation_deg") or [0, 0, 0],
            "aabb_mm": aabb,
            "obb_mm": {
                "center_mm": aabb["center_mm"],
                "size_mm": aabb["size_mm"],
                "rotation_deg": sp.get("placement_rotation_deg") or [0, 0, 0],
                "note": "axis-aligned OBB because current exported placements use zero rotation",
            },
            "bbox_source": "print/assembly_manifest.json",
        })
    return out


def collect_joints(structure: dict, manifest: dict) -> list[dict]:
    joints = []
    for j in structure.get("mates", []) or []:
        joints.append({
            "id": j.get("id"),
            "part_a": j.get("part_a"),
            "part_b": j.get("part_b"),
            "mate": j.get("mate"),
            "clearance_mm": j.get("clearance_mm", 0),
            "containment": bool(j.get("containment")),
            "source": "assembly_structure",
            "note": j.get("note", ""),
        })
    seen = {pair_key(j.get("part_a"), j.get("part_b")) + f"::{j.get('mate')}" for j in joints}
    for j in manifest.get("joints", []) or []:
        key = pair_key(j.get("male_part"), j.get("female_part")) + f"::{j.get('mate')}"
        if key in seen:
            continue
        joints.append({
            "id": j.get("id"),
            "part_a": j.get("male_part"),
            "part_b": j.get("female_part"),
            "mate": j.get("mate"),
            "clearance_mm": j.get("clearance_mm", 0),
            "containment": bool(j.get("containment")),
            "source": "print_manifest",
            "note": j.get("note", ""),
        })
    return joints


def classify_pair(a: dict, b: dict, declared: bool, contained: bool = False) -> tuple[str, dict]:
    rel = aabb_relation(a, b)
    if rel["intersects"]:
        if contained:
            # 의도된 내부 중첩(보드가 베이 안에 들어감 등) — 설계상 정상, 경고 아님
            return "expected_internal_containment", rel
        if declared:
            return "warning_declared_overlap_needs_review", rel
        return "blocked_unmapped_overlap", rel
    if rel["clearance_distance_mm"] <= NEAR_CLEARANCE_MM:
        return "near_clearance", rel
    return "clear", rel


def mate_alignment(joints: list[dict], parts_by_id: dict[str, dict]) -> list[dict]:
    rows = []
    for j in joints:
        pa, pb = j.get("part_a"), j.get("part_b")
        if not pa or not pb:
            rows.append({**j, "status": "missing_part_reference", "issue": "joint does not name both parts"})
            continue
        if pa == pb:
            rows.append({**j, "status": "self_mate_needs_review", "issue": f"{pa} mates to itself"})
            continue
        a, b = parts_by_id.get(pa), parts_by_id.get(pb)
        if not a or not b:
            rows.append({**j, "status": "missing_part_geometry", "issue": f"missing geometry for {pa} or {pb}"})
            continue
        rel = aabb_relation(a, b)
        clearance = float(j.get("clearance_mm") or 0)
        if rel["intersects"]:
            status = "declared_contact_or_internal_overlap"
            issue = ""
        elif rel["clearance_distance_mm"] <= max(MATE_GAP_WARN_MM, clearance + 2.0):
            status = "aligned_near_clearance"
            issue = ""
        elif rel["clearance_distance_mm"] <= EXPLODED_PREVIEW_GAP_MM:
            status = "exploded_preview_gap"
            issue = f"declared mate has {rel['clearance_distance_mm']}mm display gap; verify final assembled position"
        else:
            status = "wide_mate_gap"
            issue = f"declared mate gap {rel['clearance_distance_mm']}mm exceeds exploded preview threshold"
        rows.append({**j, "status": status, "issue": issue, "relation": rel})
    return rows


def fastener_findings(manifest: dict, part_ids: set[str]) -> list[str]:
    out = []
    for f in manifest.get("fasteners", []) or []:
        fid = f.get("id", "fastener")
        joins = [p for p in f.get("joins", []) or [] if p]
        missing = [p for p in joins if p not in part_ids]
        if len(joins) < 2:
            out.append(f"{fid}: fastener joins fewer than two parts")
        if missing:
            out.append(f"{fid}: fastener references missing part(s) {', '.join(missing)}")
        if not f.get("anchor"):
            out.append(f"{fid}: fastener missing anchor")
        if not f.get("hole"):
            out.append(f"{fid}: fastener missing hole/tap/through evidence")
    return out


def score_report(blocked_pairs: int, warning_pairs: int, mate_warnings: int,
                 clearance_warnings: int, print_blocked: int, fastener_issues: int,
                 missing_inputs: bool) -> int:
    score = 100
    score -= min(55, blocked_pairs * 18)
    score -= min(42, print_blocked * 16)
    score -= min(28, warning_pairs * 7)
    score -= min(24, mate_warnings * 6)
    score -= min(20, clearance_warnings * 5)
    score -= min(18, fastener_issues * 6)
    if missing_inputs:
        score -= 35
    return clamp(score)


def audit_seed(seed: str) -> dict:
    base = OUT / seed
    structure_path = base / "assembly_structure.json"
    manifest_path = base / "print" / "assembly_manifest.json"
    readiness_path = base / "print" / "print_readiness.json"

    structure = load_json(structure_path, {})
    manifest = load_json(manifest_path, {})
    readiness = load_json(readiness_path, {})
    missing = [str(p.relative_to(REPO)) for p in (structure_path, manifest_path) if not p.exists()]

    parts = collect_parts(structure, manifest) if structure and manifest else []
    parts_by_id = {p["part_id"]: p for p in parts if p.get("part_id")}
    part_ids = set(parts_by_id)
    joints = collect_joints(structure, manifest)
    declared_pairs = {pair_key(j.get("part_a"), j.get("part_b")) for j in joints if j.get("part_a") and j.get("part_b")}
    containment_pairs = {
        pair_key(j.get("part_a"), j.get("part_b"))
        for j in joints if j.get("containment") and j.get("part_a") and j.get("part_b")
    }

    pairs = []
    for i, a in enumerate(parts):
        for b in parts[i + 1:]:
            pk = pair_key(a.get("part_id"), b.get("part_id"))
            declared = pk in declared_pairs
            status, rel = classify_pair(a, b, declared, pk in containment_pairs)
            pairs.append({
                "part_a": a.get("part_id"),
                "part_b": b.get("part_id"),
                "declared_joint": declared,
                "status": status,
                **rel,
            })

    mate_rows = mate_alignment(joints, parts_by_id)
    clearance_warnings = [
        w for w in manifest.get("warnings", []) or []
        if "clearance not auto-applied" in str(w).lower()
    ]
    blocked_print_parts = []
    for p in readiness.get("parts", []) or []:
        if p.get("do_not_print") and p.get("file") != "fit_test_coupon.stl":
            blocked_print_parts.append({
                "file": p.get("file"),
                "size_mm": p.get("size_mm"),
                "failed_checks": failed_checks(p),
            })
    fastener_issues = fastener_findings(manifest, part_ids)
    missing_order = not manifest.get("assembly_order")

    blocked_pair_rows = [p for p in pairs if p["status"].startswith("blocked")]
    warning_pair_rows = [p for p in pairs if p["status"].startswith("warning") or p["status"] == "near_clearance"]
    mate_warning_rows = [m for m in mate_rows if m.get("issue")]
    warnings_total = len(warning_pair_rows) + len(mate_warning_rows) + len(clearance_warnings) + len(fastener_issues) + (1 if missing_order else 0)
    blocked_total = len(blocked_pair_rows) + len(blocked_print_parts)

    score = score_report(
        len(blocked_pair_rows),
        len(warning_pair_rows),
        len(mate_warning_rows),
        len(clearance_warnings),
        len(blocked_print_parts),
        len(fastener_issues),
        bool(missing),
    )
    status = status_for(blocked_total, warnings_total, bool(missing))

    findings = []
    for p in blocked_pair_rows[:4]:
        findings.append(f"unmapped collision {p['part_a']} <-> {p['part_b']} overlap {p['overlap_volume_mm3']}mm^3")
    for p in warning_pair_rows[:4]:
        if p["status"] == "near_clearance":
            findings.append(f"near-clearance pair {p['part_a']} <-> {p['part_b']} gap {p['clearance_distance_mm']}mm")
        else:
            findings.append(f"declared overlap {p['part_a']} <-> {p['part_b']} needs fit review")
    for m in mate_warning_rows[:4]:
        findings.append(f"mate alignment {m.get('part_a')} <-> {m.get('part_b')}: {m.get('issue')}")
    for p in blocked_print_parts[:4]:
        findings.append(f"blocked print {p['file']}: {', '.join(p['failed_checks'])}")
    for w in clearance_warnings[:4]:
        findings.append(str(w))
    findings.extend(fastener_issues[:4])
    if missing_order:
        findings.append("assembly_order missing from print manifest")
    if missing:
        findings.append(f"missing audit input(s): {', '.join(missing)}")

    loop_lines = [
        f"Improve placement/interference evidence for {seed}: status {status}, score {score}/100.",
    ]
    if blocked_pair_rows:
        loop_lines.append("- Resolve unmapped collision pairs: " + ", ".join(f"{p['part_a']}<->{p['part_b']}" for p in blocked_pair_rows[:6]))
    if mate_warning_rows:
        loop_lines.append("- Align declared mates or label them as exploded preview: " + ", ".join(f"{m.get('part_a')}<->{m.get('part_b')}" for m in mate_warning_rows[:6]))
    if blocked_print_parts:
        loop_lines.append("- Fix do_not_print parts before keep: " + ", ".join(p["file"] for p in blocked_print_parts[:6]))
    if clearance_warnings:
        loop_lines.append("- Replace explicit base ops or add per-feature clearance evidence so joint clearance is actually applied.")
    if fastener_issues:
        loop_lines.append("- Repair fastener join/anchor/hole evidence for: " + "; ".join(fastener_issues[:3]))
    loop_lines.append("- Keep this as educational mock assembly evidence; do not claim certified interference-free manufacturing.")

    report = {
        "schema": "blueprint_assembly_interference_audit_v1",
        "seed": seed,
        "status": status,
        "score": score,
        "disclaimer": "AABB-based design-review evidence only; not certified CAD collision, fit, flight, or manufacturing approval.",
        "inputs": {
            "assembly_structure": structure_path.exists(),
            "assembly_manifest": manifest_path.exists(),
            "print_readiness": readiness_path.exists(),
            "missing": missing,
        },
        "thresholds": {
            "near_clearance_mm": NEAR_CLEARANCE_MM,
            "mate_gap_warn_mm": MATE_GAP_WARN_MM,
            "exploded_preview_gap_mm": EXPLODED_PREVIEW_GAP_MM,
        },
        "counts": {
            "parts": len(parts),
            "declared_joints": len(joints),
            "total_pairs": len(pairs),
            "passed_pairs": len([p for p in pairs if p["status"] == "clear"]),
            "warning_pairs": len(warning_pair_rows),
            "blocked_pairs": len(blocked_pair_rows),
            "mate_warnings": len(mate_warning_rows),
            "clearance_warnings": len(clearance_warnings),
            "blocked_print_parts": len(blocked_print_parts),
            "fastener_issues": len(fastener_issues),
        },
        "parts": parts,
        "pair_matrix": pairs,
        "mate_alignment": mate_rows,
        "clearance_warnings": clearance_warnings,
        "blocked_print_parts": blocked_print_parts,
        "fastener_findings": fastener_issues,
        "findings": findings[:12],
        "loop_feedback": "\n".join(loop_lines),
    }
    return report


def write_report(report: dict) -> None:
    out_dir = OUT / report["seed"]
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "assembly_interference_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_summary(reports: list[dict]) -> None:
    summary = {
        "schema": "blueprint_interference_summary_v1",
        "seeds": len(reports),
        "average_score": clamp(sum(r.get("score", 0) for r in reports) / max(1, len(reports))),
        "pass": sum(1 for r in reports if r.get("status") == "pass"),
        "watch": sum(1 for r in reports if r.get("status") == "watch"),
        "block": sum(1 for r in reports if r.get("status") == "block"),
        "reports": [
            {
                "seed": r["seed"],
                "score": r["score"],
                "status": r["status"],
                "counts": r["counts"],
                "findings": r["findings"],
                "loop_feedback": r["loop_feedback"],
                "report": f"/output/{r['seed']}/assembly_interference_report.json",
            }
            for r in reports
        ],
        "disclaimer": "AABB placement/interference evidence only; not certified CAD/manufacturing approval.",
    }
    (OUT / "interference_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if a]
    seeds = SEED_LIST if not args or args[0] == "--all" else args
    reports = []
    for seed in seeds:
        report = audit_seed(seed)
        write_report(report)
        reports.append(report)
        c = report["counts"]
        print(
            f"{seed}: {report['score']}/100 {report['status']} - "
            f"pairs pass/watch/block {c['passed_pairs']}/{c['warning_pairs']}/{c['blocked_pairs']} - "
            f"print blocked {c['blocked_print_parts']}"
        )
    write_summary(reports)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
