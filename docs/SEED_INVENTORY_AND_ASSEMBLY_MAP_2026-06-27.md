# Seed Inventory and Assembly Map

This document lists the current seed set, what is inside each seed, how its assembly should be positioned, and what reference CAD/crawl work remains.

## Summary

| Group | Seed | Parts | Subsystems | Reference Status | Assets |
| --- | --- | ---: | ---: | --- | ---: |
| Original Evolution Seeds | `cubesat` | 12 | 10 | watch | 32 |
| Original Evolution Seeds | `haptic_glove` | 12 | 7 | watch | 72 |
| Original Evolution Seeds | `long_range_recon_wing` | 9 | 8 | watch | 12 |
| Original Evolution Seeds | `tiltrotor` | 9 | 8 | watch | 12 |
| Original Evolution Seeds | `robot_arm` | 12 | 8 | watch | 64 |
| Original Evolution Seeds | `small_launch_vehicle` | 13 | 7 | watch | 31 |
| Engineering Expansion Seeds | `inline_6_engine_gasoline` | 10 | 7 | needs_reference_crawl | 0 |
| Engineering Expansion Seeds | `inline_6_engine_diesel` | 10 | 7 | needs_reference_crawl | 0 |
| Engineering Expansion Seeds | `centrifugal_pump` | 8 | 5 | needs_reference_crawl | 0 |
| Engineering Expansion Seeds | `hydraulic_manifold` | 6 | 5 | watch | 9 |
| Engineering Expansion Seeds | `battery_pack_module` | 7 | 5 | watch | 8 |
| Engineering Expansion Seeds | `liquid_cold_plate` | 6 | 5 | needs_reference_crawl | 0 |
| Engineering Expansion Seeds | `cnc_axis_carriage` | 7 | 5 | watch | 29 |
| Engineering Expansion Seeds | `gearbox_reducer` | 7 | 5 | watch | 7 |
| Engineering Expansion Seeds | `underwater_sealed_sensor_housing` | 7 | 5 | watch | 12 |
| Engineering Expansion Seeds | `liquid_rocket_engine_academic` | 10 | 8 | needs_reference_crawl | 0 |

## Assembly Map Rules

- Every seed should define a primary datum/axis, a service side, and at least three adjacent interfaces.
- Every BOM part should map to one subsystem grammar or declare why it crosses multiple subsystems.
- Every subsystem should expose evidence features in `part_tree`, `geometry_ops`, and assembly/disassembly notes.
- Reference CAD is used as grammar and validation vocabulary only until license review promotes it.
- Safety-boundary seeds stay academic, non-operational, and non-buildable unless real engineering analysis and legal review exist.

# Original Evolution Seeds

## cubesat

- label: 3U CubeSat
- domain: 3U CubeSat (10x10x30cm) Earth-observation demonstrator
- material/process: Al 7075 + CFRP + FR4 / CNC + PCB
- envelope/mass: 100x100x340.5 mm / <4 kg
- reference status: watch · assets 32
- assembly position hint: Use Z as 3U stack axis; PC/104 boards and harness spine run along the body, deployables attach to side faces.

### BOM Parts
- `p1` Primary Structure (3U): 3U CubeSat primary frame, Al 7075, PC/104 standoffs, deployable rail guide grooves (CDS spec)
- `p2` Solar Panel x 4 (deploy): Deployable solar panel wing, 3U size, spring-loaded hinge, burn-wire release, deployment damper
- `p3` Antenna Deployer x 2: Tape-spring UHF/S-band antenna deployer, stowed flat, burn-wire release, latching tab
- `p4` Reaction Wheel x 3: Small reaction wheel assembly, brushless motor, momentum 0.005-0.05 Nms, isolation mount
- `p5` Star Tracker Mount: Star tracker optical bench mount, CTE-matched, baffled sun shield, line-of-sight +-1deg
- `p6` Payload Optics Bench: EO payload optics bench, thermal stability, optical baffles, focal plane interface, lens mounts
- `p7` Cold Gas Thruster x 4: Cold gas propulsion thruster bracket, 4 thrusters cross-pattern, 50mN class, plumbing manifold
- `p8` Separation Spring Plate: P-POD or ISIPOD separation interface plate, spring pusher contact, kill switch arm
- `p9` EPS Solar Charging Module: EPS solar charging subsystem: solar_panel_face inputs, removable battery_tray, eps_board_slot, power_connector keying, service cover...
- `p10` CDH Avionics Stack: Command/data handling avionics stack: obc_board, stack_harness, debug_port_access, board standoffs, connector labels, grounding poin...
- `p11` Thermal Path / Radiator Strap Evidence: Thermal_path closure module: radiator_face, thermal_strap_note, vent_hole, battery-to-frame conduction pad, service-visible thermal...
- `p12` Integration Harness + Datum Spine: Integration_harness closure spine with harness_channel, connector_keying, assembly_datum pads, routing clips, service hatch, recipro...

### Subsystem Grammar
- `structure_rails` (structures): 3U frame, deployer rails, board stack support | evidence: rail, standoff, PC/104 stack, corner_post
- `eps_solar_charging` (power): Solar panel reference articles, battery tray, charge/distribution board | evidence: solar_panel_face, battery_tray, eps_board_slot, power_connector
- `comms_antenna` (comms): Antenna deployer (tape-spring reference article ok), radio board slot, RF connector path | evidence: antenna_slot, antenna_deployer, tape_spring, deploy_hinge, radio_board, rf_connector
- `adcs` (gnc): Attitude control evidence: reaction wheel/magnetorquer reference articles, star tracker mount, sun sensor windows | evidence: reaction_wheel_reference article, magnetorquer_rod, sensor_window, star_tracker_mount, baffle_shield
- `cdh_avionics` (electronics): On-board computer stack, harness between boards | evidence: obc_board, stack_harness, debug_port_access
- `thermal_path` (thermal): Radiator face or thermal strap note from battery/OBC to structure | evidence: radiator_face, thermal_strap_note, vent_hole
- `payload_bay` (payload): Removable payload module: optics bench, focal plane, thermal baffles, inspection window | evidence: payload_tray, inspection_window, optics_bench, focal_plane, lens_mount
- `deployment_mechs` (recovery_deployment): Antenna/panel deployment hinges, separation spring plate, pod pusher contacts, release reference articles (study-level) | evidence: deploy_hinge, release_pin_reference article, burn_wire_note, separation_spring_plate, pusher_contact, kill_switch_arm
- `propulsion_study` (actuation): Cold gas thruster bracket reference articles and plumbing manifold study reference (academic non-operational) | evidence: thruster_bracket, cold_gas_nozzle_reference article, plumbing_manifold, cross_pattern_mount
- `integration_harness` (integration): Inter-board harness routing, connectors, assembly datums, connection types and load-path closure | evidence: harness_channel, connector_keying, assembly_datum

### Reference Grammar
- learn: 3U/1U frame segmentation into top/mid/bottom structural shells
- learn: print-prepped rail, corner, and skeletonized frame cues
- learn: STEP-to-STL traceability for printable structure variants
- need: EPS, CDH, solar panel, thermal strap, and harness spine references are still needed
- need: assembly card should force board stack and service access, not just frame shell

### Crawl / CAD Priorities
- 3U frame STEP with rails/standoffs
- solar deploy panel hinge CAD/drawing
- EPS/battery/PC104 stack layout
- harness spine/service cover reference

### Current Source Targets
- HeliosCube-Eleni Arduino Project Hub: Open-source CubeSat educational structure, electronics stack, sensors, assembly/BOM references.
- NASA 3D Resources: Satellite/spacecraft visual and 3D reference.

## haptic_glove

- label: Force-Feedback Haptic Glove Pair
- domain: Wearable force-feedback exo-glove pair for VR grasp resistance, serviceable actuator cartridges, linkages, wrist band, and dorsal control module
- material/process: PETG + TPU + PA12 / FDM + SLS
- envelope/mass: 220x200x60 mm / ~650g pair
- reference status: watch · assets 72
- assembly position hint: Use wrist-to-fingertip as the station axis; dorsal module at wrist/back-of-hand, finger cartridges repeat per finger.

