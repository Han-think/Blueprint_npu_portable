"""Audit downloaded reference CAD/mesh assets for design-learning value.

This is a local, read-only audit. It does not verify legal rights by itself;
it classifies engineering usefulness and highlights license/source items that
need human review before training use.
"""
from __future__ import annotations

import json
import math
import re
import struct
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "20_dataset" / "reference_assets"
INDEX = ROOT / "_index.jsonl"
REPORT_JSON = ROOT / "_reference_quality_audit.json"
REPORT_MD = ROOT / "_reference_quality_audit.md"

REFERENCE_EXTS = {
    ".step", ".stp", ".iges", ".igs", ".stl", ".obj", ".3mf", ".fcstd", ".scad", ".vsp3",
    ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".csv", ".md", ".txt", ".json",
}
CAD_EXTS = {".step", ".stp", ".iges", ".igs", ".stl", ".obj", ".3mf", ".fcstd", ".scad", ".vsp3"}
MANUFACTURING_EXTS = {".step", ".stp", ".scad", ".fcstd", ".vsp3"}
PRINT_EXTS = {".stl", ".3mf", ".scad"}
ASSEMBLY_WORDS = {
    "assembly", "base", "link", "forearm", "upperarm", "shoulder", "wrist", "hand", "finger",
    "palm", "thumb", "bend", "split", "mid", "top", "bottom", "skeleton", "body", "mainbody",
    "nose", "cone", "fin", "fins", "ring", "engine", "bay", "prop", "rotor", "wing", "hershey",
    "b777", "rectangle", "controller", "plate", "block", "crankshaft", "piston", "cylinder",
    "head", "manifold", "turbo", "pump", "impeller", "volute", "shaft", "bearing", "seal",
    "flange", "valve", "port", "gallery", "busbar", "cell", "cooling", "cold", "rail",
    "carriage", "ballscrew", "gearbox", "gear", "housing", "o-ring", "gland", "sensor",
}
PRINT_WORDS = {"stl", "print", "prepped", "3d", "scad", "slicer"}
DOC_WORDS = {
    "dimension", "dimensions", "bom", "prototype", "battery", "pack", "eps", "mppt", "pdu",
    "solar", "wall", "power", "subsystem", "document", "readme", "hardware", "pcb", "arch",
    "architecture", "orbit", "simulation", "coolant", "lubrication", "oil", "gasket",
    "cutaway", "service", "maintenance", "pressure", "thermal", "hydraulic", "valvetrain",
    "bearing", "tolerance", "datum", "seal", "o-ring",
}
SEED_EXPECTATIONS = {
    "cubesat": {"step_min": 2, "print_min": 2, "assembly_terms": {"top", "bottom", "mid", "skeleton"}},
    "haptic_glove": {"print_min": 10, "assembly_terms": {"finger", "thumb", "palm", "link", "base", "bend"}},
    "long_range_recon_wing": {"vsp3_min": 3, "assembly_terms": {"wing", "prop", "rotor", "b777", "rectangle"}},
    "tiltrotor": {"vsp3_min": 3, "assembly_terms": {"wing", "prop", "rotor"}},
    "robot_arm": {"print_min": 10, "assembly_terms": {"base", "shoulder", "forearm", "upperarm", "wrist"}},
    "small_launch_vehicle": {"print_min": 5, "assembly_terms": {"assembly", "nose", "fin", "ring", "engine", "body"}},
    "inline_6_engine_gasoline": {"step_min": 2, "assembly_terms": {"block", "crankshaft", "piston", "head", "manifold"}},
    "inline_6_engine_diesel": {"step_min": 2, "assembly_terms": {"block", "crankshaft", "injector", "turbo", "rail"}},
    "centrifugal_pump": {"step_min": 1, "assembly_terms": {"pump", "volute", "impeller", "shaft", "seal", "flange"}},
    "hydraulic_manifold": {"step_min": 1, "assembly_terms": {"manifold", "valve", "port", "gallery", "plug"}},
    "battery_pack_module": {"step_min": 1, "assembly_terms": {"battery", "cell", "busbar", "bms", "cooling", "connector"}},
    "liquid_cold_plate": {"step_min": 1, "assembly_terms": {"cold", "plate", "channel", "manifold", "gasket"}},
    "cnc_axis_carriage": {"step_min": 1, "assembly_terms": {"carriage", "rail", "bearing", "ballscrew", "sensor"}},
    "gearbox_reducer": {"step_min": 1, "assembly_terms": {"gearbox", "gear", "shaft", "bearing", "housing", "seal"}},
    "underwater_sealed_sensor_housing": {"step_min": 1, "assembly_terms": {"housing", "sensor", "o-ring", "gland", "cap", "cradle"}},
    "liquid_rocket_engine_academic": {"print_min": 2, "assembly_terms": {"engine", "chamber", "nozzle", "turbopump", "injector", "cooling", "feed", "instrumentation", "academic"}},
}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def clamp(n: float, lo: int = 0, hi: int = 100) -> int:
    return int(max(lo, min(hi, round(n))))


