"""Build prompt-safe reference feature cards from audited assets.

Cards summarize design grammar from reference CAD without telling the model to
copy a specific product. They are the bridge from raw downloaded files to
generation context.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "20_dataset" / "reference_assets"
AUDIT = ROOT / "_reference_quality_audit.json"
OUT = ROOT / "reference_feature_cards.jsonl"
OUT_MD = ROOT / "reference_feature_cards.md"

SEED_CARD_RULES = {
    "cubesat": {
        "learn": [
            "3U/1U frame segmentation into top/mid/bottom structural shells",
            "print-prepped rail, corner, and skeletonized frame cues",
            "STEP-to-STL traceability for printable structure variants",
        ],
        "must_add": [
            "EPS, CDH, solar panel, thermal strap, and harness spine references are still needed",
            "assembly card should force board stack and service access, not just frame shell",
        ],
    },
    "haptic_glove": {
        "learn": [
            "finger linkage families: base, bend segments, split links, thumb MCP and distal parts",
            "palm/base plate and modular hand-link decomposition",
            "printable mesh density for wearable mechanism study references",
        ],
        "must_add": [
            "URDF/joint ordering or assembly docs should be mapped before training promotion",
            "separate actual glove mechanism parts from generic robotic hand meshes",
        ],
    },
    "long_range_recon_wing": {
        "learn": [
            "OpenVSP wing/prop/aircraft parametric geometry grammar",
            "planform, wing station, rotor/prop, and fuselage reference vocabulary",
            "aircraft geometry can guide station-based CAD-like generation",
        ],
        "must_add": [
            "specific UAV/flying-wing center pod, payload bay, battery bay, and cutaway references",
            "2D top/side/front drawings with rib/spar/bay labels",
        ],
    },
    "tiltrotor": {
        "learn": [
            "OpenVSP prop/rotor/wing geometry grammar",
            "wing plus propulsion axis decomposition",
            "parametric aircraft references for silhouette and station placement",
        ],
        "must_add": [
            "tilting nacelle, tilt-axis bearing, servo linkage, and slack-loop harness reference",
            "VTOL-specific assembly/cutaway drawing source",
        ],
    },
    "robot_arm": {
        "learn": [
            "serial arm link naming and proportions: base, shoulder, upperarm, forearm, wrist",
            "collision mesh families for UR-style industrial arms",
            "joint-link segmentation useful for assembly grammar",
        ],
        "must_add": [
            "license must be resolved before training use",
            "visual meshes/URDF/joint metadata are needed; collision STLs alone are incomplete",
            "one permissively licensed STEP/URDF source should be added",
        ],
    },
    "small_launch_vehicle": {
        "learn": [
            "OpenSCAD parametric rocket study components: assembly, fins, rings, main body",
            "printable STL/SCAD relationship for academic non-operational rocket cutaway references",
            "module separation between shell, nose/fins/rings/controller cap",
        ],
        "must_add": [
            "keep explicit academic non-operational boundary",
            "avoid propulsion/performance instructions; use only shape, subsystem, and inspection grammar",
            "add cutaway/avionics/recovery bay references if available",
        ],
    },
    "inline_6_engine_gasoline": {
        "learn": [
            "inline-six segmentation: block, crankcase, head, cranktrain, manifolds, timing cover, oil pan",
            "gasoline-specific grammar: spark plug wells, fuel rail, injector pockets, throttle/intake plenum",
            "serviceable cutaway features: gasket faces, coolant jacket cues, oil galleries, accessory brackets",
        ],
        "must_add": [
            "permissive engine cutaway/CAD references for block/head/cranktrain are needed",
            "keep output at conceptual/educational assembly grammar; no certified running-engine claim",
        ],
    },
    "inline_6_engine_diesel": {
        "learn": [
            "diesel inline-six reinforcement grammar: thick deck, bearing ladder, cross-bolt bosses, heavy cranktrain",
            "diesel-specific layout: injector wells, common rail, return path, turbo/exhaust heat shield, oil cooler",
            "service access for timing gear housing, filters, injectors, lifting/mounting datums",
        ],
        "must_add": [
            "licensed diesel engine cutaway and common-rail layout references should be reviewed",
            "do not promote performance, emissions, injection calibration, or certified engine claims",
        ],
    },
    "centrifugal_pump": {
        "learn": [
            "volute/impeller/shaft/bearing/seal/flange decomposition for rotating fluid machinery",
            "pressure-boundary grammar: inlet eye, outlet flange, gasket faces, drain/vent plugs, inspection bosses",
            "back-pull-out service grammar: seal cartridge, bearing housing, coupling guard, baseplate alignment",
        ],
        "must_add": [
            "pump cross-section/CAD references with clear volute and seal cartridge structure are needed",
            "scorecard should penalize pumps with no flow path or serviceable seal/bearing access",
        ],
    },
    "hydraulic_manifold": {
        "learn": [
            "CNC manifold block grammar: P/T/A/B ports, cross-drilled galleries, plug bosses, datum faces",
            "cartridge valve cavities with O-ring lands, wrench clearance, flow arrows, and labels",
            "instrumentation and test access: pressure sensor boss, test port, protective cover, label plate",
        ],
        "must_add": [
            "licensed manifold drawings/CAD with visible port maps and valve cavities are needed",
            "avoid implying rated pressure certification; use conceptual routing and inspection vocabulary",
        ],
    },
    "battery_pack_module": {
        "learn": [
            "battery module decomposition: cell carrier, busbar cover, BMS bay, cooling plate, enclosure, disconnect",
            "thermal/electrical separation grammar: thermal pad zones, sense-wire channels, EMI shield, terminal guards",
            "safety/service grammar: gasketed lid, vent path, service disconnect, warning labels, no-live-energy boundary",
        ],
        "must_add": [
            "permissive battery module/cold-plate/enclosure references are needed before training promotion",
            "do not generate live-energy assembly instructions or claim pack safety certification",
        ],
    },
    "liquid_cold_plate": {
        "learn": [
            "cold plate channel grammar: serpentine path, fin islands, inlet/outlet manifold, thermal pad zones",
            "seal/leak grammar: gasket groove, compression stops, leak witness channel, drain/bleed/test ports",
            "power-device mounting grammar: flatness datum, isolation washer pockets, torque marks, service labels",
        ],
        "must_add": [
            "channel/cap/gasket CAD or drawings should be collected for geometry fidelity",
            "avoid rated pressure/thermal-performance claims until external analysis exists",
        ],
    },
    "cnc_axis_carriage": {
        "learn": [
            "precision axis decomposition: carriage plate, rails, bearing blocks, ball screw, motor mount, sensors",
            "datum/tolerance grammar: dowel holes, rail reference edge, preload notes, adjustment slots",
            "protection/service grammar: way covers, wipers, lubrication manifold, cable channels, grease ports",
        ],
        "must_add": [
            "licensed linear axis/ball screw/rail assembly CAD references are needed",
            "scorecard should penalize axis designs without rail datums, screw support, or sensor/lube access",
        ],
    },
    "gearbox_reducer": {
        "learn": [
            "gearbox decomposition: split housing, input/intermediate/output shafts, gear mesh, bearings, seals",
            "lubrication/service grammar: fill/drain/level plugs, breather, sight glass, inspection cover",
            "precision support grammar: bearing bores, shims, retainer plates, dowel pads, mesh centerline",
        ],
        "must_add": [
            "permissive reducer cutaway/CAD references with shaft/bearing/gear layout are needed",
            "do not claim torque rating or gear life without real sizing analysis",
        ],
    },
    "underwater_sealed_sensor_housing": {
        "learn": [
            "sealed marine enclosure grammar: pressure shell, end caps, O-ring grooves, cable gland, service cap",
            "payload integration grammar: sensor window, internal tray, desiccant pocket, ground lug, slide rails",
            "marine service grammar: leak test port, clamp cradle, drain path, anode pad, serial/pressure labels",
        ],
        "must_add": [
            "licensed underwater enclosure/cable gland/O-ring cap references are needed",
            "avoid depth rating or pressure certification claims without analysis",
        ],
    },
    "liquid_rocket_engine_academic": {
        "learn": [
            "academic liquid-engine subsystem grammar: chamber heat transfer, nozzle expansion study, injector taxonomy, regenerative cooling",
            "feed-system and turbomachinery architecture vocabulary without buildable sizing or operating procedures",
            "instrumentation, DAQ, interlock, thrust-frame load path, and non-buildable boundary annotation",
        ],
        "must_add": [
            "collect safe academic NASA/NTRS or textbook-like references for subsystem decomposition and terminology",
            "avoid buildable engine dimensions, propellant handling, ignition/start procedures, thrust/chamber-pressure sizing, injector hole sizing, turbopump performance, test-stand operating steps, or flight-use instructions",
            "use references as conceptual architecture and validation vocabulary only until legal/safety review",
        ],
    },
}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_audit() -> dict[str, Any]:
    return json.loads(AUDIT.read_text(encoding="utf-8"))


def selected_assets(audit: dict[str, Any], seed: str) -> list[dict[str, Any]]:
    assets = [
        a for a in audit.get("top_assets", []) + audit.get("weak_assets", [])
        if a.get("seed") == seed
    ]
    seen = set()
    out = []
    for asset in assets:
        path = asset.get("path")
        if path in seen:
            continue
        seen.add(path)
        if asset.get("scores", {}).get("design_value", 0) >= 55:
            out.append(asset)
        if len(out) >= 8:
            break
    return out


def build_cards(audit: dict[str, Any]) -> list[dict[str, Any]]:
    cards = []
    seed_reports = audit.get("seed_reports") or {}
    seeds = sorted(set(seed_reports) | set(SEED_CARD_RULES))
    for seed in seeds:
        sr = seed_reports.get(seed, {})
        rules = SEED_CARD_RULES.get(seed, {"learn": [], "must_add": []})
        assets = selected_assets(audit, seed)
        cards.append({
            "schema": "blueprint_reference_feature_card_v1",
            "created_at": now_iso(),
            "seed": seed,
            "status": sr.get("status") or "needs_reference_crawl",
            "asset_count": sr.get("asset_count") or 0,
            "average_scores": sr.get("average_scores") or {},
            "reference_assets": [
                {
                    "path": a.get("path"),
                    "design_value": a.get("scores", {}).get("design_value"),
                    "training_readiness": a.get("scores", {}).get("training_readiness"),
                    "keywords": a.get("scores", {}).get("keywords", []),
                    "verdict": a.get("scores", {}).get("verdict"),
                }
                for a in assets
            ],
            "design_grammar_to_learn": rules["learn"],
            "missing_reference_needs": rules["must_add"],
            "generation_contract": {
                "use_as": "shape/assembly grammar and validation vocabulary",
                "do_not_use_as": "direct product copy, manufacturing certification, or safety guarantee",
                "required_output_effect": [
                    "part_tree children should reflect real substructure names from the reference family",
                    "geometry_ops should distribute coordinates across stations, bays, joints, frames, or links",
                    "assembly sequence should mention access, datum, fastener, service, or print orientation where relevant",
                    "scorecard should penalize generic box-like geometry that ignores this card",
                ],
            },
            "license_gate": {
                "current_state": "blocked_until_license_review",
                "allowed_now": "human review and prompt inspiration with source citation",
                "blocked_now": "training promotion or derivative claim until license_status is reviewed",
            },
            "anti_copy_boundary": [
                "Do not reproduce a named product or exact vehicle geometry.",
                "Extract reusable engineering grammar: stations, modules, interfaces, and service access.",
                "Keep academic non-operational boundary for aerospace/launch references.",
            ],
        })
    return cards


def render_md(cards: list[dict[str, Any]]) -> str:
    lines = [
        "# Reference Feature Cards",
        "",
        "Prompt-safe summaries generated from `_reference_quality_audit.json`.",
        "",
    ]
    for card in cards:
        lines += [
            f"## {card['seed']}",
            "",
            f"- status: {card['status']}",
            f"- assets: {card['asset_count']}",
            f"- license gate: {card['license_gate']['current_state']}",
            "- design grammar:",
            *[f"  - {item}" for item in card["design_grammar_to_learn"]],
            "- missing reference needs:",
            *[f"  - {item}" for item in card["missing_reference_needs"]],
            "- selected assets:",
            *[f"  - {a['path']} ({a['verdict']}, design {a['design_value']})" for a in card["reference_assets"]],
            "",
        ]
    return "\n".join(lines)


def main() -> int:
    audit = load_audit()
    cards = build_cards(audit)
    with OUT.open("w", encoding="utf-8", newline="\n") as f:
        for card in cards:
            f.write(json.dumps(card, ensure_ascii=False) + "\n")
    OUT_MD.write_text(render_md(cards), encoding="utf-8")
    print(OUT)
    print(OUT_MD)
    print(f"[cards] {len(cards)} seeds")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