### BOM Parts
- `p1` Dorsal Control Module x 2: Snap-in dorsal electronics and battery module, tool-less lid, wireless board bay, service label and cable exits
- `p2` Finger Exo Linkage Cartridge x 10: Two-segment exoskeleton finger linkage cartridge, single-pin removable, hinge datum pads, thimble slip interface
- `p3` Flexion-Resistance Actuator x 10: Plug-in tendon brake/clutch actuator module, knuckle row mount, cable pulley, connector pocket, service access
- `p4` Adjustable Wrist Band x 2: Quick-release wrist band, cable raceway, soft-contact interface, buckle, dorsal module anchor
- `p5` Cable Raceway + Harness Cover x 2: Snap-fit cable routing cover from wrist band to fingers, strain relief slots, inspection windows
- `p6` Finger Thimble Interface Set: Replaceable fingertip thimbles, slip-clearance sockets, soft liner cue, per-finger label and hinge pin access
- `p7` Palm Sensor Plate x 2: Palm-side flex/bend sensor channel plate, IMU mount pad, per-finger sensor channel exits, sensor connector pocket, washable liner in...
- `p8` Battery + Power Module x 2: Wrist battery pocket with quick-swap door, li-ion pack 2S 18650, BMS access window, power connector keying, charge LED window
- `p9` Wiring Loom + Service Loop Set: Knuckle-crossing wiring loom with service loops, strain relief at every flex boundary, flex-rated bend radius, power vs signal chann...
- `p10` Knuckle Mount Rail x 2: Dorsal knuckle row mounting rail, actuator plug-in pockets, datum pads per finger station, fastener pattern and removal path
- `p11` Fit Calibration + Safety Release Set: Wearable_structure closure module: wrist_quick_release, soft_liner_zone, finger_clearance gauges, don/doff datum labels, emergency r...
- `p12` Service Port + Flex-Wiring Inspection Cover: Flex_wiring closure module: service_loop inspection cover, strain_relief, bend_radius_note, connector keying, charge/debug service p...

### Subsystem Grammar
- `finger_linkages` (mechanisms): Per-finger four-bar/tendon linkage cartridges, single-pin removable | evidence: finger_cartridge, hinge_pin, thimble_socket, linkage_bar
- `actuation_brakes` (actuation): Plug-in flexion-resistance actuator modules at knuckle row | evidence: actuator_module, plug_in_pocket, knuckle_mount
- `sensing` (gnc): Flex/bend sensor channels per finger, IMU mount on hand plate | evidence: sensor_channel, imu_mount, sensor_exit
- `electronics_hub` (electronics): Controller board on back-of-hand with standoffs and connector orientation | evidence: controller_board, standoff, connector_edge
- `power` (power): Battery pocket at wrist with quick-swap access | evidence: battery_pocket, swap_door, power_connector
- `wearable_structure` (human_factors): Hand plate, wrist band, quick release, soft-contact zones, finger clearance | evidence: wrist_quick_release, soft_liner_zone, finger_clearance
- `flex_wiring` (integration): Knuckle-crossing wiring with service loops and flex-rated bend radius; connection types and load-path closure | evidence: service_loop, strain_relief, bend_radius_note

### Reference Grammar
- learn: finger linkage families: base, bend segments, split links, thumb MCP and distal parts
- learn: palm/base plate and modular hand-link decomposition
- learn: printable mesh density for wearable mechanism study references
- need: URDF/joint ordering or assembly docs should be mapped before training promotion
- need: separate actual glove mechanism parts from generic robotic hand meshes

### Crawl / CAD Priorities
- URDF/joint-order docs
- finger linkage assembly CAD
- tendon/cable routing diagrams
- wearable fit/soft-contact reference

### Current Source Targets
- DOGlove project: Haptic force-feedback glove finger assembly, cable-driven mechanism, palm base, modular joints.
- CDF-Glove project: Cable-driven glove design reference for tendon routing and finger force feedback.

## long_range_recon_wing

- label: Long-Range Surveillance Wing
- domain: Fixed-wing flying-wing UAV, 2m wingspan, 4+ hour endurance
- material/process: EPP foam core + CFRP spar / FDM + foam
- envelope/mass: 2000x1100x220 mm / ~1.8kg
- reference status: watch · assets 12
- assembly position hint: Use X as fuselage/chord and Y as span; center pod at root, spars/ribs span outward, payload bays near centerline.

### BOM Parts
- `p1` Center Body Pod: Flying-wing center pod, equipment bay door, wing-spar reinforcement, motor pylon at rear
- `p2` Wing Spar (2-piece): 20mm CFRP main spar, 2-piece centerjoint, anti-rotation key, 800mm half-span each
- `p3` Wing Rib Set x 12: Wing rib NACA airfoil profile, lightening pockets, leading edge sock, trailing edge taper
- `p4` Elevon Servo Pocket x 2: Elevon servo pocket, MG90S or DS215MG, control horn linkage, removable access cover
- `p5` Motor + Pusher Prop Mount: Rear pusher 2814 BLDC mount, 10x7 folding prop clearance, thrust line +1deg down
- `p6` GPS + Pitot Boom: Nose boom 8mm, GPS at tip, pitot static port forward, BEC airflow shielded
- `p7` Camera Gimbal Bay: Forward downward camera gimbal bay 70mm deep, 2-axis micro gimbal, optical window
- `p8` Battery Bay (Slide): 4S 16000mAh Li-ion slide-in bay, CG adjust slot, top access hatch, balance lead window
- `p9` Integration Service Backbone: Wing/fuselage integration service backbone with assembly_datum pads, harness_raceway, service_hatch, connector_keying, anti-rotation...

### Subsystem Grammar
- `aero_surfaces` (structures): Wing planform, airfoil section evidence, winglets, elevon/control surface cutouts with hinges | evidence: airfoil_section, control_surface_cutout, hinge_line, winglet, elevon
- `primary_structure` (structures): Main spar, ribs, carry-through, fuselage frames; continuous load path | evidence: spar_socket, main_spar, anti_rotation_key, rib, carry_through, frame
- `propulsion_mount` (actuation): Motor pod / pusher prop mount reference article with bolt pattern and cooling path (non-operational) | evidence: motor_mount, bolt_circle, cooling_inlet, pusher_prop, motor_pod
- `power_battery` (power): Slide-in li-ion battery pack bay on CG rail, BMS and connector access | evidence: battery_bay, li_ion_pack, bms_access, xt60_connector, cg_rail_marks, power_connector
- `avionics_comms` (comms): GPS, pitot boom, receiver/telemetry boards, antenna routing away from power leads | evidence: avionics_tray, antenna_channel, signal_separation, gps_mount, pitot_boom, telemetry_board
- `recon_payload` (payload): Non-weapon camera/gimbal sensor pod bay with removable insert and window | evidence: sensor_bay, payload_insert, window, camera_pod, gimbal_mount
- `control_actuation` (mechanisms): Servo pockets, control horns, pushrod/linkage channels | evidence: servo_pocket, control_horn, pushrod_channel
- `integration_service` (integration): Wing/fuselage datums, harness raceways, hatch access, connection types and load-path closure | evidence: assembly_datum, harness_raceway, service_hatch

### Reference Grammar
- learn: OpenVSP wing/prop/aircraft parametric geometry grammar
- learn: planform, wing station, rotor/prop, and fuselage reference vocabulary
- learn: aircraft geometry can guide station-based CAD-like generation
- need: specific UAV/flying-wing center pod, payload bay, battery bay, and cutaway references
- need: 2D top/side/front drawings with rib/spar/bay labels

### Crawl / CAD Priorities
- 3-view/cutaway flying wing
- center pod payload bay CAD
- spar/rib/battery bay drawings
- servo/elevon linkage reference

### Current Source Targets
- OpenVSP Airshow: Aircraft .vsp3-style geometry references, useful for silhouette, stations, wing/nacelle/tail gram...
- OpenVSP: Parametric aircraft geometry and export workflow reference.

## tiltrotor

- label: Tiltrotor VTOL Hybrid
- domain: Fixed-wing VTOL with 2 tilting rotor nacelles, BVLOS long-range capable
- material/process: CFRP + Al + TPU / FDM + CNC
- envelope/mass: 1200x900x200 mm / ~2.5kg
- reference status: watch · assets 12
- assembly position hint: Use X fuselage, Y wing span, Z vertical; nacelles sit on wing stations with tilt-axis across nacelle/wing interface.