def load_index() -> list[dict[str, Any]]:
    rows = []
    if not INDEX.exists():
        return rows
    for line in INDEX.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows


def read_sample(path: Path, limit: int = 256_000) -> bytes:
    with path.open("rb") as f:
        return f.read(limit)


def stl_stats(path: Path) -> dict[str, Any]:
    size = path.stat().st_size
    sample = read_sample(path, min(size, 1024))
    if size >= 84:
        tri_count = struct.unpack("<I", read_sample(path, 84)[80:84])[0]
        expected = 84 + tri_count * 50
        if expected == size:
            return {"format": "binary_stl", "triangles": tri_count}
    text = read_sample(path, min(size, 1_000_000)).decode("utf-8", errors="ignore").lower()
    return {"format": "ascii_stl", "triangles": text.count("facet normal")}


def obj_stats(path: Path) -> dict[str, Any]:
    text = read_sample(path, 2_000_000).decode("utf-8", errors="ignore")
    vertices = 0
    faces = 0
    for line in text.splitlines():
        if line.startswith("v "):
            vertices += 1
        elif line.startswith("f "):
            faces += 1
    return {"vertices": vertices, "faces": faces}


def step_stats(path: Path) -> dict[str, Any]:
    text = read_sample(path, 2_000_000).decode("utf-8", errors="ignore").upper()
    return {
        "entities": text.count("\n#"),
        "advanced_faces": text.count("ADVANCED_FACE"),
        "closed_shells": text.count("CLOSED_SHELL"),
        "manifold_solids": text.count("MANIFOLD_SOLID_BREP"),
    }


def scad_stats(path: Path) -> dict[str, Any]:
    text = read_sample(path, 1_000_000).decode("utf-8", errors="ignore").lower()
    return {
        "modules": text.count("module "),
        "difference": text.count("difference("),
        "union": text.count("union("),
        "cylinder": text.count("cylinder("),
        "cube": text.count("cube("),
    }


def vsp3_stats(path: Path) -> dict[str, Any]:
    text = read_sample(path, 2_000_000).decode("utf-8", errors="ignore").lower()
    return {
        "geoms": text.count("<geom"),
        "wings": text.count("wing"),
        "fuselage": text.count("fuselage"),
        "prop": text.count("prop"),
        "pod": text.count("pod"),
    }


def collect_stats(path: Path) -> dict[str, Any]:
    ext = path.suffix.lower()
    try:
        if ext == ".stl":
            return stl_stats(path)
        if ext == ".obj":
            return obj_stats(path)
        if ext in {".step", ".stp"}:
            return step_stats(path)
        if ext == ".scad":
            return scad_stats(path)
        if ext == ".vsp3":
            return vsp3_stats(path)
    except Exception as exc:
        return {"parse_error": f"{type(exc).__name__}: {exc}"}
    return {}


def words_for(row: dict[str, Any]) -> set[str]:
    text = " ".join(str(row.get(k, "")) for k in ("filename", "github_path", "path", "source_url")).lower()
    words = set()
    text = re.sub(r"([a-z])([A-Z])", r"\1_\2", text)
    text = re.sub(r"([a-zA-Z]+)(\d+)", r"\1_\2", text)
    for raw in re.split(r"[^a-zA-Z0-9]+", text):
        raw = raw.strip(" ()[]{}")
        if raw:
            words.add(raw)
            alpha = re.sub(r"[^a-zA-Z]+", "", raw)
            if alpha and alpha != raw:
                words.add(alpha)
    if "mainbody" in words:
        words.add("main")
        words.add("body")
    if "upperarm" in words:
        words.add("upper")
        words.add("arm")
    if "forearm" in words:
        words.add("fore")
        words.add("arm")
    return words


