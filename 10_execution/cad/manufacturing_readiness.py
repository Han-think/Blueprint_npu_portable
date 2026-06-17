"""
manufacturing_readiness.py -- MRL-0.5 evidence scoring for 5 seed packages
============================================================================

This is not a manufacturing certification tool. It checks whether each seed has
enough design-for-manufacturing evidence to support the next improvement loop:
process limits, wall/tolerance data, support/orientation notes, fastener/joint
sanity, service access, inspection cues, mass/process traceability, and risk
coverage.

Usage:
    python 10_execution/cad/manufacturing_readiness.py
    python 10_execution/cad/manufacturing_readiness.py cubesat

Outputs:
    10_execution/cad/output/<seed>/<seed>_mrl05.json
    10_execution/cad/output/mrl05_summary.json
"""
from __future__ import annotations

import json
import re
import struct
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
SEEDS = REPO / "20_dataset" / "seeds"
OUT = REPO / "10_execution" / "cad" / "output"
SEED_LIST = ["cubesat", "tiltrotor", "robot_arm", "small_launch_vehicle", "long_range_recon_wing", "haptic_glove"]

PROCESS_MIN_WALL = {
    "FDM": 1.2,
    "SLA": 0.8,
    "LPBF": 0.7,
    "DED": 1.5,
    "BinderJet": 1.0,
}


def clamp(v: float, lo: int = 0, hi: int = 100) -> int:
    return int(round(max(lo, min(hi, v))))


def status_for(score: int) -> str:
    if score >= 78:
        return "ready"
    if score >= 58:
        return "watch"
    return "weak"


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def text_blob(*items) -> str:
    return json.dumps(items, ensure_ascii=False, sort_keys=True).lower()


def stl_stats(path: Path) -> dict:
    if not path.exists():
        return {"exists": False, "bytes": 0, "triangles": 0}
    data = path.read_bytes()
    triangles = 0
    if len(data) >= 84:
        try:
            n = struct.unpack_from("<I", data, 80)[0]
            if 84 + n * 50 <= len(data):
                triangles = int(n)
            else:
                triangles = len(re.findall(rb"\bfacet\s+normal\b", data[:2_000_000]))
        except Exception:
            triangles = 0
    return {"exists": True, "bytes": len(data), "triangles": triangles}


def svg_stats(path: Path) -> dict:
    if not path.exists():
        return {"exists": False, "bytes": 0, "markers": []}
    txt = path.read_text(encoding="utf-8", errors="ignore")
    markers = []
    for pat in ["FRONT CUTAWAY", "SIDE INTERFACE", "Part-tree internals", "service", "datum", "interface"]:
        if pat.lower() in txt.lower():
            markers.append(pat)
    return {"exists": True, "bytes": path.stat().st_size, "markers": markers}


