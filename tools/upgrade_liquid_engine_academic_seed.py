"""Upgrade rocket engine seed from display dummy to academic liquid-engine seed.

The seed remains non-buildable and non-operational, but it now represents an
academic liquid rocket propulsion system architecture instead of a display
dummy. It is intended for conceptual decomposition, assembly grammar,
instrumentation vocabulary, and safe historical/educational study.
"""
from __future__ import annotations

import json
import shutil
from copy import deepcopy
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
VEHICLES = REPO / "20_dataset" / "seed_vehicles.json"
PACKS = REPO / "20_dataset" / "packs"
TARGETS = REPO / "20_dataset" / "reference_assets" / "seed_reference_targets.json"

OLD = "engine_display_dummy"
NEW = "liquid_rocket_engine_academic"

COMMON_CRITERIA = [
    {
        "id": "geometry_grounding",
        "criteria": [
            {
                "criterion": "p0_feature_mapping",
                "good": "Every P0 evidence feature appears as a named part_tree child or a geometry_ops target.",
                "bad": "Subsystem claims features in prose but leaves no geometry target or child node.",
            },
            {
                "criterion": "coordinate_distribution",
                "good": "Coordinates span chamber/nozzle stations, feed-interface faces, sensor bosses, service covers, or datum pads.",
                "bad": "All academic features are stacked at the origin or represented as one shell.",
            },
            {
                "criterion": "academic_non_operational_boundary",
                "good": "Uses conceptual labels, cutaway/study sections, blocked manufacturing details, and no build/test/performance recipe.",
                "bad": "Provides operational dimensions, propellant procedures, ignition instructions, performance sizing, or test steps.",
            },
        ],
    },
    {
        "id": "assembly_integration",
        "criteria": [
            {
                "criterion": "interface_named",
                "good": "Each study module has named datums, service covers, instrumentation ports, and adjacent conceptual interfaces.",
                "bad": "Subsystems float independently without interfaces or assembly position.",
            },
            {
                "criterion": "phenomena_map_visible",
                "good": "Heat transfer, flow path, turbomachinery energy path, controls/sensing, and structural support are visible as separate study zones.",
                "bad": "Claims liquid-engine understanding while showing only a generic chamber/nozzle shell.",
            },
        ],
    },
]

BOUNDARY = (
    "Academic liquid rocket propulsion study only. Do not generate buildable engine dimensions, "
    "propellant handling or ignition procedures, chamber pressure/thrust sizing, injector hole sizing, "
    "turbopump performance, test-stand operating steps, or flight-use instructions."
)


def part(pid: int, label: str, preset: list[str], spec: str) -> dict[str, Any]:
    return {"id": f"p{pid}", "label": label, "preset": preset, "spec": spec}


