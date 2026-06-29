"""Bootstrap engineering expansion seeds for Blueprint XPU.

This script adds headless-generation seed definitions, PASS-0 skeleton packs,
per-subsystem micro-packs, and reference-source targets for broad engineering
design domains. It intentionally keeps high-risk propulsion material at
academic, non-operational, non-buildable study boundaries.
"""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
VEHICLES_FILE = REPO / "20_dataset" / "seed_vehicles.json"
PACKS = REPO / "20_dataset" / "packs"
TARGETS_FILE = REPO / "20_dataset" / "reference_assets" / "seed_reference_targets.json"

COMMON_DISCIPLINES = {
    "structures": "Load-bearing bodies, frames, ribs, bosses, covers, and stiffness paths",
    "rotating": "Shafts, bearings, gears, crank/rotor elements, couplings, and balance references",
    "fluid": "Ports, channels, galleries, manifolds, volutes, pressure boundaries, and drain paths",
    "thermal": "Heat paths, cooling plates/jackets/fins, thermal pads, and service-visible heat flow",
    "power": "Cells, busbars, disconnects, power electronics, insulation, and protected terminals",
    "electronics": "Boards, sensors, cable channels, EMI/grounding, connector keying, and covers",
    "sealing": "Gaskets, O-ring grooves, gland interfaces, pressure caps, vents, and leak inspection",
    "actuation": "Motors, screws, rails, linkages, valves, clutches, and serviceable actuator modules",
    "integration": "Datums, fastener patterns, service access, alignment features, assembly order",
    "safety_boundary": "Academic non-operational constraints, labels, blocked performance claims",
}

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
                "good": "Coordinates span stations, ports, bearing seats, service faces, or datum pads.",
                "bad": "All geometry is stacked at the origin or represented as one box/cylinder.",
            },
            {
                "criterion": "non_box_feature_variety",
                "good": "Uses pockets, channels, bosses, bolt patterns, ribs, seals, and inspection covers.",
                "bad": "Only primitive body solids with no interface or service evidence.",
            },
        ],
    },
    {
        "id": "assembly_integration",
        "criteria": [
            {
                "criterion": "connection_type_named",
                "good": "Each adjacent interface names a joint family, DOF, clearance, datum, and mating feature.",
                "bad": "Interfaces are vague mounts with no reciprocal feature or clearance.",
            },
            {
                "criterion": "service_access",
                "good": "Wear parts, covers, plugs, connectors, seals, or cartridges have visible removal paths.",
                "bad": "Maintenance-critical items are trapped behind sealed geometry.",
            },
            {
                "criterion": "load_or_flow_path_closure",
                "good": "The main load, torque, heat, fluid, or current path is traceable through named features.",
                "bad": "Functional flow/load claims stop at a shell without interfaces.",
            },
        ],
    },
]


def part(pid: int, label: str, preset: list[str], spec: str) -> dict[str, Any]:
    return {"id": f"p{pid}", "label": label, "preset": preset, "spec": spec}