def asset_scores(row: dict[str, Any], stats: dict[str, Any]) -> dict[str, Any]:
    path = REPO / row["path"]
    ext = path.suffix.lower()
    words = words_for(row)
    size = row.get("bytes") or path.stat().st_size
    source_id = str(row.get("source_id") or "")
    license_hint = str(row.get("license_hint") or "").lower()

    geom = 20
    if ext in {".step", ".stp"}:
        geom = 55 + min(35, stats.get("advanced_faces", 0) / 20)
    elif ext == ".vsp3":
        geom = 50 + min(40, stats.get("geoms", 0) * 8 + stats.get("wings", 0))
    elif ext == ".stl":
        geom = 35 + min(45, math.log10(max(1, stats.get("triangles", 0))) * 12)
    elif ext == ".obj":
        geom = 35 + min(45, math.log10(max(1, stats.get("faces", 0))) * 12)
    elif ext == ".scad":
        geom = 45 + min(35, stats.get("modules", 0) * 8 + stats.get("difference", 0) * 4)
    elif ext in {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".csv", ".md", ".txt", ".json"}:
        geom = 25 + min(35, len(words & (DOC_WORDS | ASSEMBLY_WORDS)) * 5)
    geom = clamp(geom)

    assembly_hits = len(words & ASSEMBLY_WORDS)
    assembly = clamp(20 + assembly_hits * 12)
    if "assembly" in words:
        assembly += 15
    if source_id.startswith("github:OpenVSP") and ext == ".vsp3":
        assembly += 10
    if ext in {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".csv", ".md"} and words & DOC_WORDS:
        assembly += 15
    assembly = clamp(assembly)

    print_value = 20
    if ext in PRINT_EXTS:
        print_value += 45
    if words & PRINT_WORDS:
        print_value += 20
    if ext == ".stl" and stats.get("triangles", 0) > 100:
        print_value += 15
    if words & {"dimension", "dimensions", "bom", "pcb", "prototype"}:
        print_value += 10
    print_value = clamp(print_value)

    manufacturing = 25
    if ext in MANUFACTURING_EXTS:
        manufacturing += 35
    if ext in {".step", ".stp"} and stats.get("manifold_solids", 0):
        manufacturing += 20
    if ext == ".scad" and stats.get("modules", 0):
        manufacturing += 15
    if ext in {".pdf", ".csv", ".md"} and words & {"bom", "dimension", "dimensions", "hardware", "pcb"}:
        manufacturing += 15
    manufacturing = clamp(manufacturing)

    license_score = 30
    if "mit" in license_hint or "apache" in license_hint:
        license_score = 75
    elif "gpl" in license_hint:
        license_score = 55
    elif "noassertion" in license_hint or "unknown" in license_hint:
        license_score = 30
    if row.get("license_status") == "needs_review":
        license_score = min(license_score, 60)

    completeness = 30
    if size > 50_000:
        completeness += 20
    if size > 250_000:
        completeness += 15
    if ext in {".step", ".stp", ".vsp3", ".scad", ".pdf", ".csv", ".md"}:
        completeness += 15
    completeness = clamp(completeness)

    design_value = clamp(geom * 0.28 + assembly * 0.22 + print_value * 0.16 + manufacturing * 0.2 + completeness * 0.14)
    training_readiness = clamp(design_value * 0.72 + license_score * 0.28)
    verdict = "promote_candidate"
    if training_readiness < 45:
        verdict = "quarantine_or_review"
    elif training_readiness < 65:
        verdict = "reference_only"
    elif row.get("license_status") == "needs_review":
        verdict = "license_review_then_promote"

    return {
        "geometry_fidelity": geom,
        "assembly_value": assembly,
        "print_reference_value": print_value,
        "manufacturing_reference_value": manufacturing,
        "completeness": completeness,
        "license_score": license_score,
        "design_value": design_value,
        "training_readiness": training_readiness,
        "verdict": verdict,
        "keywords": sorted((words & ASSEMBLY_WORDS) | (words & PRINT_WORDS) | (words & DOC_WORDS)),
    }


