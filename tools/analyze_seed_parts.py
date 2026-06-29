"""List all seed BOM parts and flag likely duplicate/overlap candidates."""
from __future__ import annotations

import json
import re
from itertools import combinations
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VEHICLES = REPO / "20_dataset" / "seed_vehicles.json"
OUT = REPO / "docs" / "SEED_PART_LIST_AND_OVERLAP_AUDIT_2026-06-27.md"

SEEDS = [
    "cubesat",
    "haptic_glove",
    "long_range_recon_wing",
    "tiltrotor",
    "robot_arm",
    "small_launch_vehicle",
    "inline_6_engine_gasoline",
    "inline_6_engine_diesel",
    "centrifugal_pump",
    "hydraulic_manifold",
    "battery_pack_module",
    "liquid_cold_plate",
    "cnc_axis_carriage",
    "gearbox_reducer",
    "underwater_sealed_sensor_housing",
    "liquid_rocket_engine_academic",
]

STOP = {
    "the", "and", "with", "for", "set", "module", "assembly",
    "study", "concept", "service", "access", "pattern", "interface", "x",
    "system", "primary", "section", "plate", "cover", "bay",
}

DOMAIN = {
    "cubesat": "space/electronics/frame/harness/deployables",
    "haptic_glove": "wearable robotics/linkage/cable/ergonomics",
    "long_range_recon_wing": "aero structure/wing stations/payload bay",
    "tiltrotor": "aero/propulsion mount/tilt mechanism",
    "robot_arm": "serial mechanism/joints/links/cable spine",
    "small_launch_vehicle": "academic aerospace shell/staged study boundary",
    "inline_6_engine_gasoline": "IC engine/gasoline cranktrain/valvetrain/manifolds",
    "inline_6_engine_diesel": "IC engine/diesel reinforced block/common rail/turbo",
    "centrifugal_pump": "rotating fluid machinery/volute/impeller/seal",
    "hydraulic_manifold": "fluid power block/ports/valves/galleries",
    "battery_pack_module": "power electronics/cells/busbars/BMS/enclosure",
    "liquid_cold_plate": "thermal management/channels/manifold/gasket",
    "cnc_axis_carriage": "precision motion/rails/ballscrew/sensors/lube",
    "gearbox_reducer": "rotating power transmission/gears/shafts/bearings",
    "underwater_sealed_sensor_housing": "marine sealed enclosure/O-rings/cable gland",
    "liquid_rocket_engine_academic": "academic liquid rocket propulsion/chamber/cooling/feed/instrumentation boundary",
}


def tokens(text: str) -> set[str]:
    out = set()
    for raw in re.split(r"[^a-z0-9]+", text.lower()):
        if len(raw) >= 3 and raw not in STOP:
            out.add(raw)
    return out


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def classify_overlap(a: dict, b: dict, score: float) -> str:
    same_seed = a["seed"] == b["seed"]
    shared = a["tokens"] & b["tokens"]
    if same_seed and score >= 0.4:
        return "review_same_seed_possible_duplicate"
    if {"battery", "power"} & shared:
        return "intentional_cross_domain_power_overlap"
    if {"harness", "cable", "connector", "wiring"} & shared:
        return "intentional_cross_domain_harness_overlap"
    if {"engine", "nozzle", "turbopump", "chamber"} & shared:
        return "intentional_study_boundary_overlap"
    if {"mount", "bracket", "flange", "bearing", "seal", "sensor"} & shared:
        return "generic_engineering_vocabulary_overlap"
    return "possible_functional_overlap"


def collect_parts() -> list[dict]:
    vehicles = json.loads(VEHICLES.read_text(encoding="utf-8"))
    parts = []
    for seed in SEEDS:
        vehicle = vehicles[seed]
        for part in vehicle.get("parts", []):
            text = f"{part.get('label', '')} {part.get('spec', '')}"
            parts.append({
                "seed": seed,
                "part_id": part.get("id"),
                "label": part.get("label"),
                "spec": part.get("spec"),
                "tokens": tokens(text),
            })
    return parts


def overlap_rows(parts: list[dict]) -> list[dict]:
    rows = []
    for a, b in combinations(parts, 2):
        score = jaccard(a["tokens"], b["tokens"])
        shared = sorted(a["tokens"] & b["tokens"])
        if score < 0.18 and len(shared) < 4:
            continue
        rows.append({
            "score": round(score, 3),
            "shared": shared[:12],
            "a": a,
            "b": b,
            "classification": classify_overlap(a, b, score),
        })
    return sorted(rows, key=lambda r: (-r["score"], r["a"]["seed"], r["b"]["seed"]))


def render() -> str:
    parts = collect_parts()
    overlaps = overlap_rows(parts)
    lines = [
        "# Seed Part List and Overlap Audit",
        "",
        f"- total seeds: {len(SEEDS)}",
        f"- total BOM parts: {len(parts)}",
        f"- overlap candidates: {len(overlaps)}",
        "",
        "## Seed Part Counts",
        "",
        "| Seed | Domain | Parts |",
        "| --- | --- | ---: |",
    ]
    for seed in SEEDS:
        count = sum(1 for p in parts if p["seed"] == seed)
        lines.append(f"| `{seed}` | {DOMAIN[seed]} | {count} |")
    lines += ["", "## Full BOM By Seed", ""]
    for seed in SEEDS:
        lines += [f"### {seed}", "", f"- domain: {DOMAIN[seed]}", ""]
        for p in [p for p in parts if p["seed"] == seed]:
            lines.append(f"- `{p['part_id']}` {p['label']}: {p['spec']}")
        lines.append("")
    lines += [
        "## Overlap Audit",
        "",
        "These are token-overlap candidates, not automatic duplicates. Many are intentional reusable engineering vocabulary such as cable, bearing, sensor, mount, gasket, or service cover.",
        "",
        "| Score | Classification | Part A | Part B | Shared Terms |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for row in overlaps[:80]:
        a, b = row["a"], row["b"]
        lines.append(
            f"| {row['score']:.3f} | {row['classification']} | "
            f"`{a['seed']}/{a['part_id']}` {a['label']} | "
            f"`{b['seed']}/{b['part_id']}` {b['label']} | "
            f"{', '.join(row['shared'])} |"
        )
    lines += [
        "",
        "## Readout",
        "",
        "- No exact duplicate BOM part IDs exist across seeds because IDs are seed-local.",
        "- Repeated themes like battery, harness, cable, bearing, sensor, mount, seal, and service cover are expected; they are shared engineering primitives.",
        "- Real duplication to watch is same seed/same function duplication, or cross-seed items with identical role and no domain-specific boundary.",
        "- The rocket/launch entries intentionally overlap with `liquid_rocket_engine_academic`, but the latter is held to a non-buildable academic propulsion-study boundary.",
    ]
    return "\n".join(lines)


def main() -> int:
    OUT.write_text(render(), encoding="utf-8")
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