def score_seed(seed: str) -> dict:
    pkg_path = SEEDS / seed / "package.json"
    asm_path = SEEDS / seed / "assembly.json"
    pkg = load_json(pkg_path, {})
    asm = load_json(asm_path, {})
    bp = pkg.get("schema_v6_blueprint", {})
    constraints = bp.get("brief", {}).get("constraints", {})
    cad = bp.get("cad_brief", {})
    pp = bp.get("print_profile", {})
    slicer = bp.get("slicer_job", {})
    verify = bp.get("verify", [])
    risk = bp.get("risk", [])
    ops = bp.get("geometry_ops", [])
    delta = pkg.get("assembly_delta", {})

    stl = stl_stats(OUT / seed / f"{seed}.stl")
    svg = svg_stats(OUT / seed / f"{seed}_drawing.svg")
    blob = text_blob(pkg, asm, bp, svg)

    process = constraints.get("process") or pp.get("process")
    min_wall = constraints.get("min_wall_mm") or cad.get("wall_thickness_mm", {}).get("min")
    tol = constraints.get("tol_mm")
    tol_map = cad.get("tolerances_mm", {})
    required_wall = PROCESS_MIN_WALL.get(str(process), 1.0)
    wall_ok = isinstance(min_wall, (int, float)) and min_wall >= required_wall
    wall_score = clamp(
        (28 if process else 0)
        + (30 if wall_ok else 12 if isinstance(min_wall, (int, float)) else 0)
        + (18 if constraints.get("material") or cad.get("material") else 0)
        + (14 if tol is not None or tol_map else 0)
        + (10 if len(ops) >= 12 else 5 if ops else 0)
    )

    supports = pp.get("supports")
    orientation = pp.get("orientation") or cad.get("build_direction")
    overhang = constraints.get("overhang_deg")
    support_score = clamp(
        (26 if overhang is not None else 0)
        + (26 if supports else 0)
        + (24 if orientation else 0)
        + (14 if any("support" in str(x).lower() for x in pkg.get("print_strategy", [])) else 0)
        + (10 if pp.get("layer_mm") else 0)
    )

    fasteners = asm.get("fasteners", [])
    joints = asm.get("joints", [])
    valid_fasteners = [
        f for f in fasteners
        if f.get("id") and f.get("kind") and f.get("qty", 0) > 0 and f.get("joins") and f.get("hole")
    ]
    clearance_joints = [j for j in joints if isinstance(j.get("clearance_mm"), (int, float))]
    fastener_score = clamp(
        (20 if asm.get("version") == "bp-assembly-v1" else 0)
        + min(28, len(valid_fasteners) * 10)
        + min(26, len(clearance_joints) * 9)
        + (12 if asm.get("hardware_bom") else 0)
        + (14 if all(f.get("anchor") for f in fasteners) and fasteners else 0)
    )

    access = delta.get("retained_service_access_points", [])
    service_terms = len(re.findall(r"service|access|removable|inspection|cover|panel|slot|hinge|cable|datum", blob))
    service_score = clamp(
        min(42, len(access) * 11)
        + min(28, service_terms * 2)
        + (16 if "service" in " ".join(svg.get("markers", [])).lower() else 0)
        + (14 if pkg.get("assembly_sequence") else 0)
    )

    verify_terms = len(re.findall(r"datum|inspection|tolerance|clearance|wall|mass|support|overhang|interface", blob))
    pass_count = sum(1 for v in verify if v.get("result") == "pass")
    warn_count = sum(1 for v in verify if v.get("result") == "warn")
    fail_count = sum(1 for v in verify if v.get("result") == "fail")
    inspection_score = clamp(
        min(36, len(verify) * 9)
        + min(22, pass_count * 7)
        + min(18, verify_terms)
        + (14 if len(svg.get("markers", [])) >= 4 else 5 if svg.get("exists") else 0)
        + (10 if tol is not None or clearance_joints else 0)
        - warn_count * 5
        - fail_count * 18
    )

    mass_score = clamp(
        (22 if cad.get("mass_est_g") else 0)
        + (18 if pp.get("filament_g") or pp.get("powder_kg") else 0)
        + (16 if slicer.get("input_stl") and slicer.get("output") else 0)
        + (20 if stl["exists"] and stl["bytes"] > 10_000 else 0)
        + (16 if stl["triangles"] >= 2500 else 8 if stl["triangles"] else 0)
        + (8 if svg["exists"] and svg["bytes"] > 1000 else 0)
    )

    safety_boundary = text_blob(pkg.get("target", {}).get("not_for", ""), bp.get("brief", {}).get("requirements", ""))
    mitigated = [r for r in risk if r.get("desc") and r.get("mit")]
    high = [r for r in risk if r.get("severity") == "high"]
    risk_score = clamp(
        min(35, len(mitigated) * 9)
        + (18 if verify else 0)
        + (18 if "not_for" in pkg.get("target", {}) or "not for" in safety_boundary else 0)
        + (14 if "educational" in safety_boundary or "mockup" in safety_boundary else 0)
        + (15 if len(risk) >= 3 else 6 if risk else 0)
        - max(0, len(high) - 1) * 7
    )

    categories = [
        {"name": "wall/process readiness", "score": wall_score, "note": f"process={process or 'missing'}, min_wall={min_wall}, required_floor={required_wall}"},
        {"name": "overhang/support readiness", "score": support_score, "note": f"overhang={overhang}, supports={supports or 'missing'}, orientation={orientation or 'missing'}"},
        {"name": "fastener/joint sanity", "score": fastener_score, "note": f"valid fasteners {len(valid_fasteners)}/{len(fasteners)}, clearance joints {len(clearance_joints)}/{len(joints)}"},
        {"name": "serviceability", "score": service_score, "note": f"service access points {len(access)}, service terms {service_terms}, svg markers {len(svg.get('markers', []))}"},
        {"name": "inspection readiness", "score": inspection_score, "note": f"verify pass/warn/fail {pass_count}/{warn_count}/{fail_count}, inspection terms {verify_terms}"},
        {"name": "mass/process traceability", "score": mass_score, "note": f"mass={cad.get('mass_est_g', 'missing')}g, stl triangles={stl['triangles']}, svg={svg['exists']}"},
        {"name": "risk coverage", "score": risk_score, "note": f"mitigated risks {len(mitigated)}/{len(risk)}, high risks {len(high)}"},
    ]
    score = clamp(sum(c["score"] for c in categories) / len(categories))
    issues = [
        f"{c['name']}: {c['score']}/100. {c['note']}"
        for c in categories
        if c["score"] < 70
    ][:6]
    if issues:
        loop_head = f"Improve MRL-0.5 manufacturing evidence for {seed}: target weak categories before changing styling."
        issue_lines = [f"- {issue}" for issue in issues]
    else:
        loop_head = f"Preserve MRL-0.5 manufacturing evidence for {seed}: keep datum, tolerance, service, inspection, and risk traces while improving geometry."
        issue_lines = []
    loop_feedback = [
        loop_head,
        *issue_lines,
        "- Add or preserve datum/tolerance/inspection statements tied to visible geometry and assembly interfaces.",
        "- Keep the design at educational mockup level; do not claim certification or real flight/manufacturing readiness.",
    ]

    return {
        "schema": "blueprint_mrl05_manufacturing_readiness_v1",
        "seed": seed,
        "target": pkg.get("target", {}),
        "score": score,
        "status": status_for(score),
        "disclaimer": "MRL-0.5 readiness evidence only; not manufacturing, flight, medical, or certification approval.",
        "categories": categories,
        "issues": issues,
        "loop_feedback": "\n".join(loop_feedback),
        "evidence": {
            "stl": stl,
            "svg": svg,
            "process": process,
            "material": constraints.get("material") or cad.get("material"),
            "min_wall_mm": min_wall,
            "tol_mm": tol,
            "fasteners": len(fasteners),
            "joints": len(joints),
            "service_access_points": len(access),
            "verify": {"pass": pass_count, "warn": warn_count, "fail": fail_count, "total": len(verify)},
            "risks": {"total": len(risk), "mitigated": len(mitigated), "high": len(high)},
        },
    }