### BOM Parts
- `p1` Center Fuselage Spine: CFRP box beam center fuselage, avionics bay, wing spar socket, front GPS boom mount, belly camera window
- `p2` Main Wing (2-piece): Straight wing, 4S NACA 2412, dual 15mm CFRP spar, 900mm half-span, 160mm chord, 3-layer CFRP skin
- `p3` Nacelle Assembly x 2: Tilting nacelle assembly, 0-90deg tilt axis, 6309 bearing set, servo-driven worm gear, motor and ESC pocket
- `p4` Tilt Servo + Linkage x 2: 25kg-cm DS3218 servo per nacelle, titanium pushrod, dual ball joints, tilt range 0-93deg, crash-tolerant
- `p5` V-Tail x 2 (Ruddervator): +-35deg V-tail ruddervator pair, MG996R servo each, 30deg dihedral, CFRP sandwich panel, hinge piano wire
- `p6` Landing Gear (Tri): Tricycle landing gear, spring-steel skid arms, 55mm dia wheels, CG at 1/3 chord, 200mm wheelbase
- `p7` Battery Bay (Slide-In): Belly slide-in battery bay, 6S 8000mAh Li-ion pack, Velcro + strap dual retention, CG position 28% MAC
- `p8` Payload Nose Bay: Interchangeable nose payload bay, Day/IR camera gimbal or survey sensor, 80x60x50mm, 300g payload limit
- `p9` Tilt-Axis Harness + Datum Service Bay: Tiltrotor integration_service module with tilt-axis harness_channel, slack_loop, interface_datum, service_hatch, connector keying, a...

### Subsystem Grammar
- `tilt_mechanism` (mechanisms): Tilt axis with bearing seats, servo linkage, rotation clearance arc | evidence: tilt_axis, bearing_seat, servo_linkage, clearance_arc
- `nacelle_propulsion` (actuation): Motor pod with replaceable motor module and access cover | evidence: motor_module, access_cover, bolt_pattern
- `wing_structure` (structures): Wing spar carrying nacelle loads into fuselage spine; V-tail/ruddervator and landing gear attach structure | evidence: wing_spar, spar_socket, fuselage_spine, v_tail, ruddervator, stabilizer, landing_gear_mount, gear_leg
- `power_battery` (power): Slide-in li-ion battery pack bay with CG adjustment, BMS and connector access | evidence: battery_bay, li_ion_pack, bms_access, cg_marks, connector_access
- `flight_electronics` (electronics): Flight controller/autopilot tray, telemetry and VTX modules, motor power vs signal wire separation across tilt joint | evidence: controller_tray, flight_controller, autopilot_board, firmware_board, gps_module, barometer, servo_rail, telemetry_module
- `gnc_sensors` (gnc): IMU, pitot/airspeed sensor, GPS mount evidence near CG (reference structure level) | evidence: imu_mount, pitot_probe, airspeed_sensor, gps_mount, sensor_window
- `payload_nose_bay` (payload): Nose payload/sensor bay with removable insert and service window | evidence: payload_bay, nose_bay, sensor_insert, service_window
- `integration_service` (integration): Nacelle interface datums, harness routing through tilt axis, hatches, connection types and load-path closure | evidence: interface_datum, harness_channel, service_hatch

### Reference Grammar
- learn: OpenVSP prop/rotor/wing geometry grammar
- learn: wing plus propulsion axis decomposition
- learn: parametric aircraft references for silhouette and station placement
- need: tilting nacelle, tilt-axis bearing, servo linkage, and slack-loop harness reference
- need: VTOL-specific assembly/cutaway drawing source

### Crawl / CAD Priorities
- tilt nacelle axis CAD/cutaway
- servo linkage and bearing layout
- slack-loop harness around tilt axis
- wing/nacelle load-path drawing

### Current Source Targets
- OpenVSP Airshow: VTOL/tiltrotor/nacelle/wing geometry references when available.
- OpenVSP: Aircraft geometry construction and export workflow reference.

## robot_arm

- label: 6-DOF Industrial Arm
- domain: 6-DOF serial industrial robot arm, 5kg payload, 600mm reach
- material/process: Al 7075 + steel + composite / CNC + LPBF
- envelope/mass: 600mm reach max / ~25kg
- reference status: watch · assets 64
- assembly position hint: Use serial joint chain from base J1 to tool flange J6; each link owns its joint datum and cable pass-through.

### BOM Parts
- `p1` Base Joint (J1): Base rotary joint J1, +-180deg, harmonic drive, 100Nm peak torque, mounting flange ISO 9409
- `p2` Shoulder Joint (J2): Shoulder pitch joint J2, +-120deg, harmonic drive, 80Nm, cable routing through center bore
- `p3` Upper Arm (Link 2-3): Upper arm link, 300mm length, hollow tube with cable conduit, lightweight Al 7075
- `p4` Elbow Joint (J3): Elbow pitch joint J3, +-150deg, cycloidal reducer, 50Nm, encoder dual-stack
- `p5` Forearm + Wrist (J4): Forearm with wrist roll J4, 250mm length, +-360deg continuous, slip ring for power/signal
- `p6` Wrist Pitch (J5): Wrist pitch joint J5, +-120deg, harmonic drive, 20Nm, compact form factor
- `p7` Wrist Roll (J6): Wrist final roll joint J6, +-360deg, harmonic drive, 10Nm, ISO 9409-1 50mm tool flange
- `p8` Tool Flange + Changer: Tool changer master plate at J6 end, pneumatic locking, 4 utility ports
- `p9` Cable Management Spine: External cable carrier from base to wrist, drag chain or spiral, signal + power + pneumatic
- `p10` Replaceable Motor Module Set: Actuation_motors closure module: replaceable motor_module cartridges for J1-J6, fastener_access, coupling_reference article, insert/...
- `p11` Encoder Cover + Sensing Set: Sensing_encoders closure module: encoder_pocket and encoder_cover at each joint, index marks, cable exit strain relief, inspection l...
- `p12` Drive Electronics Bay: Drive_electronics bay with driver_bay, power_channel, signal_channel, ground_point, service cover, connector keying, thermal inspect...

### Subsystem Grammar
- `link_structure` (structures): Rigid links with load path from tool flange to base, ribs where needed | evidence: link_body, rib, base_flange
- `joint_transmission` (mechanisms): J1-J6 joint cartridges: bearing seats, reducer reference articles, wrist pitch/roll axes, shaft location | evidence: bearing_seat, reducer_reference article, shoulder, wrist_pitch_axis, wrist_roll_axis, retaining_feature
- `actuation_motors` (actuation): Replaceable motor modules per joint with fastener access | evidence: motor_module, fastener_access, coupling_reference article
- `sensing_encoders` (gnc): Encoder pockets and covers at each joint | evidence: encoder_pocket, encoder_cover
- `drive_electronics` (electronics): Driver board bay, power/signal separation along the arm | evidence: driver_bay, power_channel, signal_channel, ground_point
- `cable_spine` (integration): External or inspectable harness spine with slack loops at every joint; connection types and load-path closure | evidence: cable_spine, slack_loop, strain_relief, clip
- `end_effector_interface` (payload): Tool flange with standard bolt pattern and locating boss | evidence: tool_flange, bolt_pattern, locating_boss
- `base_mounting` (structures): Base plate with mounting holes, leveling, and cable entry | evidence: base_plate, mounting_hole_pattern, cable_entry_grommet

### Reference Grammar
- learn: serial arm link naming and proportions: base, shoulder, upperarm, forearm, wrist
- learn: collision mesh families for UR-style industrial arms
- learn: joint-link segmentation useful for assembly grammar
- need: license must be resolved before training use
- need: visual meshes/URDF/joint metadata are needed; collision STLs alone are incomplete
- need: one permissively licensed STEP/URDF source should be added

### Crawl / CAD Priorities
- permissive URDF/visual mesh
- joint reducer/bearing cutaway
- cable spine routing reference
- tool flange/ISO pattern drawing

### Current Source Targets
- ARMADA project: 6-DOF arm CAD/URDF/assembly reference for joints, links, motor modules, and cable routing.

## small_launch_vehicle