SEEDS: dict[str, dict[str, Any]] = {
    "inline_6_engine_gasoline": {
        "vehicle": {
            "id": "inline_6_engine_gasoline",
            "label": "Inline-6 Gasoline Engine Assembly",
            "wikiTitle": "Straight-six engine",
            "desc": "Conceptual inline-six gasoline engine cutaway assembly for structural, cooling, lubrication, valvetrain, intake, exhaust, and service-access grammar; not a certified running engine",
            "material": "Al alloy + cast iron + steel + elastomer",
            "process": "CNC + casting reference + FDM",
            "mass": "~180kg reference class",
            "envelope": "900x650x750 mm",
            "parts": [
                part(1, "Cylinder Block + Crankcase", ["mechanical", "engine", "block"], "Inline-6 block with six cylinder bores, crankcase skirt, coolant jacket cues, oil gallery, main bearing cap pads, deck gasket face"),
                part(2, "Crankshaft + Main Bearing Set", ["mechanical", "rotating", "shaft"], "Seven-main-bearing crankshaft module with counterweights, thrust bearing face, oil holes, flywheel flange, journal labels"),
                part(3, "Piston + Connecting Rod Set x 6", ["mechanical", "engine", "piston_rod"], "Piston/rod educational cartridge set with wrist pin bosses, big-end caps, ring groove cues, orientation marks"),
                part(4, "Cylinder Head + DOHC Valvetrain", ["mechanical", "engine", "cylinder_head"], "Cylinder head with intake/exhaust ports, cam carrier, valve cover face, spark plug wells, gasket datum"),
                part(5, "Intake Manifold + Throttle Body", ["mechanical", "fluid", "manifold"], "Gasoline intake plenum with six runners, throttle body flange, injector/fuel rail clearance, sensor boss"),
                part(6, "Exhaust Manifold + Heat Shield", ["mechanical", "fluid", "manifold"], "Six-runner exhaust manifold reference structure with collector flange, oxygen sensor boss, heat shield standoff, gasket face"),
                part(7, "Timing Chain Front Cover", ["mechanical", "engine", "timing_cover"], "Front timing cover with chain path window, cam/crank alignment marks, seal bore, service fasteners"),
                part(8, "Oil Pan + Pump Pickup", ["mechanical", "fluid", "sump"], "Oil sump with drain plug, baffle ribs, pickup tube reference section, gasket rail, service access"),
                part(9, "Fuel Rail + Injector Harness", ["mechanical", "fluid", "fuel_rail"], "Low-pressure gasoline fuel rail reference structure with injector pockets, connector keying, harness clips, pressure sensor boss"),
                part(10, "Accessory Drive + Mount Brackets", ["mechanical", "actuation", "bracket"], "Belt accessory bracket set with alternator/AC/pump bosses, belt plane datum, tensioner pivot, mounting ears"),
            ],
        },
        "subsystems": [
            ("engine_block", "structures", "Block, deck, crankcase, bores, jacket, gallery", ["cylinder_bore_x6", "deck_gasket_face", "coolant_jacket", "oil_gallery", "main_bearing_cap_pad"]),
            ("rotating_cranktrain", "rotating", "Crankshaft, pistons, rods, bearing interfaces", ["main_journal", "rod_journal", "counterweight", "piston_pin_boss", "big_end_cap"]),
            ("cylinder_head_valvetrain", "actuation", "Head ports, cams, valve cover, spark plug wells", ["intake_port", "exhaust_port", "cam_carrier", "spark_plug_well", "valve_cover_gasket"]),
            ("intake_exhaust", "fluid", "Gas exchange manifolds and heat shield interfaces", ["intake_runner_x6", "plenum", "exhaust_runner_x6", "collector_flange", "heat_shield_standoff"]),
            ("lubrication_cooling", "thermal", "Oil and coolant service paths", ["oil_pickup", "drain_plug", "coolant_port", "thermostat_face", "service_plug"]),
            ("fuel_ignition_harness", "electronics", "Fuel rail, injector wells, spark/coil harness", ["fuel_rail", "injector_pocket", "coil_connector", "harness_channel", "sensor_boss"]),
            ("integration_accessory_mounts", "integration", "Accessory brackets, engine mounts, bellhousing/flywheel interfaces", ["mount_boss", "belt_plane_datum", "flywheel_flange", "bellhousing_pattern", "service_cover"]),
        ],
    },
    "inline_6_engine_diesel": {
        "vehicle": {
            "id": "inline_6_engine_diesel",
            "label": "Inline-6 Diesel Engine Assembly",
            "wikiTitle": "Diesel engine",
            "desc": "Conceptual inline-six diesel engine cutaway assembly emphasizing stronger block/head grammar, common-rail fuel path, turbo air path, cooling/lubrication, and service access; not a certified running engine",
            "material": "Compacted graphite iron + steel + Al alloy",
            "process": "CNC + casting reference + FDM",
            "mass": "~320kg reference class",
            "envelope": "1100x720x850 mm",
            "parts": [
                part(1, "Reinforced Cylinder Block", ["mechanical", "engine", "block"], "Diesel I6 block with thick deck, six bores, cross-bolted main cap cues, coolant jacket, oil gallery"),
                part(2, "Forged Crankshaft + Bearing Ladder", ["mechanical", "rotating", "shaft"], "Heavy crankshaft and bearing ladder with main caps, thrust face, oil feeds, flywheel flange"),
                part(3, "Piston/Rod Assembly x 6", ["mechanical", "engine", "piston_rod"], "Diesel piston/rod educational set with bowl crown cue, wrist pin boss, rod cap bolts, ring bands"),
                part(4, "Cylinder Head + Injector Wells", ["mechanical", "engine", "cylinder_head"], "Diesel head with injector wells, glow plug ports, valve bridge, intake/exhaust ports, gasket datum"),
                part(5, "Common Rail + Injector Harness", ["mechanical", "fluid", "fuel_rail"], "Common-rail layout reference with rail brackets, injector pockets, return line path, harness channel; academic low-detail reference"),
                part(6, "Turbocharger + Exhaust Manifold Study Section", ["mechanical", "fluid", "turbo"], "Turbo/exhaust academic study section with turbine housing shell, compressor shell, oil feed/return bosses, heat shield"),
                part(7, "Intake/EGR Cooler Path Study Section", ["mechanical", "thermal", "cooler"], "Charge-air/EGR cooler routing reference with flanges, gasket faces, bypass/service cover, sensor bosses"),
                part(8, "Oil Cooler + Filter Module", ["mechanical", "thermal", "oil_cooler"], "Oil cooler/filter module with cartridge cap, coolant ports, gasket face, drain boss"),
                part(9, "Timing Gear Housing", ["mechanical", "rotating", "gear_housing"], "Front gear housing with idler gear pockets, crank/cam gear datums, service cover, seal bore"),
                part(10, "Engine Mount + Bellhousing Interfaces", ["mechanical", "structure", "mount"], "Mount brackets and bellhousing adapter pattern with datum pads, bolt groups, lifting lug cues"),
            ],
        },
        "subsystems": [
            ("reinforced_block_head", "structures", "High-compression structural block/head grammar", ["thick_deck", "cross_bolt_boss", "main_bearing_ladder", "head_bolt_pattern", "gasket_face"]),
            ("diesel_cranktrain", "rotating", "Heavy rotating group and bearing support", ["main_journal", "rod_cap_bolt_pad", "counterweight", "bearing_ladder", "flywheel_flange"]),
            ("common_rail_injection_study", "fluid", "Academic high-pressure layout vocabulary only", ["common_rail", "injector_well", "return_line_channel", "rail_bracket", "harness_key"]),
            ("turbo_air_exhaust_study", "fluid", "Turbo/exhaust/charge air routing study reference", ["turbine_shell", "compressor_shell", "oil_feed_boss", "charge_pipe_flange", "heat_shield"]),
            ("thermal_lubrication", "thermal", "Coolant/oil galleries, cooler and filter access", ["coolant_port", "oil_cooler_face", "filter_cartridge_cap", "drain_boss", "service_plug"]),
            ("gear_timing_access", "rotating", "Timing gears and front housing serviceability", ["gear_pocket", "idler_axis", "seal_bore", "timing_mark", "front_cover"]),
            ("mounting_integration", "integration", "Mounts, lifting, bellhousing, service datums", ["mount_bracket", "lifting_lug", "bellhousing_pattern", "datum_pad", "service_window"]),
        ],
    },
    "centrifugal_pump": {
        "vehicle": {
            "id": "centrifugal_pump",
            "label": "Centrifugal Pump Assembly",
            "wikiTitle": "Centrifugal pump",
            "desc": "Industrial centrifugal pump cutaway assembly for volute, impeller, shaft, bearing, seal, flange, and service-access grammar",
            "material": "Cast iron + stainless steel + elastomer",
            "process": "Casting reference + CNC + FDM",
            "mass": "~35kg",
            "envelope": "520x320x380 mm",
            "parts": [
                part(1, "Volute Casing", ["mechanical", "fluid", "pump_volute"], "Spiral volute casing with inlet eye, outlet flange, pressure boundary, drain plug, inspection boss"),
                part(2, "Impeller", ["mechanical", "rotating", "impeller"], "Closed impeller with hub, blade channels, wear ring face, balance drill cues"),
                part(3, "Pump Shaft", ["mechanical", "rotating", "shaft"], "Stepped shaft with keyway, impeller nut, bearing journals, coupling end"),
                part(4, "Bearing Housing", ["mechanical", "structure", "bearing_housing"], "Bearing frame with front/rear bearing seats, grease ports, oil sight window, mounting feet"),
                part(5, "Mechanical Seal Cartridge", ["mechanical", "sealing", "seal"], "Seal cartridge reference structure with gland plate, O-ring groove, flush port, leakage drain"),
                part(6, "Suction/Discharge Flange Set", ["mechanical", "fluid", "flange"], "ANSI-style flanges with bolt circle, gasket face, flow arrow, pipe alignment datum"),
                part(7, "Coupling Guard + Motor Adapter", ["mechanical", "integration", "guard"], "Motor adapter and coupling guard with service window, fastener tabs, alignment slots"),
                part(8, "Baseplate + Mount Pads", ["mechanical", "structure", "baseplate"], "Baseplate with slotted mount holes, leveling pads, drain channel, lifting points"),
            ],
        },
        "subsystems": [
            ("volute_pressure_boundary", "fluid", "Casing pressure and flow path", ["inlet_eye", "volute_channel", "outlet_flange", "drain_plug", "inspection_boss"]),
            ("impeller_rotor", "rotating", "Impeller and shaft rotating path", ["impeller_hub", "blade_channel", "wear_ring_face", "shaft_keyway", "impeller_nut"]),
            ("bearing_support", "structures", "Bearing frame and support", ["bearing_seat_front", "bearing_seat_rear", "grease_port", "oil_sight_window", "mounting_foot"]),
            ("seal_gland", "sealing", "Seal cartridge and leakage path", ["gland_plate", "o_ring_groove", "flush_port", "leak_drain", "seal_access"]),
            ("pipe_motor_integration", "integration", "Pipe flanges, motor adapter, baseplate alignment", ["bolt_circle", "gasket_face", "alignment_slot", "coupling_guard", "leveling_pad"]),
        ],
    },
    "hydraulic_manifold": {
        "vehicle": {
            "id": "hydraulic_manifold",
            "label": "Hydraulic Manifold Block Assembly",
            "wikiTitle": "Hydraulic machinery",
            "desc": "Hydraulic manifold block concept for porting, cross-drilled galleries, cartridge valves, plugs, labels, and service access",
            "material": "Al 6061 + steel plugs + elastomer seals",
            "process": "CNC",
            "mass": "~8kg",
            "envelope": "260x160x120 mm",
            "parts": [
                part(1, "Main Manifold Block", ["mechanical", "fluid", "manifold"], "CNC manifold block with P/T/A/B ports, cross-drilled galleries, plug bosses, datum faces"),
                part(2, "Cartridge Valve Set", ["mechanical", "fluid", "valve"], "Screw-in cartridge valve cavities with O-ring lands, wrench clearance, port labels"),
                part(3, "Pressure Relief Valve Section", ["mechanical", "fluid", "relief_valve"], "Relief valve pocket, adjustment cap, spring chamber cue, tank return path"),
                part(4, "Check Valve Section", ["mechanical", "fluid", "check_valve"], "Check valve cavity with flow arrow, seat cone cue, service plug"),
                part(5, "Sensor + Test Port Set", ["mechanical", "electronics", "sensor_port"], "Pressure transducer boss, test coupler port, cable exit, protective cover"),
                part(6, "Mounting Feet + Label Plate", ["mechanical", "integration", "mount"], "Mounting feet, engraved circuit label plate, orientation arrows, service side datum"),
            ],
        },
        "subsystems": [
            ("manifold_flow_network", "fluid", "Port map and drilled gallery grammar", ["p_port", "t_port", "a_port", "b_port", "cross_drill", "plug_boss"]),
            ("cartridge_valve_cavities", "fluid", "Cartridge pockets and seal lands", ["valve_cavity", "o_ring_land", "wrench_clearance", "retainer_thread", "flow_arrow"]),
            ("pressure_control", "fluid", "Relief/check valve sections", ["relief_adjuster_cap", "spring_chamber", "check_seat", "tank_return_path", "service_plug"]),
            ("instrumentation_access", "electronics", "Sensor and test access", ["pressure_sensor_boss", "test_port", "cable_exit", "protective_cover", "label_plate"]),
            ("mounting_datum", "integration", "Mounting and service orientation", ["mounting_foot", "datum_face", "engraved_label", "service_side", "bolt_pattern"]),
        ],
    },
    "battery_pack_module": {
        "vehicle": {
            "id": "battery_pack_module",
            "label": "Battery Pack Module",
            "wikiTitle": "Electric vehicle battery",
            "desc": "Serviceable battery module concept for cell support, busbars, BMS, cooling plate interface, venting, isolation, and enclosure grammar; no live-energy build instruction",
            "material": "Al enclosure + polymer holders + copper busbar reference structure",
            "process": "Sheet metal + FDM + CNC",
            "mass": "~18kg",
            "envelope": "520x360x160 mm",
            "parts": [
                part(1, "Cell Carrier Tray", ["propulsion", "electric", "battery_tray"], "Cell holder tray with repeated cell pockets, compression pads, locator ribs, module datum"),
                part(2, "Busbar + Fuse Cover Study Section", ["propulsion", "electric", "busbar"], "Insulated busbar reference structure with fuse windows, terminal guards, polarity labels, no live-energy claim"),
                part(3, "BMS Electronics Bay", ["electronics", "power", "bms"], "BMS board pocket, sensing harness channels, service connector, EMI shield cover"),
                part(4, "Cooling Plate Interface", ["mechanical", "thermal", "cold_plate"], "Cooling plate contact face, thermal pad zones, inlet/outlet ports, leak inspection channel"),
                part(5, "Pack Enclosure + Lid", ["mechanical", "structure", "enclosure"], "Gasketed enclosure shell with lid flange, fastener pattern, vent path, service label"),
                part(6, "HV Connector + Service Disconnect Study Section", ["propulsion", "electric", "connector"], "Keyed HV connector reference structure, service disconnect handle, low-voltage connector, strain relief"),
                part(7, "Crash/Isolation End Plates", ["mechanical", "structure", "end_plate"], "End plates with crush ribs, isolation spacers, tie rod bosses, lifting tabs"),
            ],
        },
        "subsystems": [
            ("cell_support", "structures", "Cell pockets and compression grammar", ["cell_pocket_array", "compression_pad", "locator_rib", "tie_rod_boss", "module_datum"]),
            ("electrical_distribution_study", "power", "Busbar/fuse/terminal layout vocabulary only", ["busbar_cover", "fuse_window", "terminal_guard", "polarity_label", "sense_wire_channel"]),
            ("bms_harness", "electronics", "BMS and signal harness routing", ["bms_board_pocket", "service_connector", "emi_shield", "harness_channel", "ground_point"]),
            ("thermal_interface", "thermal", "Cooling plate and thermal pad contact", ["thermal_pad_zone", "coolant_inlet", "coolant_outlet", "leak_channel", "cold_plate_face"]),
            ("sealed_enclosure_safety", "sealing", "Lid gasket, vent, disconnect, no-live-energy boundary", ["lid_flange", "gasket_groove", "vent_path", "disconnect_handle", "warning_label"]),
        ],
    },
    "liquid_cold_plate": {
        "vehicle": {
            "id": "liquid_cold_plate",
            "label": "Liquid Cold Plate Assembly",
            "wikiTitle": "Cold plate",
            "desc": "Liquid cold plate concept for serpentine channels, manifolds, gasket, electronics mounting, leak inspection, and thermal interface grammar",
            "material": "Al 6061 + copper insert + elastomer gasket",
            "process": "CNC + brazed reference",
            "mass": "~3kg",
            "envelope": "320x220x40 mm",
            "parts": [
                part(1, "Cold Plate Body", ["mechanical", "thermal", "cold_plate"], "Machined plate body with serpentine channel, fin islands, mounting bosses, flatness datum"),
                part(2, "Inlet/Outlet Manifold Cap", ["mechanical", "fluid", "manifold"], "Manifold cap with hose barb/AN port faces, O-ring groove, flow arrow, fastener pattern"),
                part(3, "Gasket + Seal Track", ["mechanical", "sealing", "gasket"], "Continuous gasket groove, compression stops, leak witness channel, corner reliefs"),
                part(4, "Power Module Mount Pads", ["electronics", "thermal", "mount"], "IGBT/MOSFET mount pads, thermal paste zones, isolation washer pockets, sensor pad"),
                part(5, "Leak Test + Drain Ports", ["mechanical", "fluid", "test_port"], "Pressure test port, drain plug, bleed screw, service labels"),
                part(6, "Cover Plate", ["mechanical", "structure", "cover"], "Bolted cover with ribbing, datum pins, inspection window label, torque sequence marks"),
            ],
        },
        "subsystems": [
            ("thermal_channel_network", "thermal", "Serpentine cooling path and heat source pads", ["serpentine_channel", "fin_island", "thermal_pad_zone", "temperature_sensor_pad", "flatness_datum"]),
            ("manifold_ports", "fluid", "Inlet/outlet and flow distribution", ["inlet_port", "outlet_port", "manifold_cap", "flow_arrow", "hose_boss"]),
            ("seal_leak_boundary", "sealing", "Gasket track and leak witness path", ["gasket_groove", "compression_stop", "leak_witness_channel", "corner_relief", "bleed_screw"]),
            ("electronics_mounting", "electronics", "Power device mounting and isolation", ["module_mount_pad", "isolation_washer_pocket", "ground_point", "fastener_pattern", "service_label"]),
            ("service_test_access", "integration", "Test/drain/cover assembly", ["test_port", "drain_plug", "datum_pin", "torque_sequence_mark", "inspection_label"]),
        ],
    },
    "cnc_axis_carriage": {
        "vehicle": {
            "id": "cnc_axis_carriage",
            "label": "CNC Linear Axis Carriage",
            "wikiTitle": "Linear motion",
            "desc": "Precision CNC linear axis carriage concept for rails, bearing blocks, ball screw, motor mount, way covers, sensors, and lubrication grammar",
            "material": "Cast Al + steel rails + polymer covers",
            "process": "CNC + FDM cover reference",
            "mass": "~22kg",
            "envelope": "700x220x180 mm",
            "parts": [
                part(1, "Carriage Plate", ["mechanical", "structure", "carriage"], "Machined carriage with rail block bolt pattern, datum edge, dowel holes, lightening pockets"),
                part(2, "Linear Rail Pair + Bearing Blocks", ["mechanical", "actuation", "linear_rail"], "Two linear rails with four bearing block footprints, grease ports, rail datum references"),
                part(3, "Ball Screw + Nut Housing", ["mechanical", "actuation", "ballscrew"], "Ball screw shaft, nut housing, fixed/floating bearing ends, preload label"),
                part(4, "Servo Motor Mount + Coupling Guard", ["mechanical", "actuation", "motor_mount"], "Servo flange, coupling guard, belt/shaft alignment datum, service slots"),
                part(5, "Limit/Home Sensor Brackets", ["electronics", "sensor", "limit_switch"], "Home and limit switch brackets, cable channel, target flag, adjustment slots"),
                part(6, "Way Cover + Wiper Set", ["mechanical", "sealing", "way_cover"], "Telescoping way cover reference structure, wiper lip, chip guard, fastener tabs"),
                part(7, "Lubrication Manifold", ["mechanical", "fluid", "lube"], "Lubrication ports, distribution channels, grease nipples, service labels"),
            ],
        },
        "subsystems": [
            ("carriage_structure", "structures", "Datum plate, rail blocks, pockets", ["datum_edge", "dowel_hole", "rail_block_pattern", "lightening_pocket", "mount_face"]),
            ("linear_guidance", "actuation", "Rails and bearing blocks", ["linear_rail", "bearing_block", "grease_port", "rail_datum", "wiper_mount"]),
            ("ball_screw_drive", "rotating", "Screw/nut/bearing drive path", ["ball_screw", "nut_housing", "fixed_bearing", "floating_bearing", "preload_label"]),
            ("motor_sensor_integration", "electronics", "Motor, coupling, sensors, cable routing", ["servo_flange", "coupling_guard", "home_sensor", "limit_sensor", "cable_channel"]),
            ("protection_lubrication", "sealing", "Way covers and lubrication", ["way_cover", "wiper_lip", "chip_guard", "lube_manifold", "service_nipple"]),
        ],
    },
    "gearbox_reducer": {
        "vehicle": {
            "id": "gearbox_reducer",
            "label": "Two-Stage Gearbox Reducer",
            "wikiTitle": "Gear train",
            "desc": "Two-stage gearbox reducer concept for housing, gears, shafts, bearings, oiling, seals, covers, and mounting grammar",
            "material": "Cast Al housing + steel gears/shafts + elastomer seals",
            "process": "Casting reference + CNC + FDM",
            "mass": "~14kg",
            "envelope": "360x240x220 mm",
            "parts": [
                part(1, "Split Gearbox Housing", ["mechanical", "structure", "gearbox"], "Split housing with bearing bores, gasket flange, ribbing, inspection cover"),
                part(2, "Input Shaft + Pinion", ["mechanical", "rotating", "gear"], "Input shaft with pinion gear, keyway, seal journal, bearing seats"),
                part(3, "Intermediate Shaft + Gear Pair", ["mechanical", "rotating", "gear"], "Intermediate compound gear shaft with two gears, spacer, bearing seats"),
                part(4, "Output Shaft + Bull Gear", ["mechanical", "rotating", "gear"], "Output shaft with bull gear, output flange, keyway, bearing support"),
                part(5, "Bearing + Seal Set", ["mechanical", "sealing", "bearing_seal"], "Bearing cartridges, oil seals, shims, retainer plates"),
                part(6, "Lubrication + Breather System", ["mechanical", "fluid", "lubrication"], "Oil fill/drain/level plugs, splash baffle, breather cap, sight glass"),
                part(7, "Mounting Feet + Torque Arm", ["mechanical", "integration", "mount"], "Mount feet, torque arm boss, dowel pads, bolt groups"),
            ],
        },
        "subsystems": [
            ("gearbox_housing", "structures", "Split housing and bearing bores", ["bearing_bore", "gasket_flange", "rib", "inspection_cover", "dowel_pad"]),
            ("gear_train", "rotating", "Input/intermediate/output gear mesh", ["input_pinion", "compound_gear", "bull_gear", "mesh_centerline", "spacer"]),
            ("shaft_bearing_support", "rotating", "Shaft journals and bearing seats", ["shaft_journal", "bearing_seat", "retainer_plate", "shim_stack", "output_flange"]),
            ("sealing_lubrication", "sealing", "Oil seals, plugs, baffles, breather", ["oil_seal", "fill_plug", "drain_plug", "sight_glass", "breather_cap"]),
            ("mounting_service", "integration", "Mounting and access", ["mounting_foot", "torque_arm_boss", "bolt_group", "service_cover", "alignment_datum"]),
        ],
    },
    "underwater_sealed_sensor_housing": {
        "vehicle": {
            "id": "underwater_sealed_sensor_housing",
            "label": "Underwater Sealed Sensor Housing",
            "wikiTitle": "Underwater acoustics",
            "desc": "Underwater sensor housing concept for pressure shell, O-ring cap, cable gland, optical/acoustic window, mounting cradle, and service boundary grammar",
            "material": "Al 6061 + acrylic window + elastomer seals + stainless hardware",
            "process": "CNC + FDM fixture reference",
            "mass": "~4kg",
            "envelope": "320x180x180 mm",
            "parts": [
                part(1, "Cylindrical Pressure Shell", ["marine", "structure", "pressure_shell"], "Cylindrical housing shell with wall-thickness cue, internal rail slots, external cradle pads"),
                part(2, "Front Sensor Window Cap", ["marine", "sealing", "window_cap"], "Front cap with optical/acoustic window, O-ring groove, retaining ring, anti-rotation pins"),
                part(3, "Rear Service Cap", ["marine", "sealing", "service_cap"], "Rear cap with double O-ring cue, service screws, puller holes, orientation mark"),
                part(4, "Cable Gland + Strain Relief", ["marine", "electronics", "cable_gland"], "Wet-mate cable gland reference structure, bend relief boot, potting pocket, connector key"),
                part(5, "Internal Electronics Tray", ["electronics", "sensor", "tray"], "Slide-in board tray, sensor board standoffs, desiccant pocket, ground lug"),
                part(6, "Mounting Cradle + Anode Pad", ["marine", "integration", "cradle"], "ROV/vehicle cradle with clamp bands, sacrificial anode pad, drain path, lifting tab"),
                part(7, "Leak Test Port + Label Set", ["marine", "fluid", "test_port"], "Leak test plug, pressure label, inspection witness groove, serial plate"),
            ],
        },
        "subsystems": [
            ("pressure_shell", "structures", "Sealed cylinder and internal support", ["cylindrical_shell", "wall_thickness_cue", "internal_rail", "external_cradle_pad", "datum_mark"]),
            ("window_and_caps", "sealing", "Front/rear caps and O-ring boundaries", ["sensor_window", "o_ring_groove", "retaining_ring", "service_screw", "puller_hole"]),
            ("cable_penetration", "electronics", "Cable gland and strain relief", ["cable_gland", "bend_relief", "potting_pocket", "connector_key", "strain_relief"]),
            ("internal_sensor_tray", "electronics", "Slide-in electronics and sensor tray", ["board_tray", "standoff", "desiccant_pocket", "ground_lug", "slide_rail"]),
            ("marine_mount_service", "integration", "Cradle, anode, leak test, labels", ["clamp_band", "anode_pad", "drain_path", "leak_test_port", "serial_plate"]),
        ],
    },
    "liquid_rocket_engine_academic": {
        "vehicle": {
            "id": "liquid_rocket_engine_academic",
            "label": "Academic Liquid Rocket Engine System",
            "wikiTitle": "Liquid-propellant rocket",
            "desc": "Academic liquid rocket propulsion system seed for conceptual chamber/nozzle, injector taxonomy, regenerative cooling, feed-system architecture, turbomachinery, instrumentation, controls, and mount/load-path grammar; non-buildable and non-operational",
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
        },
        "subsystems": [
            ("chamber_heat_transfer", "thermal", "Combustion chamber heat-transfer and structural jacket study", ["liner_zone", "jacket_zone", "heat_transfer_label", "sensor_boss", "flange_datum"]),
            ("injector_architecture", "fluid", "Injector taxonomy and manifold-zone study without buildable orifice details", ["injector_family_label", "blocked_orifice_detail", "manifold_zone", "face_datum", "mixing_concept_label"]),
            ("nozzle_expansion_study", "structures", "Nozzle contour, throat/exit station, and thermal/structural callout study", ["throat_station_label", "exit_station_label", "contour_section", "cutaway_window", "thermal_callout"]),
            ("regenerative_cooling_study", "thermal", "Regenerative cooling route vocabulary and leak/service boundary", ["cooling_channel_route", "inlet_interface_label", "outlet_interface_label", "leak_inspection_path", "service_cover"]),
            ("feed_system_architecture", "fluid", "Conceptual feed-system topology and valve/check/filter placeholders", ["oxidizer_path_label", "fuel_path_label", "valve_placeholder", "filter_placeholder", "isolation_zone"]),
            ("turbomachinery_energy_path", "rotating", "Pump/turbine/shaft/bearing energy-path study without performance sizing", ["pump_region", "turbine_region", "shaft_axis", "bearing_region", "energy_path_arrow"]),
            ("instrumentation_controls", "electronics", "Instrumentation, DAQ, interlock, and harness vocabulary", ["sensor_boss", "daq_connector", "harness_channel", "interlock_label", "calibration_label"]),
            ("thrust_frame_integration", "integration", "Academic load path, mount datums, and cutaway boundary", ["thrust_frame", "trunnion_pad", "load_path_arrow", "datum_pad", "non_buildable_boundary_label"]),
        ],
        "boundary_note": "Academic liquid rocket propulsion study only. Do not generate buildable engine dimensions, propellant handling or ignition procedures, chamber pressure/thrust sizing, injector hole sizing, turbopump performance, test-stand operating steps, or flight-use instructions.",
    },
}


