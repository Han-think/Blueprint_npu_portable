"""Attach seed-level operability and multiphysics profiles to all packs."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
PACKS = REPO / "20_dataset" / "packs"
DOC = REPO / "docs" / "SEED_OPERABILITY_PROFILES_2026-06-28.md"


PROFILES: dict[str, dict[str, Any]] = {
    "cubesat": {
        "operating_principle": "Small spacecraft architecture that routes loads through rails/frame, power through EPS/battery/solar, data through avionics stack, and heat to radiator/structure paths.",
        "primary_paths": {
            "load_path": ["rail/frame launch load path", "panel hinge load path", "payload bench to frame"],
            "fluid_path": [],
            "thermal_path": ["battery to frame conduction", "avionics heat to radiator face", "solar panel thermal exposure"],
            "electrical_path": ["solar panel to EPS", "battery to PDU", "PDU to avionics/payload"],
            "signal_path": ["antenna to radio", "OBC to sensors", "payload data to storage/downlink"],
        },
        "solver_focus": ["modal/launch-load FEA", "thermal balance proxy", "harness clearance review"],
    },
    "haptic_glove": {
        "operating_principle": "Wearable robotic hand interface that transfers finger motion through linkages/cables while preserving ergonomic fit, sensor routing, and safe contact surfaces.",
        "primary_paths": {
            "load_path": ["finger link force path", "palm base reaction path", "strap/contact pressure path"],
            "fluid_path": [],
            "thermal_path": ["electronics heat to palm shell", "skin-contact thermal comfort"],
            "electrical_path": ["battery/control board to actuators", "sensor power rail"],
            "signal_path": ["finger sensors to controller", "haptic actuator command routing"],
        },
        "solver_focus": ["linkage clearance", "ergonomic contact pressure", "cable bend radius"],
    },
    "long_range_recon_wing": {
        "operating_principle": "Fixed-wing UAV architecture that carries lift through spar/rib stations, routes propulsion/power through the fuselage, and isolates payload/sensor bays.",
        "primary_paths": {
            "load_path": ["wing spar bending path", "landing/payload bay reaction", "motor mount thrust reaction"],
            "fluid_path": ["external airflow over wing/body", "cooling airflow through electronics bay"],
            "thermal_path": ["battery heat to bay vents", "ESC/motor heat rejection"],
            "electrical_path": ["battery to ESC/motor", "battery to avionics/payload"],
            "signal_path": ["autopilot to servos", "payload sensor to datalink"],
        },
        "solver_focus": ["aero CFD proxy/OpenFOAM case", "wing bending FEA", "payload bay cooling"],
    },
    "tiltrotor": {
        "operating_principle": "VTOL aircraft architecture that transitions thrust vector through nacelle tilt axes while preserving wing load paths, slack-loop harnesses, and control authority.",
        "primary_paths": {
            "load_path": ["nacelle thrust to wing spar", "tilt bearing reaction", "landing gear reaction"],
            "fluid_path": ["rotor slipstream over wing", "cooling airflow through nacelles"],
            "thermal_path": ["motor/ESC heat to nacelle vents", "battery bay heat path"],
            "electrical_path": ["battery to tilt/propulsion ESCs", "power distribution to avionics"],
            "signal_path": ["flight controller to tilt servo", "IMU/GPS/pitot to controller"],
        },
        "solver_focus": ["tilt-axis joint FEA", "rotor/wing flow interaction proxy", "harness slack clearance"],
    },
    "robot_arm": {
        "operating_principle": "Serial manipulator architecture that carries torque through joints/links, routes cables along the spine, and exposes serviceable actuator/sensor modules.",
        "primary_paths": {
            "load_path": ["base to shoulder torque path", "link bending path", "tool flange payload path"],
            "fluid_path": ["optional pneumatic utility routing"],
            "thermal_path": ["motor heat to joint housings", "drive electronics bay heat path"],
            "electrical_path": ["drive power to each joint", "grounding through base/electronics"],
            "signal_path": ["encoder feedback", "tool I/O", "joint command bus"],
        },
        "solver_focus": ["joint torque/FoS screening", "cable bend and service access", "link stiffness"],
    },
    "small_launch_vehicle": {
        "operating_principle": "Academic launch-vehicle architecture study that separates stage shell, tank reference articles, avionics, recovery, and propulsion study sections for reviewable load/path grammar.",
        "primary_paths": {
            "load_path": ["stage stack axial load", "interstage separation datum", "fairing/payload adapter reaction"],
            "fluid_path": ["conceptual propellant route labels only", "vent/drain label topology only"],
            "thermal_path": ["engine study heat-zone labels", "avionics bay thermal isolation"],
            "electrical_path": ["battery/power study module to avionics", "safe harness routing labels"],
            "signal_path": ["avionics to instrumentation labels", "recovery command boundary labels"],
        },
        "solver_focus": ["stage shell FEA", "thermal zone annotation", "non-operational topology review"],
        "blocked_outputs": ["operational propellant handling", "ignition/test procedure", "flight qualification instruction"],
    },
    "inline_6_engine_gasoline": {
        "operating_principle": "Internal combustion engine architecture study that coordinates cranktrain rotation, gas exchange, cooling, lubrication, fuel/ignition harness, and service access.",
        "primary_paths": {
            "load_path": ["combustion load to block/crankcase", "mount bracket reaction", "bearing cap load path"],
            "fluid_path": ["intake/exhaust runner topology", "oil gallery/pickup path", "coolant jacket path"],
            "thermal_path": ["head/block heat to coolant", "exhaust heat shield path", "oil cooling path"],
            "electrical_path": ["ignition/fuel rail harness power", "sensor power routing"],
            "signal_path": ["crank/cam sensor", "temperature/pressure sensors", "injector/coil command"],
        },
        "solver_focus": ["coolant/oil passage review", "block/head thermal path", "mount/load FEA"],
    },
    "inline_6_engine_diesel": {
        "operating_principle": "Diesel engine architecture study with reinforced block/head, heavy cranktrain, common-rail topology, turbo air path, cooling/lubrication, and service datums.",
        "primary_paths": {
            "load_path": ["high-compression block/head load path", "bearing ladder reaction", "mount/bellhousing reaction"],
            "fluid_path": ["common-rail layout topology", "turbo/exhaust/charge air route", "oil/coolant route"],
            "thermal_path": ["turbo/exhaust heat shield", "oil cooler/filter module", "head/block heat rejection"],
            "electrical_path": ["injector harness", "sensor/actuator power", "glow/control harness"],
            "signal_path": ["rail pressure sensor", "temperature/boost sensors", "engine control signals"],
        },
        "solver_focus": ["reinforced housing FEA", "air/exhaust routing CFD proxy", "thermal shielding"],
    },
    "centrifugal_pump": {
        "operating_principle": "Rotating fluid machine that converts shaft power to pressure/flow through impeller and volute while sealing leakage and carrying bearing loads to baseplate.",
        "primary_paths": {
            "load_path": ["shaft to bearings", "casing pressure to feet/baseplate", "pipe flange reaction"],
            "fluid_path": ["suction eye", "impeller channels", "volute", "discharge flange", "leak/flush path"],
            "thermal_path": ["bearing heat to housing", "seal friction heat", "fluid heat transfer"],
            "electrical_path": ["motor power interface if modeled"],
            "signal_path": ["optional pressure/temperature vibration sensor ports"],
        },
        "solver_focus": ["OpenFOAM volute/impeller domain", "bearing/shaft FEA", "seal leak path review"],
    },
    "hydraulic_manifold": {
        "operating_principle": "Hydraulic block architecture that routes pressure/return/work ports through drilled galleries, cartridge valves, plugs, sensors, and service labels.",
        "primary_paths": {
            "load_path": ["port pressure to block body", "mount feet reaction", "plug/valve thread reaction"],
            "fluid_path": ["P/T/A/B port network", "cross-drilled galleries", "relief/check return path"],
            "thermal_path": ["fluid heating to block", "sensor/coil local heat"],
            "electrical_path": ["sensor/solenoid power routing"],
            "signal_path": ["pressure sensor/test port signals", "valve command wiring"],
        },
        "solver_focus": ["gallery pressure-loss CFD", "block stress around ports", "service access"],
    },
    "battery_pack_module": {
        "operating_principle": "No-live-energy battery module architecture that organizes cell support, busbar covers, BMS, thermal interface, venting, isolation, and service disconnect grammar.",
        "primary_paths": {
            "load_path": ["cell compression/end-plate path", "enclosure crash/isolation path", "mounting reaction"],
            "fluid_path": ["vent path", "coolant interface if cold plate present"],
            "thermal_path": ["cell heat to cold plate", "busbar/fuse local heat", "enclosure heat path"],
            "electrical_path": ["cell group to protected busbar", "service disconnect boundary", "BMS sense lines"],
            "signal_path": ["voltage/temp sense harness", "BMS communication", "interlock loop"],
        },
        "solver_focus": ["thermal spreading", "isolation/clearance review", "vent path topology"],
        "blocked_outputs": ["live pack assembly instruction", "unsafe high-voltage operation"],
    },
    "liquid_cold_plate": {
        "operating_principle": "Thermal management plate that transfers heat from electronics pads into internal liquid channels and manifold ports while maintaining gasket/leak boundaries.",
        "primary_paths": {
            "load_path": ["mount screw compression", "gasket compression", "module pad contact"],
            "fluid_path": ["inlet manifold", "serpentine channels", "outlet manifold", "drain/bleed/test path"],
            "thermal_path": ["device pad to plate", "plate to coolant", "sensor pad feedback"],
            "electrical_path": ["ground/isolation washer context"],
            "signal_path": ["temperature sensor routing if present"],
        },
        "solver_focus": ["OpenFOAM channel flow", "thermal conduction/convection", "gasket compression review"],
    },
    "cnc_axis_carriage": {
        "operating_principle": "Precision linear axis that constrains travel with rails/bearing blocks, drives motion through a screw/motor, protects ways, and routes sensors/lubrication.",
        "primary_paths": {
            "load_path": ["tool/load to carriage plate", "bearing block to rails", "ballscrew thrust to supports"],
            "fluid_path": ["lubrication manifold to rail/block points"],
            "thermal_path": ["motor heat", "bearing/screw friction heat", "thermal growth datum"],
            "electrical_path": ["motor power", "sensor power", "grounding"],
            "signal_path": ["home/limit sensors", "encoder/motor command", "lubrication status"],
        },
        "solver_focus": ["carriage stiffness FEA", "motion clearance", "lube routing"],
    },
    "gearbox_reducer": {
        "operating_principle": "Two-stage reducer that carries torque through gear meshes, supports shafts with bearings, manages lubrication/sealing, and reacts loads through housing mounts.",
        "primary_paths": {
            "load_path": ["input shaft to gear mesh", "gear mesh to output shaft", "bearing to housing/mounts"],
            "fluid_path": ["oil splash path", "fill/drain/level/breather path"],
            "thermal_path": ["gear mesh heat to oil/housing", "bearing heat path"],
            "electrical_path": [],
            "signal_path": ["optional speed/vibration/temperature sensors"],
        },
        "solver_focus": ["housing FEA", "lubrication topology", "thermal heat rejection"],
    },
    "underwater_sealed_sensor_housing": {
        "operating_principle": "Sealed marine electronics housing that carries pressure loads through shell/caps, routes cable penetration safely, and supports internal sensor/electronics trays.",
        "primary_paths": {
            "load_path": ["external pressure to shell/caps", "cradle clamp reaction", "window/cap retaining ring"],
            "fluid_path": ["external water exclusion boundary", "leak-test port path", "drain path"],
            "thermal_path": ["electronics heat to shell/water", "window/cap thermal path"],
            "electrical_path": ["cable gland power entry", "grounding to tray/shell"],
            "signal_path": ["sensor signal through cable gland", "internal board connector routing"],
        },
        "solver_focus": ["pressure shell FEA", "seal/gland leak boundary", "thermal dissipation to water"],
    },
    "liquid_rocket_engine_academic": {
        "operating_principle": "Academic liquid propulsion architecture study linking chamber/nozzle, injector taxonomy, regenerative cooling, feed topology, turbomachinery, instrumentation, controls, and thrust-frame load path.",
        "primary_paths": {
            "load_path": ["chamber/nozzle thrust-frame path", "feed/turbomachinery mount reactions", "sensor/cover service loads"],
            "fluid_path": ["conceptual fuel/oxidizer feed topology", "injector manifold zones", "cooling jacket route labels"],
            "thermal_path": ["chamber liner to jacket", "nozzle thermal callouts", "regenerative cooling study path"],
            "electrical_path": ["DAQ/control/interlock power boundaries", "sensor power routing"],
            "signal_path": ["pressure/temperature/vibration sensor paths", "interlock state labels", "DAQ connector routing"],
        },
        "solver_focus": ["topology-only CFD/thermal study", "thrust-frame FEA", "instrumentation/control review"],
        "blocked_outputs": ["buildable injector sizing", "propellant handling", "ignition/start/test procedure", "operating pressure/thrust/mass-flow recipe"],
    },
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def apply_profile_to_pack(path: Path, seed: str, profile: dict[str, Any]) -> bool:
    data = load_json(path)
    if not isinstance(data, dict):
        return False
    data["operability_profile"] = profile
    write_json(path, data)
    return True


def render_doc(applied: list[str]) -> str:
    lines = [
        "# Seed Operability Profiles - 2026-06-28",
        "",
        "All 16 seeds now carry an `operability_profile` in their skeleton and PASS-1 micro-packs.",
        "The profile forces generation toward operation-aware structure, multiphysics path tracing, and solver readiness.",
        "",
        "| Seed | Operating Principle | Solver Focus |",
        "| --- | --- | --- |",
    ]
    for seed in sorted(PROFILES):
        p = PROFILES[seed]
        lines.append(
            f"| `{seed}` | {p['operating_principle']} | {', '.join(p.get('solver_focus') or [])} |"
        )
    lines += [
        "",
        "## Applied Files",
        "",
        f"- profiles: {len(PROFILES)}",
        f"- pack files updated: {len(applied)}",
        "",
        "High-risk seeds keep physics-grounded analysis intent while blocking unsafe operational recipes.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    applied: list[str] = []
    for seed, profile in PROFILES.items():
        seed_dir = PACKS / seed
        if not seed_dir.exists():
            raise FileNotFoundError(seed_dir)
        for path in sorted(seed_dir.glob("*.json")):
            if apply_profile_to_pack(path, seed, profile):
                applied.append(str(path.relative_to(REPO)))
        top_pack = PACKS / f"{seed}.json"
        if top_pack.exists() and apply_profile_to_pack(top_pack, seed, profile):
            applied.append(str(top_pack.relative_to(REPO)))
    DOC.write_text(render_doc(applied), encoding="utf-8")
    print(f"profiles={len(PROFILES)} pack_files={len(applied)}")
    print(DOC)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