- label: Small Launch Vehicle (sounding)
- domain: Saturn V-structured, Electron-class 2-stage smallsat launcher demonstrator
- material/process: Al 7075 + CFRP + Inconel + ablative / LPBF + CFRP layup
- envelope/mass: 0.6x12m / ~500-2000 kg
- reference status: watch · assets 31
- assembly position hint: Use Z as stage stack axis; shells, rings, fairings, and academic study modules stack vertically with cutaway windows.

### BOM Parts
- `p1` Stage 1 Combustion Chamber Academic Study Section: Non-operational academic educational engine_academic study cartridge: combustion_chamber_reference article, injector-face visual ins...
- `p2` Stage 1 Bell Nozzle Cutaway Study Shell: Non-operational academic bell_nozzle_shell academic study structure with cutaway_window, bolt_circle_reference article, throat label...
- `p3` Turbopump Assembly Academic Study Section: Non-operational academic turbopump_assembly_reference article with impeller_reference article, service cutaway bay, slide_rail, insp...
- `p4` Propellant Tank Reference Article (LOX): Primary_structure tank_reference article barrel for academic study only: propellant_tank_reference article, dome caps, alignment_key...
- `p5` Propellant Tank Reference Article (Fuel): Primary_structure fuel tank_reference article barrel for academic study only: propellant_tank_reference article, fill/drain labels,...
- `p6` Interstage Adapter + Separation Datum: Separation_academic study structure: separation_plane_datum, clamp_band_reference article, interstage_datum, alignment_key, no energ...
- `p7` Stage 2 Engine Academic Study Section: Non-operational academic stage_engine_study with bell_nozzle_shell, cutaway_window, engine_study_cartridge slide_rail, educational l...
- `p8` Payload Fairing Cutaway Study Shell: Primary_structure payload_fairing/nose_cone cutaway study shell with split seam, inspection window, acoustic blanket labels, no flig...
- `p9` Fin Set x 4 Academic Study Structure: Primary_structure fin_set academic study structure with root tabs, alignment_key, bolt_circle_reference article, inspection callouts...
- `p10` Avionics Bay Reference Structure Tray: Avionics_bay educational tray with board_standoff, harness_passthrough, connector labels, EMI shield reference structure, no ordnanc...
- `p11` Battery/Power Academic Study Module: Power_study battery_module reference article with access_panel, keyed connector label, service cover, mass budget note, no live-ener...
- `p12` Recovery Bay Academic Study Section: Recovery_bay educational academic study section with deploy_door, hinge, parachute volume label, inspection window, no deployment-ch...
- `p13` Integration Inspection Ring: Integration_inspection ring with assembly_datum pads, inspection_window, checklist_callout, connection type labels, load-path closur...

### Subsystem Grammar
- `primary_structure` (structures): Propellant tank reference article barrels (LOX/fuel), interstage, payload fairing, fin set, skirts; stacking datums and alignment keys | evidence: tank_reference article, propellant_tank_reference article, payload_fairing, nose_cone, fin_set, interstage_datum, alignment_key, bolt_circle_reference article
- `engine_study` (mechanisms): Removable engine academic study cartridge: combustion chamber reference article, bell nozzle shell, turbopump reference article in cutaway bay (non-operational academic) | evidence: engine_study_cartridge, combustion_chamber_reference article, bell_nozzle_shell, turbopump_assembly_reference article, impeller_reference article, stage_engine_study, cutaway_window, slide_rail
- `avionics_bay` (electronics): Avionics ring/tray with board mounts and harness pass-throughs | evidence: avionics_tray, harness_passthrough, board_standoff
- `power_study` (power): Battery module reference article with access panel | evidence: battery_module, access_panel
- `recovery_bay` (recovery_deployment): Parachute bay reference article with deployment door hinge (study-level) | evidence: recovery_bay, deploy_door, hinge
- `separation_study` (mechanisms): Stage separation plane shown as datum + reference article clamp band (no energetic device) | evidence: separation_plane_datum, clamp_band_reference article
- `integration_inspection` (integration): Assembly order evidence, inspection windows, readiness checklist hooks, connection types and load-path closure | evidence: inspection_window, assembly_datum, checklist_callout

### Reference Grammar
- learn: OpenSCAD parametric rocket study components: assembly, fins, rings, main body
- learn: printable STL/SCAD relationship for academic non-operational rocket cutaway references
- learn: module separation between shell, nose/fins/rings/controller cap
- need: keep explicit academic non-operational boundary
- need: avoid propulsion/performance instructions; use only shape, subsystem, and inspection grammar
- need: add cutaway/avionics/recovery bay references if available

### Crawl / CAD Priorities
- academic non-operational stage shell cutaway
- avionics/recovery bay study reference
- chamber/tank reference-section CAD
- academic boundary labels

### Current Source Targets
- NASA 3D Resources: Academic non-operational rocket/spacecraft shape and subsystem references only.

# Engineering Expansion Seeds

## inline_6_engine_gasoline

- label: Inline-6 Gasoline Engine Assembly
- domain: Conceptual inline-six gasoline engine cutaway assembly for structural, cooling, lubrication, valvetrain, intake, exhaust, and service-access grammar; not a certified running engine
- material/process: Al alloy + cast iron + steel + elastomer / CNC + casting reference structure + FDM
- envelope/mass: 900x650x750 mm / ~180kg reference class
- reference status: needs_reference_crawl · assets 0
- assembly position hint: Use X along crankshaft/cylinder row, Z vertical bore axis, Y intake/exhaust sides; service covers on top/front/bottom.

### BOM Parts
- `p1` Cylinder Block + Crankcase: Inline-6 block with six cylinder bores, crankcase skirt, coolant jacket cues, oil gallery, main bearing cap pads, deck gasket face
- `p2` Crankshaft + Main Bearing Set: Seven-main-bearing crankshaft module with counterweights, thrust bearing face, oil holes, flywheel flange, journal labels
- `p3` Piston + Connecting Rod Set x 6: Piston/rod educational cartridge set with wrist pin bosses, big-end caps, ring groove cues, orientation marks
- `p4` Cylinder Head + DOHC Valvetrain: Cylinder head with intake/exhaust ports, cam carrier, valve cover face, spark plug wells, gasket datum
- `p5` Intake Manifold + Throttle Body: Gasoline intake plenum with six runners, throttle body flange, injector/fuel rail clearance, sensor boss
- `p6` Exhaust Manifold + Heat Shield: Six-runner exhaust manifold reference structure with collector flange, oxygen sensor boss, heat shield standoff, gasket face
- `p7` Timing Chain Front Cover: Front timing cover with chain path window, cam/crank alignment marks, seal bore, service fasteners
- `p8` Oil Pan + Pump Pickup: Oil sump with drain plug, baffle ribs, pickup tube reference article, gasket rail, service access
- `p9` Fuel Rail + Injector Harness: Low-pressure gasoline fuel rail reference structure with injector pockets, connector keying, harness clips, pressure sensor boss
- `p10` Accessory Drive + Mount Brackets: Belt accessory bracket set with alternator/AC/pump bosses, belt plane datum, tensioner pivot, mounting ears

### Subsystem Grammar
- `engine_block` (structures): Block, deck, crankcase, bores, jacket, gallery | evidence: cylinder_bore_x6, deck_gasket_face, coolant_jacket, oil_gallery, main_bearing_cap_pad
- `rotating_cranktrain` (rotating): Crankshaft, pistons, rods, bearing interfaces | evidence: main_journal, rod_journal, counterweight, piston_pin_boss, big_end_cap
- `cylinder_head_valvetrain` (actuation): Head ports, cams, valve cover, spark plug wells | evidence: intake_port, exhaust_port, cam_carrier, spark_plug_well, valve_cover_gasket
- `intake_exhaust` (fluid): Gas exchange manifolds and heat shield interfaces | evidence: intake_runner_x6, plenum, exhaust_runner_x6, collector_flange, heat_shield_standoff
- `lubrication_cooling` (thermal): Oil and coolant service paths | evidence: oil_pickup, drain_plug, coolant_port, thermostat_face, service_plug
- `fuel_ignition_harness` (electronics): Fuel rail, injector wells, spark/coil harness | evidence: fuel_rail, injector_pocket, coil_connector, harness_channel, sensor_boss
- `integration_accessory_mounts` (integration): Accessory brackets, engine mounts, bellhousing/flywheel interfaces | evidence: mount_boss, belt_plane_datum, flywheel_flange, bellhousing_pattern, service_cover

