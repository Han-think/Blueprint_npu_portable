"""Build a consolidated inventory of Blueprint engineering seeds.

The output is a human-facing map of every seed, its BOM, subsystem grammar,
assembly-position hints, reference status, and crawl priorities.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
VEHICLES_FILE = REPO / "20_dataset" / "seed_vehicles.json"
PACKS = REPO / "20_dataset" / "packs"
CARDS = REPO / "20_dataset" / "reference_assets" / "reference_feature_cards.jsonl"
TARGETS = REPO / "20_dataset" / "reference_assets" / "seed_reference_targets.json"
OUT = REPO / "docs" / "SEED_INVENTORY_AND_ASSEMBLY_MAP_2026-06-27.md"
OUT_JSON = REPO / "docs" / "seed_inventory_and_assembly_map_2026-06-27.json"

SEED_GROUPS = {
    "Original Evolution Seeds": [
        "cubesat",
        "haptic_glove",
        "long_range_recon_wing",
        "tiltrotor",
        "robot_arm",
        "small_launch_vehicle",
    ],
    "Engineering Expansion Seeds": [
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
    ],
}

ASSEMBLY_AXIS_HINTS = {
    "cubesat": "Use Z as 3U stack axis; PC/104 boards and harness spine run along the body, deployables attach to side faces.",
    "haptic_glove": "Use wrist-to-fingertip as the station axis; dorsal module at wrist/back-of-hand, finger cartridges repeat per finger.",
    "long_range_recon_wing": "Use X as fuselage/chord and Y as span; center pod at root, spars/ribs span outward, payload bays near centerline.",
    "tiltrotor": "Use X fuselage, Y wing span, Z vertical; nacelles sit on wing stations with tilt-axis across nacelle/wing interface.",
    "robot_arm": "Use serial joint chain from base J1 to tool flange J6; each link owns its joint datum and cable pass-through.",
    "small_launch_vehicle": "Use Z as stage stack axis; shells, rings, fairings, and academic study modules stack vertically with cutaway windows.",
    "inline_6_engine_gasoline": "Use X along crankshaft/cylinder row, Z vertical bore axis, Y intake/exhaust sides; service covers on top/front/bottom.",
    "inline_6_engine_diesel": "Use X along crankshaft/cylinder row, Z bore/head axis; turbo/exhaust on one side, intake/common rail service on the other.",
    "centrifugal_pump": "Use X shaft axis, radial impeller/volute around shaft, suction at impeller eye, discharge tangent to volute.",
    "hydraulic_manifold": "Use block datum faces; ports occupy named faces, cross-drilled galleries run between P/T/A/B and cartridge cavities.",
    "battery_pack_module": "Use module length/width as cell array plane and Z as lid/service direction; cooling plate and busbars are separated layers.",
    "liquid_cold_plate": "Use plate XY as heat-source plane and Z as stacked cover/gasket direction; inlet/outlet manifolds sit on one edge.",
    "cnc_axis_carriage": "Use X as travel axis; rails parallel X, ball screw on centerline, carriage plate rides above bearing blocks.",
    "gearbox_reducer": "Use parallel shaft axes through housing; gear mesh centerlines define internal layout, service cover on top/side.",
    "underwater_sealed_sensor_housing": "Use cylinder axis through front window and rear cap; cable gland exits rear/side, cradle supports shell below.",
    "liquid_rocket_engine_academic": "Use Z as chamber/nozzle study axis; feed-system modules sit radially, turbomachinery/DAQ modules sit off-axis, thrust-frame datum is aft.",
}

REFERENCE_CRAWL_PRIORITIES = {
    "cubesat": ["3U frame STEP with rails/standoffs", "solar deploy panel hinge CAD/drawing", "EPS/battery/PC104 stack layout", "harness spine/service cover reference"],
    "haptic_glove": ["URDF/joint-order docs", "finger linkage assembly CAD", "tendon/cable routing diagrams", "wearable fit/soft-contact reference"],
    "long_range_recon_wing": ["3-view/cutaway flying wing", "center pod payload bay CAD", "spar/rib/battery bay drawings", "servo/elevon linkage reference"],
    "tiltrotor": ["tilt nacelle axis CAD/cutaway", "servo linkage and bearing layout", "slack-loop harness around tilt axis", "wing/nacelle load-path drawing"],
    "robot_arm": ["permissive URDF/visual mesh", "joint reducer/bearing cutaway", "cable spine routing reference", "tool flange/ISO pattern drawing"],
    "small_launch_vehicle": ["academic non-operational stage shell cutaway", "avionics/recovery bay study reference", "chamber/tank reference-section CAD", "academic boundary labels"],
    "inline_6_engine_gasoline": ["engine block/head cutaway CAD", "cranktrain exploded view", "intake/exhaust manifold CAD", "oil/coolant gallery diagram"],
    "inline_6_engine_diesel": ["reinforced diesel block/head cutaway", "common rail/injector well layout", "turbo/exhaust routing CAD", "oil cooler/filter module drawing"],
    "centrifugal_pump": ["volute casing STEP/cutaway", "impeller CAD", "mechanical seal cartridge drawing", "bearing frame/baseplate assembly"],
    "hydraulic_manifold": ["manifold port map drawing", "cross-drilled gallery CAD", "cartridge valve cavity reference", "sensor/test port layout"],
    "battery_pack_module": ["cell tray CAD", "busbar/BMS cover reference", "cooling plate interface", "vent/disconnect/enclosure drawing"],
    "liquid_cold_plate": ["serpentine channel CAD", "manifold cap/gasket drawing", "thermal pad/mount pattern", "leak-test/drain port reference"],
    "cnc_axis_carriage": ["linear rail/carriage CAD", "ball screw support assembly", "servo mount/coupling guard", "way cover/lube manifold reference"],
    "gearbox_reducer": ["split housing cutaway", "gear/shaft/bearing layout", "oil seal/plug/breather details", "mounting feet/torque arm drawing"],
    "underwater_sealed_sensor_housing": ["pressure shell/end cap CAD", "O-ring/cable gland drawing", "internal electronics tray", "cradle/anode/leak-test reference"],
    "liquid_rocket_engine_academic": ["NASA/NTRS academic liquid propulsion reports", "safe cutaway diagrams for chamber/nozzle/cooling/feed topology", "instrumentation/control architecture references", "turbomachinery educational diagrams without performance sizing"],
}


def load_cards() -> dict[str, dict[str, Any]]:
    cards: dict[str, dict[str, Any]] = {}
    if not CARDS.exists():
        return cards
    for line in CARDS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        card = json.loads(line)
        cards[card["seed"]] = card
    return cards


def load_targets() -> dict[str, list[dict[str, Any]]]:
    if not TARGETS.exists():
        return {}
    return (json.loads(TARGETS.read_text(encoding="utf-8")).get("targets") or {})


def load_skeleton(seed: str) -> dict[str, Any]:
    path = PACKS / seed / "skeleton.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def short(text: str, limit: int = 135) -> str:
    text = " ".join(str(text or "").split())
    return text if len(text) <= limit else text[: limit - 3].rstrip() + "..."


def render_seed(seed: str, vehicle: dict[str, Any], card: dict[str, Any], targets: list[dict[str, Any]]) -> list[str]:
    skeleton = load_skeleton(seed)
    subs = skeleton.get("required_subsystems") or []
    parts = vehicle.get("parts") or []
    lines = [
        f"## {seed}",
        "",
        f"- label: {vehicle.get('label', '')}",
        f"- domain: {vehicle.get('desc', '')}",
        f"- material/process: {vehicle.get('material', '')} / {vehicle.get('process', '')}",
        f"- envelope/mass: {vehicle.get('envelope', '')} / {vehicle.get('mass', '')}",
        f"- reference status: {card.get('status', 'missing_card')} · assets {card.get('asset_count', 0)}",
        f"- assembly position hint: {ASSEMBLY_AXIS_HINTS.get(seed, 'Define primary datum, station axis, service side, and adjacent interfaces.')}",
        "",
        "### BOM Parts",
    ]
    for p in parts:
        lines.append(f"- `{p.get('id')}` {p.get('label')}: {short(p.get('spec'))}")
    lines += ["", "### Subsystem Grammar"]
    if subs:
        for sub in subs:
            ev = ", ".join((sub.get("evidence_features") or [])[:8])
            lines.append(f"- `{sub.get('id')}` ({sub.get('discipline')}): {sub.get('function')} | evidence: {ev}")
    else:
        lines.append("- missing skeleton pack")
    lines += ["", "### Reference Grammar"]
    for item in (card.get("design_grammar_to_learn") or [])[:5]:
        lines.append(f"- learn: {item}")
    for item in (card.get("missing_reference_needs") or [])[:5]:
        lines.append(f"- need: {item}")
    lines += ["", "### Crawl / CAD Priorities"]
    for item in REFERENCE_CRAWL_PRIORITIES.get(seed, []):
        lines.append(f"- {item}")
    if targets:
        lines.append("")
        lines.append("### Current Source Targets")
        for t in targets:
            label = t.get("label") or t.get("url") or "target"
            why = short(t.get("why", ""), 100)
            lines.append(f"- {label}: {why}")
    lines.append("")
    return lines


def token_set(text: str) -> set[str]:
    out = set()
    for raw in str(text or "").lower().replace("_", " ").replace("/", " ").split():
        token = "".join(ch for ch in raw if ch.isalnum())
        if len(token) >= 3:
            out.add(token)
    return out


def map_part_to_subsystems(part: dict[str, Any], subs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    part_tokens = token_set(f"{part.get('label', '')} {part.get('spec', '')}")
    scored = []
    for sub in subs:
        sub_tokens = token_set(
            f"{sub.get('id', '')} {sub.get('discipline', '')} {sub.get('function', '')} "
            f"{' '.join(sub.get('evidence_features') or [])}"
        )
        score = len(part_tokens & sub_tokens)
        if score:
            scored.append({"subsystem": sub.get("id"), "score": score})
    return sorted(scored, key=lambda item: (-item["score"], item["subsystem"]))[:3]


def inventory_json() -> dict[str, Any]:
    vehicles = json.loads(VEHICLES_FILE.read_text(encoding="utf-8"))
    cards = load_cards()
    targets = load_targets()
    seeds = [seed for group in SEED_GROUPS.values() for seed in group]
    out = {
        "schema": "blueprint_seed_inventory_and_assembly_map_v1",
        "seeds": [],
    }
    for seed in seeds:
        vehicle = vehicles.get(seed, {})
        skeleton = load_skeleton(seed)
        subs = skeleton.get("required_subsystems") or []
        parts = vehicle.get("parts") or []
        part_map = [
            {
                "part_id": p.get("id"),
                "label": p.get("label"),
                "subsystem_candidates": map_part_to_subsystems(p, subs),
            }
            for p in parts
        ]
        out["seeds"].append({
            "seed": seed,
            "label": vehicle.get("label"),
            "parts_count": len(parts),
            "subsystems_count": len(subs),
            "reference_status": cards.get(seed, {}).get("status"),
            "asset_count": cards.get(seed, {}).get("asset_count", 0),
            "assembly_position_hint": ASSEMBLY_AXIS_HINTS.get(seed),
            "crawl_priorities": REFERENCE_CRAWL_PRIORITIES.get(seed, []),
            "source_targets": targets.get(seed, []),
            "bom_to_subsystem_candidates": part_map,
        })
    return out


def render() -> str:
    vehicles = json.loads(VEHICLES_FILE.read_text(encoding="utf-8"))
    cards = load_cards()
    targets = load_targets()
    lines = [
        "# Seed Inventory and Assembly Map",
        "",
        "This document lists the current seed set, what is inside each seed, how its assembly should be positioned, and what reference CAD/crawl work remains.",
        "",
        "## Summary",
        "",
        "| Group | Seed | Parts | Subsystems | Reference Status | Assets |",
        "| --- | --- | ---: | ---: | --- | ---: |",
    ]
    for group, seeds in SEED_GROUPS.items():
        for seed in seeds:
            vehicle = vehicles.get(seed, {})
            card = cards.get(seed, {})
            subs = load_skeleton(seed).get("required_subsystems") or []
            lines.append(
                f"| {group} | `{seed}` | {len(vehicle.get('parts') or [])} | {len(subs)} | "
                f"{card.get('status', 'missing_card')} | {card.get('asset_count', 0)} |"
            )
    lines += [
        "",
        "## Assembly Map Rules",
        "",
        "- Every seed should define a primary datum/axis, a service side, and at least three adjacent interfaces.",
        "- Every BOM part should map to one subsystem grammar or declare why it crosses multiple subsystems.",
        "- Every subsystem should expose evidence features in `part_tree`, `geometry_ops`, and assembly/disassembly notes.",
        "- Reference CAD is used as grammar and validation vocabulary only until license review promotes it.",
        "- Safety-boundary seeds stay academic, non-operational, and non-buildable unless real engineering analysis and legal review exist.",
        "",
    ]
    for group, seeds in SEED_GROUPS.items():
        lines += [f"# {group}", ""]
        for seed in seeds:
            if seed not in vehicles:
                lines += [f"## {seed}", "", "- missing from seed_vehicles.json", ""]
                continue
            lines += render_seed(seed, vehicles[seed], cards.get(seed, {}), targets.get(seed, []))
    return "\n".join(lines)


def main() -> int:
    OUT.write_text(render(), encoding="utf-8")
    OUT_JSON.write_text(json.dumps(inventory_json(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(OUT)
    print(OUT_JSON)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
