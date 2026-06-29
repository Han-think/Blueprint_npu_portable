# Reference Feature Cards

Prompt-safe summaries generated from `_reference_quality_audit.json`.

## battery_pack_module

- status: watch
- assets: 8
- license gate: blocked_until_license_review
- design grammar:
  - battery module decomposition: cell carrier, busbar cover, BMS bay, cooling plate, enclosure, disconnect
  - thermal/electrical separation grammar: thermal pad zones, sense-wire channels, EMI shield, terminal guards
  - safety/service grammar: gasketed lid, vent path, service disconnect, warning labels, no-live-energy boundary
- missing reference needs:
  - permissive battery module/cold-plate/enclosure references are needed before training promotion
  - do not generate live-energy assembly instructions or claim pack safety certification
- selected assets:
  - 20_dataset/reference_assets/battery_pack_module/cad/printed__pcb_mount.scad (reference_only, design 63)

## centrifugal_pump

- status: needs_reference_crawl
- assets: 0
- license gate: blocked_until_license_review
- design grammar:
  - volute/impeller/shaft/bearing/seal/flange decomposition for rotating fluid machinery
  - pressure-boundary grammar: inlet eye, outlet flange, gasket faces, drain/vent plugs, inspection bosses
  - back-pull-out service grammar: seal cartridge, bearing housing, coupling guard, baseplate alignment
- missing reference needs:
  - pump cross-section/CAD references with clear volute and seal cartridge structure are needed
  - scorecard should penalize pumps with no flow path or serviceable seal/bearing access
- selected assets:

## cnc_axis_carriage

- status: watch
- assets: 29
- license gate: blocked_until_license_review
- design grammar:
  - precision axis decomposition: carriage plate, rails, bearing blocks, ball screw, motor mount, sensors
  - datum/tolerance grammar: dowel holes, rail reference edge, preload notes, adjustment slots
  - protection/service grammar: way covers, wipers, lubrication manifold, cable channels, grease ports
- missing reference needs:
  - licensed linear axis/ball screw/rail assembly CAD references are needed
  - scorecard should penalize axis designs without rail datums, screw support, or sensor/lube access
- selected assets:
  - 20_dataset/reference_assets/cnc_axis_carriage/cad/vitamins__bearing_block.scad (license_review_then_promote, design 70)
  - 20_dataset/reference_assets/cnc_axis_carriage/cad/vitamins__gear_motor.scad (reference_only, design 67)
  - 20_dataset/reference_assets/cnc_axis_carriage/cad/vitamins__rail.scad (reference_only, design 67)
  - 20_dataset/reference_assets/cnc_axis_carriage/cad/printed__pcb_mount.scad (reference_only, design 66)
  - 20_dataset/reference_assets/cnc_axis_carriage/cad/vitamins__sbr_rail.scad (reference_only, design 65)
  - 20_dataset/reference_assets/cnc_axis_carriage/cad/printed__carriers.scad (reference_only, design 64)
  - 20_dataset/reference_assets/cnc_axis_carriage/cad/printed__drag_chain.scad (reference_only, design 64)
  - 20_dataset/reference_assets/cnc_axis_carriage/cad/printed__printed_pulleys.scad (reference_only, design 64)

## cubesat

- status: watch
- assets: 32
- license gate: blocked_until_license_review
- design grammar:
  - 3U/1U frame segmentation into top/mid/bottom structural shells
  - print-prepped rail, corner, and skeletonized frame cues
  - STEP-to-STL traceability for printable structure variants
- missing reference needs:
  - EPS, CDH, solar panel, thermal strap, and harness spine references are still needed
  - assembly card should force board stack and service access, not just frame shell
- selected assets:

## gearbox_reducer

- status: watch
- assets: 7
- license gate: blocked_until_license_review
- design grammar:
  - gearbox decomposition: split housing, input/intermediate/output shafts, gear mesh, bearings, seals
  - lubrication/service grammar: fill/drain/level plugs, breather, sight glass, inspection cover
  - precision support grammar: bearing bores, shims, retainer plates, dowel pads, mesh centerline
- missing reference needs:
  - permissive reducer cutaway/CAD references with shaft/bearing/gear layout are needed
  - do not claim torque rating or gear life without real sizing analysis
- selected assets:

## haptic_glove