### Reference Grammar
- learn: inline-six segmentation: block, crankcase, head, cranktrain, manifolds, timing cover, oil pan
- learn: gasoline-specific grammar: spark plug wells, fuel rail, injector pockets, throttle/intake plenum
- learn: serviceable cutaway features: gasket faces, coolant jacket cues, oil galleries, accessory brackets
- need: permissive engine cutaway/CAD references for block/head/cranktrain are needed
- need: keep output at conceptual/educational assembly grammar; no certified running-engine claim

### Crawl / CAD Priorities
- engine block/head cutaway CAD
- cranktrain exploded view
- intake/exhaust manifold CAD
- oil/coolant gallery diagram

### Current Source Targets
- Wikipedia Straight-six engine: General inline-six architecture vocabulary and external layout references.
- GrabCAD inline-six / engine block search: Potential CAD-like visual references for block, cranktrain, head, and accessory layout.

## inline_6_engine_diesel

- label: Inline-6 Diesel Engine Assembly
- domain: Conceptual inline-six diesel engine cutaway assembly emphasizing stronger block/head grammar, common-rail fuel path, turbo air path, cooling/lubrication, and service access; not a certified running engine
- material/process: Compacted graphite iron + steel + Al alloy / CNC + casting reference structure + FDM
- envelope/mass: 1100x720x850 mm / ~320kg reference class
- reference status: needs_reference_crawl · assets 0
- assembly position hint: Use X along crankshaft/cylinder row, Z bore/head axis; turbo/exhaust on one side, intake/common rail service on the other.

### BOM Parts
- `p1` Reinforced Cylinder Block: Diesel I6 block with thick deck, six bores, cross-bolted main cap cues, coolant jacket, oil gallery
- `p2` Forged Crankshaft + Bearing Ladder: Heavy crankshaft and bearing ladder with main caps, thrust face, oil feeds, flywheel flange
- `p3` Piston/Rod Assembly x 6: Diesel piston/rod educational set with bowl crown cue, wrist pin boss, rod cap bolts, ring bands
- `p4` Cylinder Head + Injector Wells: Diesel head with injector wells, glow plug ports, valve bridge, intake/exhaust ports, gasket datum
- `p5` Common Rail + Injector Harness: Common-rail layout reference structure with rail brackets, injector pockets, return line path, harness channel; non-operational acad...
- `p6` Turbocharger + Exhaust Manifold Reference Structure: Turbo/exhaust academic study structure with turbine housing shell, compressor shell, oil feed/return bosses, heat shield
- `p7` Intake/EGR Cooler Path Reference Structure: Charge-air/EGR cooler routing reference structure with flanges, gasket faces, bypass/service cover, sensor bosses
- `p8` Oil Cooler + Filter Module: Oil cooler/filter module with cartridge cap, coolant ports, gasket face, drain boss
- `p9` Timing Gear Housing: Front gear housing with idler gear pockets, crank/cam gear datums, service cover, seal bore
- `p10` Engine Mount + Bellhousing Interfaces: Mount brackets and bellhousing adapter pattern with datum pads, bolt groups, lifting lug cues

### Subsystem Grammar
- `reinforced_block_head` (structures): High-compression structural block/head grammar | evidence: thick_deck, cross_bolt_boss, main_bearing_ladder, head_bolt_pattern, gasket_face
- `diesel_cranktrain` (rotating): Heavy rotating group and bearing support | evidence: main_journal, rod_cap_bolt_pad, counterweight, bearing_ladder, flywheel_flange
- `common_rail_injection_study` (fluid): Non-operational academic high-pressure layout vocabulary only | evidence: common_rail, injector_well, return_line_channel, rail_bracket, harness_key
- `turbo_air_exhaust_study` (fluid): Turbo/exhaust/charge air routing reference structure | evidence: turbine_shell, compressor_shell, oil_feed_boss, charge_pipe_flange, heat_shield
- `thermal_lubrication` (thermal): Coolant/oil galleries, cooler and filter access | evidence: coolant_port, oil_cooler_face, filter_cartridge_cap, drain_boss, service_plug
- `gear_timing_access` (rotating): Timing gears and front housing serviceability | evidence: gear_pocket, idler_axis, seal_bore, timing_mark, front_cover
- `mounting_integration` (integration): Mounts, lifting, bellhousing, service datums | evidence: mount_bracket, lifting_lug, bellhousing_pattern, datum_pad, service_window

### Reference Grammar
- learn: diesel inline-six reinforcement grammar: thick deck, bearing ladder, cross-bolt bosses, heavy cranktrain
- learn: diesel-specific layout: injector wells, common rail, return path, turbo/exhaust heat shield, oil cooler
- learn: service access for timing gear housing, filters, injectors, lifting/mounting datums
- need: licensed diesel engine cutaway and common-rail layout references should be reviewed
- need: do not promote performance, emissions, injection calibration, or certified engine claims

### Crawl / CAD Priorities
- reinforced diesel block/head cutaway
- common rail/injector well layout
- turbo/exhaust routing CAD
- oil cooler/filter module drawing

### Current Source Targets
- Wikipedia Diesel engine: Diesel-specific architecture vocabulary: injector wells, common rail, turbo path, reinforced block.
- GrabCAD diesel engine / inline six search: Potential CAD-like visual references for diesel block/head/common-rail/turbo layouts.

## centrifugal_pump

- label: Centrifugal Pump Assembly
- domain: Industrial centrifugal pump cutaway assembly for volute, impeller, shaft, bearing, seal, flange, and service-access grammar
- material/process: Cast iron + stainless steel + elastomer / Casting reference structure + CNC + FDM
- envelope/mass: 520x320x380 mm / ~35kg
- reference status: needs_reference_crawl · assets 0
- assembly position hint: Use X shaft axis, radial impeller/volute around shaft, suction at impeller eye, discharge tangent to volute.

### BOM Parts
- `p1` Volute Casing: Spiral volute casing with inlet eye, outlet flange, pressure boundary, drain plug, inspection boss
- `p2` Impeller: Closed impeller with hub, blade channels, wear ring face, balance drill cues
- `p3` Pump Shaft: Stepped shaft with keyway, impeller nut, bearing journals, coupling end
- `p4` Bearing Housing: Bearing frame with front/rear bearing seats, grease ports, oil sight window, mounting feet
- `p5` Mechanical Seal Cartridge: Seal cartridge reference structure with gland plate, O-ring groove, flush port, leakage drain
- `p6` Suction/Discharge Flange Set: ANSI-style flanges with bolt circle, gasket face, flow arrow, pipe alignment datum
- `p7` Coupling Guard + Motor Adapter: Motor adapter and coupling guard with service window, fastener tabs, alignment slots
- `p8` Baseplate + Mount Pads: Baseplate with slotted mount holes, leveling pads, drain channel, lifting points

### Subsystem Grammar
- `volute_pressure_boundary` (fluid): Casing pressure and flow path | evidence: inlet_eye, volute_channel, outlet_flange, drain_plug, inspection_boss
- `impeller_rotor` (rotating): Impeller and shaft rotating path | evidence: impeller_hub, blade_channel, wear_ring_face, shaft_keyway, impeller_nut
- `bearing_support` (structures): Bearing frame and support | evidence: bearing_seat_front, bearing_seat_rear, grease_port, oil_sight_window, mounting_foot
- `seal_gland` (sealing): Seal cartridge and leakage path | evidence: gland_plate, o_ring_groove, flush_port, leak_drain, seal_access
- `pipe_motor_integration` (integration): Pipe flanges, motor adapter, baseplate alignment | evidence: bolt_circle, gasket_face, alignment_slot, coupling_guard, leveling_pad

### Reference Grammar
- learn: volute/impeller/shaft/bearing/seal/flange decomposition for rotating fluid machinery
- learn: pressure-boundary grammar: inlet eye, outlet flange, gasket faces, drain/vent plugs, inspection bosses
- learn: back-pull-out service grammar: seal cartridge, bearing housing, coupling guard, baseplate alignment
- need: pump cross-section/CAD references with clear volute and seal cartridge structure are needed
- need: scorecard should penalize pumps with no flow path or serviceable seal/bearing access