REFERENCE_TARGETS = {
    "inline_6_engine_gasoline": [
        {
            "label": "Wikipedia Straight-six engine",
            "url": "https://en.wikipedia.org/wiki/Straight-six_engine",
            "license_hint": "CC BY-SA text/images where applicable; verify media and CAD separately.",
            "why": "General inline-six architecture vocabulary and external layout references.",
        },
        {
            "label": "GrabCAD inline-six / engine block search",
            "url": "https://grabcad.com/library?query=inline%206%20engine",
            "license_hint": "Verify each model license before use; default reference-only.",
            "why": "Potential CAD-like visual references for block, cranktrain, head, and accessory layout.",
        },
    ],
    "inline_6_engine_diesel": [
        {
            "label": "Wikipedia Diesel engine",
            "url": "https://en.wikipedia.org/wiki/Diesel_engine",
            "license_hint": "CC BY-SA text/images where applicable; verify media and CAD separately.",
            "why": "Diesel-specific architecture vocabulary: injector wells, common rail, turbo path, reinforced block.",
        },
        {
            "label": "GrabCAD diesel engine / inline six search",
            "url": "https://grabcad.com/library?query=diesel%20engine%20inline%206",
            "license_hint": "Verify each model license before use; default reference-only.",
            "why": "Potential CAD-like visual references for diesel block/head/common-rail/turbo layouts.",
        },
    ],
    "centrifugal_pump": [
        {
            "label": "NIST / public pump reference search",
            "url": "https://www.nist.gov/",
            "license_hint": "Verify each asset.",
            "why": "Public technical references for pump components and inspection vocabulary.",
        },
        {
            "label": "GrabCAD centrifugal pump search",
            "url": "https://grabcad.com/library?query=centrifugal%20pump",
            "license_hint": "Verify each model license before use; default reference-only.",
            "why": "Volute, impeller, bearing frame, and flange CAD references.",
        },
    ],
    "hydraulic_manifold": [
        {
            "label": "GrabCAD hydraulic manifold search",
            "url": "https://grabcad.com/library?query=hydraulic%20manifold",
            "license_hint": "Verify each model license before use; default reference-only.",
            "why": "Manifold block porting, cartridge valve, plug, and label layout references.",
        }
    ],
    "battery_pack_module": [
        {
            "label": "NREL battery thermal management publications",
            "url": "https://www.nrel.gov/transportation/battery-thermal-management.html",
            "license_hint": "Verify publication/media terms.",
            "why": "Battery thermal, module, and safety vocabulary for non-live concept generation.",
        },
        {
            "label": "GrabCAD battery module search",
            "url": "https://grabcad.com/library?query=battery%20module",
            "license_hint": "Verify each model license before use; default reference-only.",
            "why": "Cell holders, busbar covers, BMS pockets, enclosures, and connector references.",
        },
    ],
    "liquid_cold_plate": [
        {
            "label": "GrabCAD liquid cold plate search",
            "url": "https://grabcad.com/library?query=liquid%20cold%20plate",
            "license_hint": "Verify each model license before use; default reference-only.",
            "why": "Serpentine channels, manifolds, gasket tracks, and mounting pad references.",
        }
    ],
    "cnc_axis_carriage": [
        {
            "label": "OpenBuilds linear motion documentation",
            "url": "https://openbuilds.com/",
            "license_hint": "Verify product/CAD terms; reference-only until reviewed.",
            "why": "Linear rail/carriage, actuator, motor mount, and sensor bracket vocabulary.",
        },
        {
            "label": "GrabCAD CNC linear axis search",
            "url": "https://grabcad.com/library?query=cnc%20linear%20axis",
            "license_hint": "Verify each model license before use; default reference-only.",
            "why": "Carriage plate, ball screw, linear rail, and cover references.",
        },
    ],
    "gearbox_reducer": [
        {
            "label": "GrabCAD gearbox reducer search",
            "url": "https://grabcad.com/library?query=gearbox%20reducer",
            "license_hint": "Verify each model license before use; default reference-only.",
            "why": "Housing, gear train, shaft, bearing, seal, and lubrication references.",
        }
    ],
    "underwater_sealed_sensor_housing": [
        {
            "label": "Blue Robotics documentation",
            "url": "https://bluerobotics.com/learn/",
            "license_hint": "Verify documentation/CAD terms; reference-only until reviewed.",
            "why": "Underwater enclosure, cable gland, O-ring, thruster/sensor mounting vocabulary.",
        },
        {
            "label": "GrabCAD underwater housing search",
            "url": "https://grabcad.com/library?query=underwater%20housing",
            "license_hint": "Verify each model license before use; default reference-only.",
            "why": "Sealed pressure shell, end cap, cable gland, and cradle references.",
        },
    ],
    "liquid_rocket_engine_academic": [
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
        }
    ],
}