VEHICLE = {
    "id": NEW,
    "label": "Academic Liquid Rocket Engine System",
    "wikiTitle": "Liquid-propellant rocket",
    "desc": (
        "Academic liquid rocket propulsion system seed for conceptual chamber/nozzle, injector taxonomy, "
        "regenerative cooling, feed-system architecture, turbomachinery, instrumentation, controls, and mount/load-path grammar; "
        "non-buildable and non-operational"
    ),
    "material": "academic multi-material reference: copper alloy liner + steel jacket + Al/steel structures",
    "process": "concept CAD + cutaway study model",
    "mass": "academic reference only",
    "envelope": "conceptual study envelope",
    "parts": [
        part(1, "Combustion Chamber Heat-Transfer Study Section", ["space", "propulsion", "combustion_chamber"], "Academic chamber section with liner/jacket zones, heat-transfer labels, sensor bosses, flange datums, and no operational pressure/thrust sizing"),
        part(2, "Injector Architecture Taxonomy Plate", ["space", "propulsion", "injector_face"], "Non-buildable injector concept plate comparing injector families with blocked detail holes, manifold zones, face datum, and no orifice dimensions"),
        part(3, "Nozzle Contour Phenomena Study Shell", ["space", "propulsion", "nozzle_bell"], "Nozzle contour study shell with throat/exit/station labels, thermal/structural callouts, cutaway window, and no expansion-ratio performance claim"),
        part(4, "Regenerative Cooling Path Study Jacket", ["space", "thermal", "regen_cooling"], "Cooling-path teaching jacket with channel-route vocabulary, inlet/outlet interface labels, leak-inspection path, and no flow-rate/sizing recipe"),
        part(5, "Feed-System Architecture Manifold", ["space", "fluid", "feed_system"], "Conceptual oxidizer/fuel feed manifold map with valve/filter/check-element placeholders, port labels, isolation zones, and no propellant handling instruction"),
        part(6, "Turbopump Energy-Path Study Module", ["space", "propulsion", "turbopump"], "Academic turbopump module showing pump/turbine/shaft/bearing regions, energy-path arrows, service covers, and no performance/speed sizing"),
        part(7, "Instrumentation + Data Acquisition Ring", ["electronics", "sensor", "daq_ring"], "Sensor boss ring, harness channels, DAQ connector zones, calibration labels, and safe measurement vocabulary without operating procedure"),
        part(8, "Control Logic + Interlock Panel", ["electronics", "control", "interlock_panel"], "Conceptual control/interlock panel with state labels, inhibit blocks, connector keying, and no ignition/start sequence instructions"),
        part(9, "Thrust-Frame Load-Path Study Mount", ["mechanical", "structure", "thrust_frame"], "Academic thrust-frame/mount interface with trunnion pads, load-path arrows, bolted datum pads, and no flight qualification claim"),
        part(10, "Cutaway Safety Boundary + Annotation Cover", ["mechanical", "integration", "annotation_cover"], "Transparent cutaway cover and annotation frame that marks non-buildable academic boundaries, blocked parameters, and inspection labels"),
    ],
}

SUBSYSTEMS = [
    ("chamber_heat_transfer", "thermal", "Combustion chamber heat-transfer and structural jacket study", ["liner_zone", "jacket_zone", "heat_transfer_label", "sensor_boss", "flange_datum"]),
    ("injector_architecture", "fluid", "Injector taxonomy and manifold-zone study without buildable orifice details", ["injector_family_label", "blocked_orifice_detail", "manifold_zone", "face_datum", "mixing_concept_label"]),
    ("nozzle_expansion_study", "structures", "Nozzle contour, throat/exit station, and thermal/structural callout study", ["throat_station_label", "exit_station_label", "contour_section", "cutaway_window", "thermal_callout"]),
    ("regenerative_cooling_study", "thermal", "Regenerative cooling route vocabulary and leak/service boundary", ["cooling_channel_route", "inlet_interface_label", "outlet_interface_label", "leak_inspection_path", "service_cover"]),
    ("feed_system_architecture", "fluid", "Conceptual feed-system topology and valve/check/filter placeholders", ["oxidizer_path_label", "fuel_path_label", "valve_placeholder", "filter_placeholder", "isolation_zone"]),
    ("turbomachinery_energy_path", "rotating", "Pump/turbine/shaft/bearing energy-path study without performance sizing", ["pump_region", "turbine_region", "shaft_axis", "bearing_region", "energy_path_arrow"]),
    ("instrumentation_controls", "electronics", "Instrumentation, DAQ, interlock, and harness vocabulary", ["sensor_boss", "daq_connector", "harness_channel", "interlock_label", "calibration_label"]),
    ("thrust_frame_integration", "integration", "Academic load path, mount datums, and cutaway boundary", ["thrust_frame", "trunnion_pad", "load_path_arrow", "datum_pad", "non_buildable_boundary_label"]),
]


def micro_pack(seed: str, sub: tuple[str, str, str, list[str]]) -> dict[str, Any]:
    sid, discipline, function, evidence = sub
    criteria = deepcopy(COMMON_CRITERIA)
    criteria.append({
        "id": f"{sid}_domain_grammar",
        "criteria": [
            {
                "criterion": "academic_evidence_features",
                "good": f"Uses academic evidence features: {', '.join(evidence)}.",
                "bad": f"Omitted visible study grammar for {sid}.",
            },
            {
                "criterion": "blocked_operational_detail",
                "good": "Keeps dimensions, propellant handling, ignition, sizing, and operating steps blocked.",
                "bad": "Turns academic vocabulary into a build/test/operate recipe.",
            },
        ],
    })
    return {
        "schema": "blueprint_micro_pack_v1",
        "seed": seed,
        "subsystem": {
            "id": sid,
            "discipline": discipline,
            "function": function,
            "evidence_features": evidence,
        },
        "criteria": criteria,
        "boundary_note": BOUNDARY,
    }