### Crawl / CAD Priorities
- volute casing STEP/cutaway
- impeller CAD
- mechanical seal cartridge drawing
- bearing frame/baseplate assembly

### Current Source Targets
- NIST / public pump reference search: Public technical references for pump components and inspection vocabulary.
- GrabCAD centrifugal pump search: Volute, impeller, bearing frame, and flange CAD references.

## hydraulic_manifold

- label: Hydraulic Manifold Block Assembly
- domain: Hydraulic manifold block concept for porting, cross-drilled galleries, cartridge valves, plugs, labels, and service access
- material/process: Al 6061 + steel plugs + elastomer seals / CNC
- envelope/mass: 260x160x120 mm / ~8kg
- reference status: watch · assets 9
- assembly position hint: Use block datum faces; ports occupy named faces, cross-drilled galleries run between P/T/A/B and cartridge cavities.

### BOM Parts
- `p1` Main Manifold Block: CNC manifold block with P/T/A/B ports, cross-drilled galleries, plug bosses, datum faces
- `p2` Cartridge Valve Set: Screw-in cartridge valve cavities with O-ring lands, wrench clearance, port labels
- `p3` Pressure Relief Valve Section: Relief valve pocket, adjustment cap, spring chamber cue, tank return path
- `p4` Check Valve Section: Check valve cavity with flow arrow, seat cone cue, service plug
- `p5` Sensor + Test Port Set: Pressure transducer boss, test coupler port, cable exit, protective cover
- `p6` Mounting Feet + Label Plate: Mounting feet, engraved circuit label plate, orientation arrows, service side datum

### Subsystem Grammar
- `manifold_flow_network` (fluid): Port map and drilled gallery grammar | evidence: p_port, t_port, a_port, b_port, cross_drill, plug_boss
- `cartridge_valve_cavities` (fluid): Cartridge pockets and seal lands | evidence: valve_cavity, o_ring_land, wrench_clearance, retainer_thread, flow_arrow
- `pressure_control` (fluid): Relief/check valve sections | evidence: relief_adjuster_cap, spring_chamber, check_seat, tank_return_path, service_plug
- `instrumentation_access` (electronics): Sensor and test access | evidence: pressure_sensor_boss, test_port, cable_exit, protective_cover, label_plate
- `mounting_datum` (integration): Mounting and service orientation | evidence: mounting_foot, datum_face, engraved_label, service_side, bolt_pattern

### Reference Grammar
- learn: CNC manifold block grammar: P/T/A/B ports, cross-drilled galleries, plug bosses, datum faces
- learn: cartridge valve cavities with O-ring lands, wrench clearance, flow arrows, and labels
- learn: instrumentation and test access: pressure sensor boss, test port, protective cover, label plate
- need: licensed manifold drawings/CAD with visible port maps and valve cavities are needed
- need: avoid implying rated pressure certification; use conceptual routing and inspection vocabulary

### Crawl / CAD Priorities
- manifold port map drawing
- cross-drilled gallery CAD
- cartridge valve cavity reference
- sensor/test port layout

### Current Source Targets
- GrabCAD hydraulic manifold search: Manifold block porting, cartridge valve, plug, and label layout references.
- OpenSCAD MCAD block/hole/fastener primitives: OpenSCAD boxes, polyholes, fasteners, hardware, and regular-shape grammar for manifold block port...

## battery_pack_module

- label: Battery Pack Module
- domain: Serviceable battery module concept for cell support, busbars, BMS, cooling plate interface, venting, isolation, and enclosure grammar; no live-energy build instruction
- material/process: Al enclosure + polymer holders + copper busbar reference structure / Sheet metal + FDM + CNC
- envelope/mass: 520x360x160 mm / ~18kg
- reference status: watch · assets 8
- assembly position hint: Use module length/width as cell array plane and Z as lid/service direction; cooling plate and busbars are separated layers.

### BOM Parts
- `p1` Cell Carrier Tray: Cell holder tray with repeated cell pockets, compression pads, locator ribs, module datum
- `p2` Busbar + Fuse Cover Reference Structure: Insulated busbar reference structure with fuse windows, terminal guards, polarity labels, no live-energy claim
- `p3` BMS Electronics Bay: BMS board pocket, sensing harness channels, service connector, EMI shield cover
- `p4` Cooling Plate Interface: Cooling plate contact face, thermal pad zones, inlet/outlet ports, leak inspection channel
- `p5` Pack Enclosure + Lid: Gasketed enclosure shell with lid flange, fastener pattern, vent path, service label
- `p6` HV Connector + Service Disconnect Reference Structure: Keyed HV connector reference structure, service disconnect handle, low-voltage connector, strain relief
- `p7` Crash/Isolation End Plates: End plates with crush ribs, isolation spacers, tie rod bosses, lifting tabs

### Subsystem Grammar
- `cell_support` (structures): Cell pockets and compression grammar | evidence: cell_pocket_array, compression_pad, locator_rib, tie_rod_boss, module_datum
- `electrical_distribution_study` (power): Busbar/fuse/terminal layout vocabulary only | evidence: busbar_cover, fuse_window, terminal_guard, polarity_label, sense_wire_channel
- `bms_harness` (electronics): BMS and signal harness routing | evidence: bms_board_pocket, service_connector, emi_shield, harness_channel, ground_point
- `thermal_interface` (thermal): Cooling plate and thermal pad contact | evidence: thermal_pad_zone, coolant_inlet, coolant_outlet, leak_channel, cold_plate_face
- `sealed_enclosure_safety` (sealing): Lid gasket, vent, disconnect, no-live-energy boundary | evidence: lid_flange, gasket_groove, vent_path, disconnect_handle, warning_label

### Reference Grammar
- learn: battery module decomposition: cell carrier, busbar cover, BMS bay, cooling plate, enclosure, disconnect
- learn: thermal/electrical separation grammar: thermal pad zones, sense-wire channels, EMI shield, terminal guards
- learn: safety/service grammar: gasketed lid, vent path, service disconnect, warning labels, no-live-energy boundary
- need: permissive battery module/cold-plate/enclosure references are needed before training promotion
- need: do not generate live-energy assembly instructions or claim pack safety certification

### Crawl / CAD Priorities
- cell tray CAD
- busbar/BMS cover reference
- cooling plate interface
- vent/disconnect/enclosure drawing

### Current Source Targets
- NREL battery thermal management publications: Battery thermal, module, and safety vocabulary for non-live concept generation.
- GrabCAD battery module search: Cell holders, busbar covers, BMS pockets, enclosures, and connector references.
- NopSCADlib battery/connector/enclosure primitives: Battery, fuseholder, connector, cable strip, PCB mount, and enclosure grammar for battery module...

## liquid_cold_plate

- label: Liquid Cold Plate Assembly
- domain: Liquid cold plate concept for serpentine channels, manifolds, gasket, electronics mounting, leak inspection, and thermal interface grammar
- material/process: Al 6061 + copper insert + elastomer gasket / CNC + brazed reference structure
- envelope/mass: 320x220x40 mm / ~3kg
- reference status: needs_reference_crawl · assets 0
- assembly position hint: Use plate XY as heat-source plane and Z as stacked cover/gasket direction; inlet/outlet manifolds sit on one edge.

### BOM Parts
- `p1` Cold Plate Body: Machined plate body with serpentine channel, fin islands, mounting bosses, flatness datum
- `p2` Inlet/Outlet Manifold Cap: Manifold cap with hose barb/AN port faces, O-ring groove, flow arrow, fastener pattern
- `p3` Gasket + Seal Track: Continuous gasket groove, compression stops, leak witness channel, corner reliefs
- `p4` Power Module Mount Pads: IGBT/MOSFET mount pads, thermal paste zones, isolation washer pockets, sensor pad
- `p5` Leak Test + Drain Ports: Pressure test port, drain plug, bleed screw, service labels
- `p6` Cover Plate: Bolted cover with ribbing, datum pins, inspection window label, torque sequence marks