def summarize_seed(seed: str, assets: list[dict[str, Any]]) -> dict[str, Any]:
    exts = Counter(a["extension"] for a in assets)
    verdicts = Counter(a["scores"]["verdict"] for a in assets)
    avg = lambda key: round(sum(a["scores"][key] for a in assets) / max(1, len(assets)), 1)
    top_assets = sorted(assets, key=lambda a: a["scores"]["design_value"], reverse=True)[: min(12, len(assets))]
    top_avg = lambda key: round(sum(a["scores"][key] for a in top_assets) / max(1, len(top_assets)), 1)
    term_hits = Counter()
    for a in assets:
        term_hits.update(a["scores"]["keywords"])
    expect = SEED_EXPECTATIONS.get(seed, {})
    missing_terms = sorted(set(expect.get("assembly_terms", set())) - set(term_hits))
    issues = []
    if len(assets) < 5:
        issues.append("too few reference assets for robust seed grounding")
    if expect.get("step_min", 0) and sum(exts[e] for e in (".step", ".stp")) < expect["step_min"]:
        issues.append("needs more STEP/B-rep source geometry")
    if expect.get("vsp3_min", 0) and exts[".vsp3"] < expect["vsp3_min"]:
        issues.append("needs more OpenVSP aircraft geometry")
    if expect.get("print_min", 0) and sum(exts[e] for e in PRINT_EXTS) < expect["print_min"]:
        issues.append("needs more print-oriented STL/SCAD/3MF assets")
    if missing_terms:
        issues.append(f"missing expected assembly terms: {', '.join(missing_terms[:8])}")
    license_text = " ".join(str(a.get("license_hint", "")).lower() for a in assets)
    if "unknown" in license_text or "noassertion" in license_text:
        issues.append("license unresolved for at least one source; keep as reference-only until reviewed")

    status = "strong"
    if issues:
        status = "watch"
    if top_avg("training_readiness") < 50 and top_avg("design_value") < 55:
        status = "weak"
    return {
        "seed": seed,
        "asset_count": len(assets),
        "extensions": dict(exts),
        "sources": dict(Counter(a["source_id"] for a in assets)),
        "license_hints": dict(Counter(a["license_hint"] for a in assets)),
        "average_scores": {
            "design_value": avg("design_value"),
            "training_readiness": avg("training_readiness"),
            "top_design_value": top_avg("design_value"),
            "top_training_readiness": top_avg("training_readiness"),
            "geometry_fidelity": avg("geometry_fidelity"),
            "assembly_value": avg("assembly_value"),
            "print_reference_value": avg("print_reference_value"),
            "manufacturing_reference_value": avg("manufacturing_reference_value"),
        },
        "verdicts": dict(verdicts),
        "top_terms": dict(term_hits.most_common(16)),
        "status": status,
        "issues": issues,
        "recommendation": seed_recommendation(seed, status, issues, exts),
    }


def seed_recommendation(seed: str, status: str, issues: list[str], exts: Counter) -> str:
    if seed == "cubesat":
        return "Good structural/print base: STEP plus prepped STL. Add avionics/solar/EPS reference later for subsystem breadth."
    if seed == "haptic_glove":
        return "Strong mesh corpus for fingers/palm/links. Needs licensing pass and possibly assembly docs/URDF mapping before training promotion."
    if seed == "long_range_recon_wing":
        return "Useful OpenVSP geometry grammar for wings/props/aircraft. Needs specific UAV/flying-wing references and 2D/cutaway drawings."
    if seed == "tiltrotor":
        return "Useful aircraft/rotor VSP grammar but not truly tiltrotor-specific yet. Add nacelle tilt mechanism or VTOL repo references."
    if seed == "robot_arm":
        return "Strong link/joint STL family for industrial arms. License is unresolved; add URDF/joint metadata and one permissively licensed CAD source."
    if seed == "small_launch_vehicle":
        return "Good academic rocket/SCAD print reference. Keep non-operational study boundary; do not treat as flight/propulsion design."
    return "Review manually."