def skeleton() -> dict[str, Any]:
    return {
        "schema": "blueprint_skeleton_pack_v1",
        "seed": NEW,
        "pass": "PASS-0",
        "instruction": "Lay out one top-level node per academic propulsion subsystem, global datums, cutaway/study zones, and non-buildable boundary labels. No detailed manufacturing geometry or operating recipe.",
        "disciplines": {
            "thermal": "Heat-transfer, cooling-path, and thermal-interface study vocabulary",
            "fluid": "Conceptual flow-path topology, manifolds, placeholders, labels, and blocked operational detail",
            "rotating": "Turbomachinery energy-path vocabulary without speed/performance sizing",
            "electronics": "Instrumentation, DAQ, harness, interlock, and control-state vocabulary",
            "structures": "Chamber/nozzle/thrust-frame load paths, cutaway shells, datums, and covers",
            "integration": "Mounting, service access, annotation covers, and academic safety boundaries",
        },
        "required_subsystems": [
            {
                "id": sid,
                "discipline": discipline,
                "function": function,
                "evidence_features": evidence,
                "criteria_refs": ["geometry_grounding", "assembly_integration", f"{sid}_domain_grammar"],
            }
            for sid, discipline, function, evidence in SUBSYSTEMS
        ],
        "completeness_rule": "Every academic subsystem must appear in part_tree with evidence features in geometry_ops; any operational build/test detail is a boundary failure.",
        "global_judgment_summary": COMMON_CRITERIA,
        "connection_taxonomy": {
            "rule": "Name conceptual interfaces with joint/path family + DOF + academic datum; avoid operational sizing.",
            "families": {
                "study_joint": ["bolted_datum_pad(0)", "cutaway_cover(0)", "service_panel(0)"],
                "conceptual_flow": ["labeled_feed_path(0)", "blocked_port_placeholder(0)", "manifold_zone(0)"],
                "instrumentation": ["sensor_boss_label(0)", "daq_connector_zone(0)", "harness_channel(0)"],
                "rotating_study": ["shaft_axis_label(1R)", "bearing_region_label(1R)", "energy_path_arrow(0)"],
            },
        },
        "boundary_note": BOUNDARY,
    }


def update_seed_vehicles() -> None:
    data = json.loads(VEHICLES.read_text(encoding="utf-8"))
    data.pop(OLD, None)
    data[NEW] = VEHICLE
    VEHICLES.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_packs() -> None:
    old_dir = PACKS / OLD
    new_dir = PACKS / NEW
    if old_dir.exists() and not new_dir.exists():
        shutil.move(str(old_dir), str(new_dir))
    new_dir.mkdir(parents=True, exist_ok=True)
    for path in new_dir.glob("*.json"):
        path.unlink()
    (new_dir / "skeleton.json").write_text(json.dumps(skeleton(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for sub in SUBSYSTEMS:
        (new_dir / f"{sub[0]}.json").write_text(json.dumps(micro_pack(NEW, sub), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_targets() -> None:
    data = json.loads(TARGETS.read_text(encoding="utf-8"))
    targets = data.setdefault("targets", {})
    old_targets = targets.pop(OLD, [])
    targets[NEW] = [
        {
            "label": "NASA 3D Resources",
            "url": "https://science.nasa.gov/3d-resources/",
            "license_hint": "NASA/public-government material; verify each asset page.",
            "why": "Safe public spacecraft/engine visual references for academic cutaway and annotation grammar.",
        },
        {
            "label": "NASA technical reports / NTRS liquid propulsion references",
            "url": "https://ntrs.nasa.gov/",
            "license_hint": "Verify each report/media asset; use as academic literature reference only.",
            "why": "Academic liquid propulsion terminology, subsystem decomposition, instrumentation, cooling, and turbomachinery vocabulary.",
        },
        *old_targets,
    ]
    TARGETS.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    update_seed_vehicles()
    update_packs()
    update_targets()
    print(f"upgraded {OLD} -> {NEW}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