def pack_tokens(text: str) -> list[str]:
    return [w for w in text.lower().replace("_", " ").replace("/", " ").split() if len(w) >= 3]


def micro_pack(seed: str, sub: tuple[str, str, str, list[str]], boundary_note: str | None = None) -> dict[str, Any]:
    sid, discipline, function, evidence = sub
    criteria = deepcopy(COMMON_CRITERIA)
    criteria.append(
        {
            "id": f"{sid}_domain_grammar",
            "criteria": [
                {
                    "criterion": "domain_evidence_features",
                    "good": f"Uses subsystem-specific evidence features: {', '.join(evidence)}.",
                    "bad": f"Omits the visible grammar for {sid} and substitutes generic blocks.",
                },
                {
                    "criterion": "service_or_boundary_visible",
                    "good": "Includes service, inspection, sealing, datum, or safety-boundary evidence where relevant.",
                    "bad": "Claims a functional subsystem without access, datums, labels, or boundary constraints.",
                },
            ],
        }
    )
    pack = {
        "schema": "blueprint_micro_pack_v1",
        "seed": seed,
        "subsystem": {
            "id": sid,
            "discipline": discipline,
            "function": function,
            "evidence_features": evidence,
        },
        "criteria": criteria,
    }
    if boundary_note:
        pack["boundary_note"] = boundary_note
    return pack