- status: watch
- assets: 72
- license gate: blocked_until_license_review
- design grammar:
  - finger linkage families: base, bend segments, split links, thumb MCP and distal parts
  - palm/base plate and modular hand-link decomposition
  - printable mesh density for wearable mechanism study references
- missing reference needs:
  - URDF/joint ordering or assembly docs should be mapped before training promotion
  - separate actual glove mechanism parts from generic robotic hand meshes
- selected assets:
  - 20_dataset/reference_assets/haptic_glove/cad/hand_meshes__inspire_hand__meshes__base_link.STL (reference_only, design 65)
  - 20_dataset/reference_assets/haptic_glove/cad/hand_meshes__inspire_hand__meshes__hand_base_link.STL (reference_only, design 65)
  - 20_dataset/reference_assets/haptic_glove/cad/hand_meshes__wonik_allegro__assets__base_link_left.stl (reference_only, design 65)
  - 20_dataset/reference_assets/haptic_glove/cad/DOGlove_meshes__base_link.STL (reference_only, design 62)
  - 20_dataset/reference_assets/haptic_glove/cad/DOGlove_meshes__ring_split.STL (reference_only, design 62)
  - 20_dataset/reference_assets/haptic_glove/cad/DOGlove_meshes__thumb_split.STL (reference_only, design 62)
  - 20_dataset/reference_assets/haptic_glove/cad/hand_meshes__inspire_hand__meshes__Link12.STL (reference_only, design 62)
  - 20_dataset/reference_assets/haptic_glove/cad/hand_meshes__inspire_hand__meshes__Link13.STL (reference_only, design 62)

## hydraulic_manifold

- status: watch
- assets: 9
- license gate: blocked_until_license_review
- design grammar:
  - CNC manifold block grammar: P/T/A/B ports, cross-drilled galleries, plug bosses, datum faces
  - cartridge valve cavities with O-ring lands, wrench clearance, flow arrows, and labels
  - instrumentation and test access: pressure sensor boss, test port, protective cover, label plate
- missing reference needs:
  - licensed manifold drawings/CAD with visible port maps and valve cavities are needed
  - avoid implying rated pressure certification; use conceptual routing and inspection vocabulary
- selected assets:

## inline_6_engine_diesel

- status: needs_reference_crawl
- assets: 0
- license gate: blocked_until_license_review
- design grammar:
  - diesel inline-six reinforcement grammar: thick deck, bearing ladder, cross-bolt bosses, heavy cranktrain
  - diesel-specific layout: injector wells, common rail, return path, turbo/exhaust heat shield, oil cooler
  - service access for timing gear housing, filters, injectors, lifting/mounting datums
- missing reference needs:
  - licensed diesel engine cutaway and common-rail layout references should be reviewed
  - do not promote performance, emissions, injection calibration, or certified engine claims
- selected assets:

## inline_6_engine_gasoline

- status: needs_reference_crawl
- assets: 0
- license gate: blocked_until_license_review
- design grammar:
  - inline-six segmentation: block, crankcase, head, cranktrain, manifolds, timing cover, oil pan
  - gasoline-specific grammar: spark plug wells, fuel rail, injector pockets, throttle/intake plenum
  - serviceable cutaway features: gasket faces, coolant jacket cues, oil galleries, accessory brackets
- missing reference needs:
  - permissive engine cutaway/CAD references for block/head/cranktrain are needed
  - keep output at conceptual/educational assembly grammar; no certified running-engine claim
- selected assets:

## liquid_cold_plate

- status: needs_reference_crawl
- assets: 0
- license gate: blocked_until_license_review
- design grammar:
  - cold plate channel grammar: serpentine path, fin islands, inlet/outlet manifold, thermal pad zones
  - seal/leak grammar: gasket groove, compression stops, leak witness channel, drain/bleed/test ports
  - power-device mounting grammar: flatness datum, isolation washer pockets, torque marks, service labels
- missing reference needs:
  - channel/cap/gasket CAD or drawings should be collected for geometry fidelity
  - avoid rated pressure/thermal-performance claims until external analysis exists
- selected assets:

## liquid_rocket_engine_academic

- status: needs_reference_crawl
- assets: 0
- license gate: blocked_until_license_review
- design grammar:
  - academic liquid-engine subsystem grammar: chamber heat transfer, nozzle expansion study, injector taxonomy, regenerative cooling
  - feed-system and turbomachinery architecture vocabulary without buildable sizing or operating procedures
  - instrumentation, DAQ, interlock, thrust-frame load path, and non-buildable boundary annotation