### Subsystem Grammar
- `thermal_channel_network` (thermal): Serpentine cooling path and heat source pads | evidence: serpentine_channel, fin_island, thermal_pad_zone, temperature_sensor_pad, flatness_datum
- `manifold_ports` (fluid): Inlet/outlet and flow distribution | evidence: inlet_port, outlet_port, manifold_cap, flow_arrow, hose_boss
- `seal_leak_boundary` (sealing): Gasket track and leak witness path | evidence: gasket_groove, compression_stop, leak_witness_channel, corner_relief, bleed_screw
- `electronics_mounting` (electronics): Power device mounting and isolation | evidence: module_mount_pad, isolation_washer_pocket, ground_point, fastener_pattern, service_label
- `service_test_access` (integration): Test/drain/cover assembly | evidence: test_port, drain_plug, datum_pin, torque_sequence_mark, inspection_label

### Reference Grammar
- learn: cold plate channel grammar: serpentine path, fin islands, inlet/outlet manifold, thermal pad zones
- learn: seal/leak grammar: gasket groove, compression stops, leak witness channel, drain/bleed/test ports
- learn: power-device mounting grammar: flatness datum, isolation washer pockets, torque marks, service labels
- need: channel/cap/gasket CAD or drawings should be collected for geometry fidelity
- need: avoid rated pressure/thermal-performance claims until external analysis exists

### Crawl / CAD Priorities
- serpentine channel CAD
- manifold cap/gasket drawing
- thermal pad/mount pattern
- leak-test/drain port reference

### Current Source Targets
- GrabCAD liquid cold plate search: Serpentine channels, manifolds, gasket tracks, and mounting pad references.

## cnc_axis_carriage

- label: CNC Linear Axis Carriage
- domain: Precision CNC linear axis carriage concept for rails, bearing blocks, ball screw, motor mount, way covers, sensors, and lubrication grammar
- material/process: Cast Al + steel rails + polymer covers / CNC + FDM cover reference structure
- envelope/mass: 700x220x180 mm / ~22kg
- reference status: watch · assets 29
- assembly position hint: Use X as travel axis; rails parallel X, ball screw on centerline, carriage plate rides above bearing blocks.

### BOM Parts
- `p1` Carriage Plate: Machined carriage with rail block bolt pattern, datum edge, dowel holes, lightening pockets
- `p2` Linear Rail Pair + Bearing Blocks: Two linear rails with four bearing block footprints, grease ports, rail datum references
- `p3` Ball Screw + Nut Housing: Ball screw shaft, nut housing, fixed/floating bearing ends, preload label
- `p4` Servo Motor Mount + Coupling Guard: Servo flange, coupling guard, belt/shaft alignment datum, service slots
- `p5` Limit/Home Sensor Brackets: Home and limit switch brackets, cable channel, target flag, adjustment slots
- `p6` Way Cover + Wiper Set: Telescoping way cover reference structure, wiper lip, chip guard, fastener tabs
- `p7` Lubrication Manifold: Lubrication ports, distribution channels, grease nipples, service labels

### Subsystem Grammar
- `carriage_structure` (structures): Datum plate, rail blocks, pockets | evidence: datum_edge, dowel_hole, rail_block_pattern, lightening_pocket, mount_face
- `linear_guidance` (actuation): Rails and bearing blocks | evidence: linear_rail, bearing_block, grease_port, rail_datum, wiper_mount
- `ball_screw_drive` (rotating): Screw/nut/bearing drive path | evidence: ball_screw, nut_housing, fixed_bearing, floating_bearing, preload_label
- `motor_sensor_integration` (electronics): Motor, coupling, sensors, cable routing | evidence: servo_flange, coupling_guard, home_sensor, limit_sensor, cable_channel
- `protection_lubrication` (sealing): Way covers and lubrication | evidence: way_cover, wiper_lip, chip_guard, lube_manifold, service_nipple

### Reference Grammar
- learn: precision axis decomposition: carriage plate, rails, bearing blocks, ball screw, motor mount, sensors
- learn: datum/tolerance grammar: dowel holes, rail reference edge, preload notes, adjustment slots
- learn: protection/service grammar: way covers, wipers, lubrication manifold, cable channels, grease ports
- need: licensed linear axis/ball screw/rail assembly CAD references are needed
- need: scorecard should penalize axis designs without rail datums, screw support, or sensor/lube access

### Crawl / CAD Priorities
- linear rail/carriage CAD
- ball screw support assembly
- servo mount/coupling guard
- way cover/lube manifold reference

### Current Source Targets
- OpenBuilds linear motion documentation: Linear rail/carriage, actuator, motor mount, and sensor bracket vocabulary.
- GrabCAD CNC linear axis search: Carriage plate, ball screw, linear rail, and cover references.
- NopSCADlib rail/bearing/motor primitives: Linear rail, SBR rail, bearing block, screw, stepper, motor, pulley, and drag-chain grammar for C...

## gearbox_reducer

- label: Two-Stage Gearbox Reducer
- domain: Two-stage gearbox reducer concept for housing, gears, shafts, bearings, oiling, seals, covers, and mounting grammar
- material/process: Cast Al housing + steel gears/shafts + elastomer seals / Casting reference structure + CNC + FDM
- envelope/mass: 360x240x220 mm / ~14kg
- reference status: watch · assets 7
- assembly position hint: Use parallel shaft axes through housing; gear mesh centerlines define internal layout, service cover on top/side.

### BOM Parts
- `p1` Split Gearbox Housing: Split housing with bearing bores, gasket flange, ribbing, inspection cover
- `p2` Input Shaft + Pinion: Input shaft with pinion gear, keyway, seal journal, bearing seats
- `p3` Intermediate Shaft + Gear Pair: Intermediate compound gear shaft with two gears, spacer, bearing seats
- `p4` Output Shaft + Bull Gear: Output shaft with bull gear, output flange, keyway, bearing support
- `p5` Bearing + Seal Set: Bearing cartridges, oil seals, shims, retainer plates
- `p6` Lubrication + Breather System: Oil fill/drain/level plugs, splash baffle, breather cap, sight glass
- `p7` Mounting Feet + Torque Arm: Mount feet, torque arm boss, dowel pads, bolt groups

### Subsystem Grammar
- `gearbox_housing` (structures): Split housing and bearing bores | evidence: bearing_bore, gasket_flange, rib, inspection_cover, dowel_pad
- `gear_train` (rotating): Input/intermediate/output gear mesh | evidence: input_pinion, compound_gear, bull_gear, mesh_centerline, spacer
- `shaft_bearing_support` (rotating): Shaft journals and bearing seats | evidence: shaft_journal, bearing_seat, retainer_plate, shim_stack, output_flange
- `sealing_lubrication` (sealing): Oil seals, plugs, baffles, breather | evidence: oil_seal, fill_plug, drain_plug, sight_glass, breather_cap
- `mounting_service` (integration): Mounting and access | evidence: mounting_foot, torque_arm_boss, bolt_group, service_cover, alignment_datum

### Reference Grammar
- learn: gearbox decomposition: split housing, input/intermediate/output shafts, gear mesh, bearings, seals
- learn: lubrication/service grammar: fill/drain/level plugs, breather, sight glass, inspection cover
- learn: precision support grammar: bearing bores, shims, retainer plates, dowel pads, mesh centerline
- need: permissive reducer cutaway/CAD references with shaft/bearing/gear layout are needed
- need: do not claim torque rating or gear life without real sizing analysis

### Crawl / CAD Priorities
- split housing cutaway
- gear/shaft/bearing layout
- oil seal/plug/breather details
- mounting feet/torque arm drawing

### Current Source Targets
- GrabCAD gearbox reducer search: Housing, gear train, shaft, bearing, seal, and lubrication references.
- OpenSCAD MCAD mechanical library: OpenSCAD bearing, gear, involute gear, screw, motor, stepper, and linear-bearing grammar for redu...

## underwater_sealed_sensor_housing

- label: Underwater Sealed Sensor Housing
- domain: Underwater sensor housing concept for pressure shell, O-ring cap, cable gland, optical/acoustic window, mounting cradle, and service boundary grammar
- material/process: Al 6061 + acrylic window + elastomer seals + stainless hardware / CNC + FDM fixture reference structure
- envelope/mass: 320x180x180 mm / ~4kg
- reference status: watch · assets 12
- assembly position hint: Use cylinder axis through front window and rear cap; cable gland exits rear/side, cradle supports shell below.