def skeleton(seed: str, spec: dict[str, Any]) -> dict[str, Any]:
    required = [
        {
            "id": sid,
            "discipline": discipline,
            "function": function,
            "evidence_features": evidence,
            "criteria_refs": ["geometry_grounding", "assembly_integration", f"{sid}_domain_grammar"],
        }
        for sid, discipline, function, evidence in spec["subsystems"]
    ]
    return {
        "schema": "blueprint_skeleton_pack_v1",
        "seed": seed,
        "pass": "PASS-0",
        "instruction": "Lay out one top-level node per required_subsystem, global datums, envelope, and stub interfaces. No detailed geometry in PASS-0.",
        "disciplines": COMMON_DISCIPLINES,
        "required_subsystems": required,
        "completeness_rule": "Every required_subsystem must appear in part_tree with at least one evidence_feature in geometry_ops; missing subsystem coverage is a scorecard failure, not style.",
        "global_judgment_summary": COMMON_CRITERIA,
        "connection_taxonomy": {
            "rule": "Name each inter-part interface with connection type + DOF + numeric clearance.",
            "dof_codes": "0=fixed, 1R=revolute, 1T=prismatic, 1R1T=cylindrical, 3R=spherical",
            "families": {
                "fastened": ["bolted_through(0)", "threaded_insert(0)", "retainer_plate(0)"],
                "rotating": ["bearing_seat(1R)", "shaft_coupling(1R)", "gear_mesh(1R)"],
                "fluid": ["flanged_gasket(0)", "threaded_port(0)", "hose_barb(0)", "gland_seal(0)"],
                "electrical": ["keyed_connector(0)", "service_disconnect(0)", "ground_lug(0)"],
                "service": ["sliding_tray(1T)", "inspection_cover(0)", "cartridge_retainer(0)"],
            },
        },
        "boundary_note": spec.get("boundary_note"),
    }