- missing reference needs:
  - collect safe academic NASA/NTRS or textbook-like references for subsystem decomposition and terminology
  - avoid buildable engine dimensions, propellant handling, ignition/start procedures, thrust/chamber-pressure sizing, injector hole sizing, turbopump performance, test-stand operating steps, or flight-use instructions
  - use references as conceptual architecture and validation vocabulary only until legal/safety review
- selected assets:

## long_range_recon_wing

- status: watch
- assets: 12
- license gate: blocked_until_license_review
- design grammar:
  - OpenVSP wing/prop/aircraft parametric geometry grammar
  - planform, wing station, rotor/prop, and fuselage reference vocabulary
  - aircraft geometry can guide station-based CAD-like generation
- missing reference needs:
  - specific UAV/flying-wing center pod, payload bay, battery bay, and cutaway references
  - 2D top/side/front drawings with rib/spar/bay labels
- selected assets:

## robot_arm

- status: watch
- assets: 64
- license gate: blocked_until_license_review
- design grammar:
  - serial arm link naming and proportions: base, shoulder, upperarm, forearm, wrist
  - collision mesh families for UR-style industrial arms
  - joint-link segmentation useful for assembly grammar
- missing reference needs:
  - license must be resolved before training use
  - visual meshes/URDF/joint metadata are needed; collision STLs alone are incomplete
  - one permissively licensed STEP/URDF source should be added
- selected assets:

## small_launch_vehicle

- status: watch
- assets: 31
- license gate: blocked_until_license_review
- design grammar:
  - OpenSCAD parametric rocket study components: assembly, fins, rings, main body
  - printable STL/SCAD relationship for academic non-operational rocket cutaway references
  - module separation between shell, nose/fins/rings/controller cap
- missing reference needs:
  - keep explicit academic non-operational boundary
  - avoid propulsion/performance instructions; use only shape, subsystem, and inspection grammar
  - add cutaway/avionics/recovery bay references if available
- selected assets:
  - 20_dataset/reference_assets/small_launch_vehicle/cad/ROCKET__STL__ASSEMBLY.stl (reference_only, design 63)

## tiltrotor

- status: watch
- assets: 12
- license gate: blocked_until_license_review
- design grammar:
  - OpenVSP prop/rotor/wing geometry grammar
  - wing plus propulsion axis decomposition
  - parametric aircraft references for silhouette and station placement
- missing reference needs:
  - tilting nacelle, tilt-axis bearing, servo linkage, and slack-loop harness reference
  - VTOL-specific assembly/cutaway drawing source
- selected assets:

## underwater_sealed_sensor_housing

- status: watch
- assets: 12
- license gate: blocked_until_license_review
- design grammar:
  - sealed marine enclosure grammar: pressure shell, end caps, O-ring grooves, cable gland, service cap
  - payload integration grammar: sensor window, internal tray, desiccant pocket, ground lug, slide rails
  - marine service grammar: leak test port, clamp cradle, drain path, anode pad, serial/pressure labels
- missing reference needs:
  - licensed underwater enclosure/cable gland/O-ring cap references are needed
  - avoid depth rating or pressure certification claims without analysis
- selected assets:
  - 20_dataset/reference_assets/underwater_sealed_sensor_housing/cad/printed__box_assembly.scad (license_review_then_promote, design 70)
  - 20_dataset/reference_assets/underwater_sealed_sensor_housing/cad/printed__box.scad (reference_only, design 67)
  - 20_dataset/reference_assets/underwater_sealed_sensor_housing/cad/printed__butt_box.scad (reference_only, design 67)
  - 20_dataset/reference_assets/underwater_sealed_sensor_housing/cad/printed__cable_grommets.scad (reference_only, design 67)
  - 20_dataset/reference_assets/underwater_sealed_sensor_housing/cad/printed__camera_housing.scad (reference_only, design 67)
  - 20_dataset/reference_assets/underwater_sealed_sensor_housing/cad/printed__printed_box.scad (reference_only, design 67)
  - 20_dataset/reference_assets/underwater_sealed_sensor_housing/cad/printed__socket_box.scad (reference_only, design 67)
  - 20_dataset/reference_assets/underwater_sealed_sensor_housing/cad/utils__tube.scad (reference_only, design 67)