### BOM Parts
- `p1` Cylindrical Pressure Shell: Cylindrical housing shell with wall-thickness cue, internal rail slots, external cradle pads
- `p2` Front Sensor Window Cap: Front cap with optical/acoustic window, O-ring groove, retaining ring, anti-rotation pins
- `p3` Rear Service Cap: Rear cap with double O-ring cue, service screws, puller holes, orientation mark
- `p4` Cable Gland + Strain Relief: Wet-mate cable gland reference structure, bend relief boot, potting pocket, connector key
- `p5` Internal Electronics Tray: Slide-in board tray, sensor board standoffs, desiccant pocket, ground lug
- `p6` Mounting Cradle + Anode Pad: ROV/vehicle cradle with clamp bands, sacrificial anode pad, drain path, lifting tab
- `p7` Leak Test Port + Label Set: Leak test plug, pressure label, inspection witness groove, serial plate

### Subsystem Grammar
- `pressure_shell` (structures): Sealed cylinder and internal support | evidence: cylindrical_shell, wall_thickness_cue, internal_rail, external_cradle_pad, datum_mark
- `window_and_caps` (sealing): Front/rear caps and O-ring boundaries | evidence: sensor_window, o_ring_groove, retaining_ring, service_screw, puller_hole
- `cable_penetration` (electronics): Cable gland and strain relief | evidence: cable_gland, bend_relief, potting_pocket, connector_key, strain_relief
- `internal_sensor_tray` (electronics): Slide-in electronics and sensor tray | evidence: board_tray, standoff, desiccant_pocket, ground_lug, slide_rail
- `marine_mount_service` (integration): Cradle, anode, leak test, labels | evidence: clamp_band, anode_pad, drain_path, leak_test_port, serial_plate

### Reference Grammar
- learn: sealed marine enclosure grammar: pressure shell, end caps, O-ring grooves, cable gland, service cap
- learn: payload integration grammar: sensor window, internal tray, desiccant pocket, ground lug, slide rails
- learn: marine service grammar: leak test port, clamp cradle, drain path, anode pad, serial/pressure labels
- need: licensed underwater enclosure/cable gland/O-ring cap references are needed
- need: avoid depth rating or pressure certification claims without analysis

### Crawl / CAD Priorities
- pressure shell/end cap CAD
- O-ring/cable gland drawing
- internal electronics tray
- cradle/anode/leak-test reference

### Current Source Targets
- Blue Robotics documentation: Underwater enclosure, cable gland, O-ring, thruster/sensor mounting vocabulary.
- GrabCAD underwater housing search: Sealed pressure shell, end cap, cable gland, and cradle references.
- NopSCADlib enclosure/sealing primitives: Box, camera housing, tube, cable grommet, O-ring, and sealing-strip grammar for sealed housing re...

## liquid_rocket_engine_academic

- label: Academic Liquid Rocket Engine System
- domain: Academic liquid rocket propulsion system seed for conceptual chamber/nozzle, injector taxonomy, regenerative cooling, feed-system architecture, turbomachinery, instrumentation, controls, and mount/load-path grammar; non-buildable and non-operational
- material/process: academic multi-material reference: copper alloy liner + steel jacket + Al/steel structures / concept CAD + cutaway study model
- envelope/mass: conceptual study envelope / academic reference only
- reference status: needs_reference_crawl · assets 0
- assembly position hint: Use Z as chamber/nozzle study axis; feed-system modules sit radially, turbomachinery/DAQ modules sit off-axis, thrust-frame datum is aft.

### BOM Parts
- `p1` Combustion Chamber Heat-Transfer Study Section: Academic chamber section with liner/jacket zones, heat-transfer labels, sensor bosses, flange datums, and no operational pressure/th...
- `p2` Injector Architecture Taxonomy Plate: Non-buildable injector concept plate comparing injector families with blocked detail holes, manifold zones, face datum, and no orifi...
- `p3` Nozzle Contour Phenomena Study Shell: Nozzle contour study shell with throat/exit/station labels, thermal/structural callouts, cutaway window, and no expansion-ratio perf...
- `p4` Regenerative Cooling Path Study Jacket: Cooling-path teaching jacket with channel-route vocabulary, inlet/outlet interface labels, leak-inspection path, and no flow-rate/si...
- `p5` Feed-System Architecture Manifold: Conceptual oxidizer/fuel feed manifold map with valve/filter/check-element placeholders, port labels, isolation zones, and no propel...
- `p6` Turbopump Energy-Path Study Module: Academic turbopump module showing pump/turbine/shaft/bearing regions, energy-path arrows, service covers, and no performance/speed s...
- `p7` Instrumentation + Data Acquisition Ring: Sensor boss ring, harness channels, DAQ connector zones, calibration labels, and safe measurement vocabulary without operating proce...
- `p8` Control Logic + Interlock Panel: Conceptual control/interlock panel with state labels, inhibit blocks, connector keying, and no ignition/start sequence instructions
- `p9` Thrust-Frame Load-Path Study Mount: Academic thrust-frame/mount interface with trunnion pads, load-path arrows, bolted datum pads, and no flight qualification claim
- `p10` Cutaway Safety Boundary + Annotation Cover: Transparent cutaway cover and annotation frame that marks non-buildable academic boundaries, blocked parameters, and inspection labels

### Subsystem Grammar
- `chamber_heat_transfer` (thermal): Combustion chamber heat-transfer and structural jacket study | evidence: liner_zone, jacket_zone, heat_transfer_label, sensor_boss, flange_datum
- `injector_architecture` (fluid): Injector taxonomy and manifold-zone study without buildable orifice details | evidence: injector_family_label, blocked_orifice_detail, manifold_zone, face_datum, mixing_concept_label
- `nozzle_expansion_study` (structures): Nozzle contour, throat/exit station, and thermal/structural callout study | evidence: throat_station_label, exit_station_label, contour_section, cutaway_window, thermal_callout
- `regenerative_cooling_study` (thermal): Regenerative cooling route vocabulary and leak/service boundary | evidence: cooling_channel_route, inlet_interface_label, outlet_interface_label, leak_inspection_path, service_cover
- `feed_system_architecture` (fluid): Conceptual feed-system topology and valve/check/filter placeholders | evidence: oxidizer_path_label, fuel_path_label, valve_placeholder, filter_placeholder, isolation_zone
- `turbomachinery_energy_path` (rotating): Pump/turbine/shaft/bearing energy-path study without performance sizing | evidence: pump_region, turbine_region, shaft_axis, bearing_region, energy_path_arrow
- `instrumentation_controls` (electronics): Instrumentation, DAQ, interlock, and harness vocabulary | evidence: sensor_boss, daq_connector, harness_channel, interlock_label, calibration_label
- `thrust_frame_integration` (integration): Academic load path, mount datums, and cutaway boundary | evidence: thrust_frame, trunnion_pad, load_path_arrow, datum_pad, non_buildable_boundary_label

### Reference Grammar
- learn: academic liquid-engine subsystem grammar: chamber heat transfer, nozzle expansion study, injector taxonomy, regenerative cooling
- learn: feed-system and turbomachinery architecture vocabulary without buildable sizing or operating procedures
- learn: instrumentation, DAQ, interlock, thrust-frame load path, and non-buildable boundary annotation
- need: collect safe academic NASA/NTRS or textbook-like references for subsystem decomposition and terminology
- need: avoid buildable engine dimensions, propellant handling, ignition/start procedures, thrust/chamber-pressure sizing, injector hole sizing, turbopump performance, test-stand operating steps, or flight-use instructions
- need: use references as conceptual architecture and validation vocabulary only until legal/safety review

### Crawl / CAD Priorities
- NASA/NTRS academic liquid propulsion reports
- safe cutaway diagrams for chamber/nozzle/cooling/feed topology
- instrumentation/control architecture references
- turbomachinery educational diagrams without performance sizing

### Current Source Targets
- NASA 3D Resources: Safe public spacecraft/engine visual references for academic cutaway and annotation grammar.
- NASA technical reports / NTRS liquid propulsion references: Academic liquid propulsion terminology, subsystem decomposition, instrumentation, cooling, and tu...
- NASA 3D Resources: Academic non-operational rocket engine cutaway and subsystem references only.