def write_report(report: dict) -> None:
    seed = report["seed"]
    out_dir = OUT / seed
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{seed}_mrl05.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def main(argv: list[str]) -> int:
    seeds = [a for a in argv[1:] if not a.startswith("--")] or SEED_LIST
    reports = []
    for seed in seeds:
        report = score_seed(seed)
        write_report(report)
        reports.append(report)
        print(f"{seed}: {report['score']}/100 {report['status']} · issues {len(report['issues'])}")

    summary = {
        "schema": "blueprint_mrl05_summary_v1",
        "seeds": len(reports),
        "average_score": clamp(sum(r["score"] for r in reports) / max(1, len(reports))),
        "ready": sum(1 for r in reports if r["status"] == "ready"),
        "watch": sum(1 for r in reports if r["status"] == "watch"),
        "weak": sum(1 for r in reports if r["status"] == "weak"),
        "reports": [
            {
                "seed": r["seed"],
                "score": r["score"],
                "status": r["status"],
                "issues": r["issues"],
                "loop_feedback": r["loop_feedback"],
                "report": f"/output/{r['seed']}/{r['seed']}_mrl05.json",
            }
            for r in reports
        ],
        "disclaimer": "MRL-0.5 readiness evidence only; not manufacturing approval.",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "mrl05_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"summary: {summary['average_score']}/100 · ready/watch/weak {summary['ready']}/{summary['watch']}/{summary['weak']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