def main() -> int:
    rows = load_index()
    audited_assets = []
    for row in rows:
        path = REPO / row.get("path", "")
        if not path.exists() or path.suffix.lower() not in REFERENCE_EXTS:
            continue
        stats = collect_stats(path)
        scores = asset_scores(row, stats)
        audited_assets.append({
            "seed": row.get("seed"),
            "path": row.get("path"),
            "filename": row.get("filename"),
            "extension": row.get("extension"),
            "source_id": row.get("source_id"),
            "license_hint": row.get("license_hint"),
            "license_status": row.get("license_status"),
            "bytes": row.get("bytes"),
            "stats": stats,
            "scores": scores,
        })

    by_seed = defaultdict(list)
    for asset in audited_assets:
        by_seed[asset["seed"]].append(asset)
    seed_reports = {seed: summarize_seed(seed, assets) for seed, assets in sorted(by_seed.items())}
    report = {
        "schema": "blueprint_reference_quality_audit_v1",
        "generated_at": now_iso(),
        "source": str(INDEX.relative_to(REPO)),
        "asset_count": len(audited_assets),
        "seed_reports": seed_reports,
        "top_assets": sorted(
            audited_assets,
            key=lambda a: (a["scores"]["training_readiness"], a["scores"]["design_value"]),
            reverse=True,
        )[:40],
        "weak_assets": sorted(
            audited_assets,
            key=lambda a: (a["scores"]["training_readiness"], a["scores"]["design_value"]),
        )[:40],
        "global_findings": global_findings(seed_reports),
    }
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    print(REPORT_JSON)
    print(REPORT_MD)
    for seed, sr in seed_reports.items():
        print(f"[{seed}] {sr['status']} assets={sr['asset_count']} avg_design={sr['average_scores']['design_value']} "
              f"avg_ready={sr['average_scores']['training_readiness']}")
    return 0


def global_findings(seed_reports: dict[str, Any]) -> list[str]:
    findings = []
    weak = [seed for seed, sr in seed_reports.items() if sr["status"] == "weak"]
    watch = [seed for seed, sr in seed_reports.items() if sr["status"] == "watch"]
    if weak:
        findings.append(f"Weak seed reference sets: {', '.join(weak)}.")
    if watch:
        findings.append(f"Watch seed reference sets need targeted补강: {', '.join(watch)}.")
    findings.append("All assets remain license-gated until manual review changes training_use/license_status.")
    findings.append("Reference assets are useful for shape grammar, assembly vocabulary, and scoring; they are not yet wired into generation prompts.")
    findings.append("Next hardening step: generate reference_feature_cards.jsonl with seed-specific part labels, station cues, and forbidden-copy boundary.")
    return findings


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Reference Quality Audit",
        "",
        f"Generated: {report['generated_at']}",
        f"Audited CAD assets: {report['asset_count']}",
        "",
        "## Seed Summary",
        "",
        "| seed | status | assets | avg design | avg readiness | key recommendation |",
        "|---|---|---:|---:|---:|---|",
    ]
    for seed, sr in report["seed_reports"].items():
        lines.append(
            f"| {seed} | {sr['status']} | {sr['asset_count']} | "
            f"{sr['average_scores']['design_value']} | {sr['average_scores']['training_readiness']} | "
            f"{sr['recommendation']} |"
        )
    lines += ["", "## Per-Seed Detail", ""]
    for seed, sr in report["seed_reports"].items():
        lines += [
            f"### {seed}",
            "",
            f"- status: {sr['status']}",
            f"- assets: {sr['asset_count']}",
            f"- extensions: {sr['extensions']}",
            f"- verdicts: {sr['verdicts']}",
            f"- top terms: {sr['top_terms']}",
            f"- recommendation: {sr['recommendation']}",
        ]
        if sr["issues"]:
            lines += ["- issues:"] + [f"  - {item}" for item in sr["issues"]]
        lines.append("")
    lines += [
        "## Global Findings",
        "",
        *[f"- {item}" for item in report["global_findings"]],
        "",
        "## Strongest Assets",
        "",
        "| seed | readiness | design | path |",
        "|---|---:|---:|---|",
    ]
    for asset in report["top_assets"][:20]:
        lines.append(
            f"| {asset['seed']} | {asset['scores']['training_readiness']} | "
            f"{asset['scores']['design_value']} | {asset['path']} |"
        )
    lines += [
        "",
        "## Weakest Assets",
        "",
        "| seed | readiness | design | path | note |",
        "|---|---:|---:|---|---|",
    ]
    for asset in report["weak_assets"][:20]:
        note = asset["scores"]["verdict"]
        lines.append(
            f"| {asset['seed']} | {asset['scores']['training_readiness']} | "
            f"{asset['scores']['design_value']} | {asset['path']} | {note} |"
        )
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