def update_seed_vehicles() -> None:
    vehicles = json.loads(VEHICLES_FILE.read_text(encoding="utf-8"))
    vehicles.setdefault("_note", "Evolution and engineering-expansion seed vehicle BOMs used by generate_batch.py.")
    for seed, spec in SEEDS.items():
        vehicles[seed] = spec["vehicle"]
    VEHICLES_FILE.write_text(json.dumps(vehicles, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_packs() -> None:
    for seed, spec in SEEDS.items():
        out_dir = PACKS / seed
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "skeleton.json").write_text(
            json.dumps(skeleton(seed, spec), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        boundary = spec.get("boundary_note")
        for sub in spec["subsystems"]:
            sid = sub[0]
            (out_dir / f"{sid}.json").write_text(
                json.dumps(micro_pack(seed, sub, boundary), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )


def update_reference_targets() -> None:
    targets = json.loads(TARGETS_FILE.read_text(encoding="utf-8"))
    target_map = targets.setdefault("targets", {})
    for seed, seed_targets in REFERENCE_TARGETS.items():
        existing = {t.get("label") for t in target_map.get(seed, [])}
        merged = list(target_map.get(seed, []))
        for target in seed_targets:
            if target.get("label") not in existing:
                merged.append(target)
        target_map[seed] = merged
    TARGETS_FILE.write_text(json.dumps(targets, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    update_seed_vehicles()
    write_packs()
    update_reference_targets()
    print(f"[engineering-expansion] seeds: {len(SEEDS)}")
    print(f"[engineering-expansion] vehicles -> {VEHICLES_FILE}")
    print(f"[engineering-expansion] packs -> {PACKS}")
    print(f"[engineering-expansion] reference targets -> {TARGETS_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
