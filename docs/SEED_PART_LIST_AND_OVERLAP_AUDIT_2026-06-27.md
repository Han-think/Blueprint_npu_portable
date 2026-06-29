# Seed Part List and Overlap Audit

- total seeds: 16
- total BOM parts: 145
- overlap candidates: 128

## Seed Part Counts

| Seed | Domain | Parts |
| --- | --- | ---: |
| `cubesat` | space/electronics/frame/harness/deployables | 12 |
| `haptic_glove` | wearable robotics/linkage/cable/ergonomics | 12 |
| `long_range_recon_wing` | aero structure/wing stations/payload bay | 9 |
| `tiltrotor` | aero/propulsion mount/tilt mechanism | 9 |
| `robot_arm` | serial mechanism/joints/links/cable spine | 12 |
| `small_launch_vehicle` | academic aerospace shell/staged study boundary | 13 |
| `inline_6_engine_gasoline` | IC engine/gasoline cranktrain/valvetrain/manifolds | 10 |
| `inline_6_engine_diesel` | IC engine/diesel reinforced block/common rail/turbo | 10 |
| `centrifugal_pump` | rotating fluid machinery/volute/impeller/seal | 8 |
| `hydraulic_manifold` | fluid power block/ports/valves/galleries | 6 |
| `battery_pack_module` | power electronics/cells/busbars/BMS/enclosure | 7 |
| `liquid_cold_plate` | thermal management/channels/manifold/gasket | 6 |
| `cnc_axis_carriage` | precision motion/rails/ballscrew/sensors/lube | 7 |
| `gearbox_reducer` | rotating power transmission/gears/shafts/bearings | 7 |
| `underwater_sealed_sensor_housing` | marine sealed enclosure/O-rings/cable gland | 7 |
| `liquid_rocket_engine_academic` | academic liquid rocket propulsion/chamber/cooling/feed/instrumentation boundary | 10 |

## Full BOM By Seed

### cubesat

- domain: space/electronics/frame/harness/deployables

- `p1` Primary Structure (3U): 3U CubeSat primary frame, Al 7075, PC/104 standoffs, deployable rail guide grooves (CDS spec)
- `p2` Solar Panel x 4 (deploy): Deployable solar panel wing, 3U size, spring-loaded hinge, burn-wire release, deployment damper
- `p3` Antenna Deployer x 2: Tape-spring UHF/S-band antenna deployer, stowed flat, burn-wire release, latching tab
- `p4` Reaction Wheel x 3: Small reaction wheel assembly, brushless motor, momentum 0.005-0.05 Nms, isolation mount
- `p5` Star Tracker Mount: Star tracker optical bench mount, CTE-matched, baffled sun shield, line-of-sight +-1deg
- `p6` Payload Optics Bench: EO payload optics bench, thermal stability, optical baffles, focal plane interface, lens mounts
- `p7` Cold Gas Thruster x 4: Cold gas propulsion thruster bracket, 4 thrusters cross-pattern, 50mN class, plumbing manifold
- `p8` Separation Spring Plate: P-POD or ISIPOD separation interface plate, spring pusher contact, kill switch arm
- `p9` EPS Solar Charging Module: EPS solar charging subsystem: solar_panel_face inputs, removable battery_tray, eps_board_slot, power_connector keying, service cover, mass budget <480g
- `p10` CDH Avionics Stack: Command/data handling avionics stack: obc_board, stack_harness, debug_port_access, board standoffs, connector labels, grounding point, mass budget <260g
- `p11` Thermal Path / Radiator Strap Evidence: Thermal_path closure module: radiator_face, thermal_strap_note, vent_hole, battery-to-frame conduction pad, service-visible thermal datum, inspection label, mass budget <120g
- `p12` Integration Harness + Datum Spine: Integration_harness closure spine with harness_channel, connector_keying, assembly_datum pads, routing clips, service hatch, reciprocal interface labels, inspection checklist marks

### haptic_glove

- domain: wearable robotics/linkage/cable/ergonomics

- `p1` Dorsal Control Module x 2: Snap-in dorsal electronics and battery module, tool-less lid, wireless board bay, service label and cable exits
- `p2` Finger Exo Linkage Cartridge x 10: Two-segment exoskeleton finger linkage cartridge, single-pin removable, hinge datum pads, thimble slip interface
- `p3` Flexion-Resistance Actuator x 10: Plug-in tendon brake/clutch actuator module, knuckle row mount, cable pulley, connector pocket, service access
- `p4` Adjustable Wrist Band x 2: Quick-release wrist band, cable raceway, soft-contact interface, buckle, dorsal module anchor
- `p5` Cable Raceway + Harness Cover x 2: Snap-fit cable routing cover from wrist band to fingers, strain relief slots, inspection windows
- `p6` Finger Thimble Interface Set: Replaceable fingertip thimbles, slip-clearance sockets, soft liner cue, per-finger label and hinge pin access
- `p7` Palm Sensor Plate x 2: Palm-side flex/bend sensor channel plate, IMU mount pad, per-finger sensor channel exits, sensor connector pocket, washable liner interface
- `p8` Battery + Power Module x 2: Wrist battery pocket with quick-swap door, li-ion pack 2S 18650, BMS access window, power connector keying, charge LED window
- `p9` Wiring Loom + Service Loop Set: Knuckle-crossing wiring loom with service loops, strain relief at every flex boundary, flex-rated bend radius, power vs signal channel separation
- `p10` Knuckle Mount Rail x 2: Dorsal knuckle row mounting rail, actuator plug-in pockets, datum pads per finger station, fastener pattern and removal path
- `p11` Fit Calibration + Safety Release Set: Wearable_structure closure module: wrist_quick_release, soft_liner_zone, finger_clearance gauges, don/doff datum labels, emergency release pull tab
- `p12` Service Port + Flex-Wiring Inspection Cover: Flex_wiring closure module: service_loop inspection cover, strain_relief, bend_radius_note, connector keying, charge/debug service port, power vs signal separation label

### long_range_recon_wing

- domain: aero structure/wing stations/payload bay

- `p1` Center Body Pod: Flying-wing center pod, equipment bay door, wing-spar reinforcement, motor pylon at rear
- `p2` Wing Spar (2-piece): 20mm CFRP main spar, 2-piece centerjoint, anti-rotation key, 800mm half-span each
- `p3` Wing Rib Set x 12: Wing rib NACA airfoil profile, lightening pockets, leading edge sock, trailing edge taper
- `p4` Elevon Servo Pocket x 2: Elevon servo pocket, MG90S or DS215MG, control horn linkage, removable access cover
- `p5` Motor + Pusher Prop Mount: Rear pusher 2814 BLDC mount, 10x7 folding prop clearance, thrust line +1deg down
- `p6` GPS + Pitot Boom: Nose boom 8mm, GPS at tip, pitot static port forward, BEC airflow shielded
- `p7` Camera Gimbal Bay: Forward downward camera gimbal bay 70mm deep, 2-axis micro gimbal, optical window
- `p8` Battery Bay (Slide): 4S 16000mAh Li-ion slide-in bay, CG adjust slot, top access hatch, balance lead window
- `p9` Integration Service Backbone: Wing/fuselage integration service backbone with assembly_datum pads, harness_raceway, service_hatch, connector_keying, anti-rotation wing datum, and visible load-path inspection marks

### tiltrotor

- domain: aero/propulsion mount/tilt mechanism

- `p1` Center Fuselage Spine: CFRP box beam center fuselage, avionics bay, wing spar socket, front GPS boom mount, belly camera window
- `p2` Main Wing (2-piece): Straight wing, 4S NACA 2412, dual 15mm CFRP spar, 900mm half-span, 160mm chord, 3-layer CFRP skin
- `p3` Nacelle Assembly x 2: Tilting nacelle assembly, 0-90deg tilt axis, 6309 bearing set, servo-driven worm gear, motor and ESC pocket
- `p4` Tilt Servo + Linkage x 2: 25kg-cm DS3218 servo per nacelle, titanium pushrod, dual ball joints, tilt range 0-93deg, crash-tolerant
- `p5` V-Tail x 2 (Ruddervator): +-35deg V-tail ruddervator pair, MG996R servo each, 30deg dihedral, CFRP sandwich panel, hinge piano wire
- `p6` Landing Gear (Tri): Tricycle landing gear, spring-steel skid arms, 55mm dia wheels, CG at 1/3 chord, 200mm wheelbase
- `p7` Battery Bay (Slide-In): Belly slide-in battery bay, 6S 8000mAh Li-ion pack, Velcro + strap dual retention, CG position 28% MAC
- `p8` Payload Nose Bay: Interchangeable nose payload bay, Day/IR camera gimbal or survey sensor, 80x60x50mm, 300g payload limit
- `p9` Tilt-Axis Harness + Datum Service Bay: Tiltrotor integration_service module with tilt-axis harness_channel, slack_loop, interface_datum, service_hatch, connector keying, and nacelle-to-wing load-path inspection access

### robot_arm

- domain: serial mechanism/joints/links/cable spine

- `p1` Base Joint (J1): Base rotary joint J1, +-180deg, harmonic drive, 100Nm peak torque, mounting flange ISO 9409
- `p2` Shoulder Joint (J2): Shoulder pitch joint J2, +-120deg, harmonic drive, 80Nm, cable routing through center bore
- `p3` Upper Arm (Link 2-3): Upper arm link, 300mm length, hollow tube with cable conduit, lightweight Al 7075
- `p4` Elbow Joint (J3): Elbow pitch joint J3, +-150deg, cycloidal reducer, 50Nm, encoder dual-stack
- `p5` Forearm + Wrist (J4): Forearm with wrist roll J4, 250mm length, +-360deg continuous, slip ring for power/signal
- `p6` Wrist Pitch (J5): Wrist pitch joint J5, +-120deg, harmonic drive, 20Nm, compact form factor
- `p7` Wrist Roll (J6): Wrist final roll joint J6, +-360deg, harmonic drive, 10Nm, ISO 9409-1 50mm tool flange
- `p8` Tool Flange + Changer: Tool changer master plate at J6 end, pneumatic locking, 4 utility ports
- `p9` Cable Management Spine: External cable carrier from base to wrist, drag chain or spiral, signal + power + pneumatic
- `p10` Replaceable Motor Module Set: Actuation_motors closure module: replaceable motor_module cartridges for J1-J6, fastener_access, coupling_reference article, insert/washer preload pads, torque_Nm intent labels
- `p11` Encoder Cover + Sensing Set: Sensing_encoders closure module: encoder_pocket and encoder_cover at each joint, index marks, cable exit strain relief, inspection labels
- `p12` Drive Electronics Bay: Drive_electronics bay with driver_bay, power_channel, signal_channel, ground_point, service cover, connector keying, thermal inspection window

### small_launch_vehicle

- domain: academic aerospace shell/staged study boundary

- `p1` Stage 1 Combustion Chamber Academic Study Section: Non-operational academic educational engine_academic study cartridge: combustion_chamber_reference article, injector-face visual insert, cutaway_window, slide_rail, academic boundary: no operational pressure, ignition, or flight-use instruction
- `p2` Stage 1 Bell Nozzle Cutaway Study Shell: Non-operational academic bell_nozzle_shell academic study structure with cutaway_window, bolt_circle_reference article, throat label, removable engine_study_cartridge interface
- `p3` Turbopump Assembly Academic Study Section: Non-operational academic turbopump_assembly_reference article with impeller_reference article, service cutaway bay, slide_rail, inspection label, no pump performance sizing claim
- `p4` Propellant Tank Reference Article (LOX): Primary_structure tank_reference article barrel for academic study only: propellant_tank_reference article, dome caps, alignment_key, inspection_window, no pressure-vessel certification claim
- `p5` Propellant Tank Reference Article (Fuel): Primary_structure fuel tank_reference article barrel for academic study only: propellant_tank_reference article, fill/drain labels, alignment_key, bolt_circle_reference article, no operational fluid-service instruction
- `p6` Interstage Adapter + Separation Datum: Separation_academic study structure: separation_plane_datum, clamp_band_reference article, interstage_datum, alignment_key, no energetic-device, pyro, or deployment instruction
- `p7` Stage 2 Engine Academic Study Section: Non-operational academic stage_engine_study with bell_nozzle_shell, cutaway_window, engine_study_cartridge slide_rail, educational label only
- `p8` Payload Fairing Cutaway Study Shell: Primary_structure payload_fairing/nose_cone cutaway study shell with split seam, inspection window, acoustic blanket labels, no flight-performance or flight-readiness claim
- `p9` Fin Set x 4 Academic Study Structure: Primary_structure fin_set academic study structure with root tabs, alignment_key, bolt_circle_reference article, inspection callouts, no stability/performance or flight-readiness claim
- `p10` Avionics Bay Reference Structure Tray: Avionics_bay educational tray with board_standoff, harness_passthrough, connector labels, EMI shield reference structure, no ordnance or flight computer authority
- `p11` Battery/Power Academic Study Module: Power_study battery_module reference article with access_panel, keyed connector label, service cover, mass budget note, no live-energy assembly instruction
- `p12` Recovery Bay Academic Study Section: Recovery_bay educational academic study section with deploy_door, hinge, parachute volume label, inspection window, no deployment-charge or flight-recovery instruction
- `p13` Integration Inspection Ring: Integration_inspection ring with assembly_datum pads, inspection_window, checklist_callout, connection type labels, load-path closure marks

### inline_6_engine_gasoline

- domain: IC engine/gasoline cranktrain/valvetrain/manifolds

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

### inline_6_engine_diesel

- domain: IC engine/diesel reinforced block/common rail/turbo

- `p1` Reinforced Cylinder Block: Diesel I6 block with thick deck, six bores, cross-bolted main cap cues, coolant jacket, oil gallery
- `p2` Forged Crankshaft + Bearing Ladder: Heavy crankshaft and bearing ladder with main caps, thrust face, oil feeds, flywheel flange
- `p3` Piston/Rod Assembly x 6: Diesel piston/rod educational set with bowl crown cue, wrist pin boss, rod cap bolts, ring bands
- `p4` Cylinder Head + Injector Wells: Diesel head with injector wells, glow plug ports, valve bridge, intake/exhaust ports, gasket datum
- `p5` Common Rail + Injector Harness: Common-rail layout reference structure with rail brackets, injector pockets, return line path, harness channel; non-operational academic low-detail reference
- `p6` Turbocharger + Exhaust Manifold Reference Structure: Turbo/exhaust academic study structure with turbine housing shell, compressor shell, oil feed/return bosses, heat shield
- `p7` Intake/EGR Cooler Path Reference Structure: Charge-air/EGR cooler routing reference structure with flanges, gasket faces, bypass/service cover, sensor bosses
- `p8` Oil Cooler + Filter Module: Oil cooler/filter module with cartridge cap, coolant ports, gasket face, drain boss
- `p9` Timing Gear Housing: Front gear housing with idler gear pockets, crank/cam gear datums, service cover, seal bore
- `p10` Engine Mount + Bellhousing Interfaces: Mount brackets and bellhousing adapter pattern with datum pads, bolt groups, lifting lug cues

### centrifugal_pump

- domain: rotating fluid machinery/volute/impeller/seal

- `p1` Volute Casing: Spiral volute casing with inlet eye, outlet flange, pressure boundary, drain plug, inspection boss
- `p2` Impeller: Closed impeller with hub, blade channels, wear ring face, balance drill cues
- `p3` Pump Shaft: Stepped shaft with keyway, impeller nut, bearing journals, coupling end
- `p4` Bearing Housing: Bearing frame with front/rear bearing seats, grease ports, oil sight window, mounting feet
- `p5` Mechanical Seal Cartridge: Seal cartridge reference structure with gland plate, O-ring groove, flush port, leakage drain
- `p6` Suction/Discharge Flange Set: ANSI-style flanges with bolt circle, gasket face, flow arrow, pipe alignment datum
- `p7` Coupling Guard + Motor Adapter: Motor adapter and coupling guard with service window, fastener tabs, alignment slots
- `p8` Baseplate + Mount Pads: Baseplate with slotted mount holes, leveling pads, drain channel, lifting points

### hydraulic_manifold

- domain: fluid power block/ports/valves/galleries

- `p1` Main Manifold Block: CNC manifold block with P/T/A/B ports, cross-drilled galleries, plug bosses, datum faces
- `p2` Cartridge Valve Set: Screw-in cartridge valve cavities with O-ring lands, wrench clearance, port labels
- `p3` Pressure Relief Valve Section: Relief valve pocket, adjustment cap, spring chamber cue, tank return path
- `p4` Check Valve Section: Check valve cavity with flow arrow, seat cone cue, service plug
- `p5` Sensor + Test Port Set: Pressure transducer boss, test coupler port, cable exit, protective cover
- `p6` Mounting Feet + Label Plate: Mounting feet, engraved circuit label plate, orientation arrows, service side datum

### battery_pack_module

- domain: power electronics/cells/busbars/BMS/enclosure

- `p1` Cell Carrier Tray: Cell holder tray with repeated cell pockets, compression pads, locator ribs, module datum
- `p2` Busbar + Fuse Cover Reference Structure: Insulated busbar reference structure with fuse windows, terminal guards, polarity labels, no live-energy claim
- `p3` BMS Electronics Bay: BMS board pocket, sensing harness channels, service connector, EMI shield cover
- `p4` Cooling Plate Interface: Cooling plate contact face, thermal pad zones, inlet/outlet ports, leak inspection channel
- `p5` Pack Enclosure + Lid: Gasketed enclosure shell with lid flange, fastener pattern, vent path, service label
- `p6` HV Connector + Service Disconnect Reference Structure: Keyed HV connector reference structure, service disconnect handle, low-voltage connector, strain relief
- `p7` Crash/Isolation End Plates: End plates with crush ribs, isolation spacers, tie rod bosses, lifting tabs

### liquid_cold_plate

- domain: thermal management/channels/manifold/gasket

- `p1` Cold Plate Body: Machined plate body with serpentine channel, fin islands, mounting bosses, flatness datum
- `p2` Inlet/Outlet Manifold Cap: Manifold cap with hose barb/AN port faces, O-ring groove, flow arrow, fastener pattern
- `p3` Gasket + Seal Track: Continuous gasket groove, compression stops, leak witness channel, corner reliefs
- `p4` Power Module Mount Pads: IGBT/MOSFET mount pads, thermal paste zones, isolation washer pockets, sensor pad
- `p5` Leak Test + Drain Ports: Pressure test port, drain plug, bleed screw, service labels
- `p6` Cover Plate: Bolted cover with ribbing, datum pins, inspection window label, torque sequence marks

### cnc_axis_carriage

- domain: precision motion/rails/ballscrew/sensors/lube

- `p1` Carriage Plate: Machined carriage with rail block bolt pattern, datum edge, dowel holes, lightening pockets
- `p2` Linear Rail Pair + Bearing Blocks: Two linear rails with four bearing block footprints, grease ports, rail datum references
- `p3` Ball Screw + Nut Housing: Ball screw shaft, nut housing, fixed/floating bearing ends, preload label
- `p4` Servo Motor Mount + Coupling Guard: Servo flange, coupling guard, belt/shaft alignment datum, service slots
- `p5` Limit/Home Sensor Brackets: Home and limit switch brackets, cable channel, target flag, adjustment slots
- `p6` Way Cover + Wiper Set: Telescoping way cover reference structure, wiper lip, chip guard, fastener tabs
- `p7` Lubrication Manifold: Lubrication ports, distribution channels, grease nipples, service labels

### gearbox_reducer

- domain: rotating power transmission/gears/shafts/bearings

- `p1` Split Gearbox Housing: Split housing with bearing bores, gasket flange, ribbing, inspection cover
- `p2` Input Shaft + Pinion: Input shaft with pinion gear, keyway, seal journal, bearing seats
- `p3` Intermediate Shaft + Gear Pair: Intermediate compound gear shaft with two gears, spacer, bearing seats
- `p4` Output Shaft + Bull Gear: Output shaft with bull gear, output flange, keyway, bearing support
- `p5` Bearing + Seal Set: Bearing cartridges, oil seals, shims, retainer plates
- `p6` Lubrication + Breather System: Oil fill/drain/level plugs, splash baffle, breather cap, sight glass
- `p7` Mounting Feet + Torque Arm: Mount feet, torque arm boss, dowel pads, bolt groups

### underwater_sealed_sensor_housing

- domain: marine sealed enclosure/O-rings/cable gland

- `p1` Cylindrical Pressure Shell: Cylindrical housing shell with wall-thickness cue, internal rail slots, external cradle pads
- `p2` Front Sensor Window Cap: Front cap with optical/acoustic window, O-ring groove, retaining ring, anti-rotation pins
- `p3` Rear Service Cap: Rear cap with double O-ring cue, service screws, puller holes, orientation mark
- `p4` Cable Gland + Strain Relief: Wet-mate cable gland reference structure, bend relief boot, potting pocket, connector key
- `p5` Internal Electronics Tray: Slide-in board tray, sensor board standoffs, desiccant pocket, ground lug
- `p6` Mounting Cradle + Anode Pad: ROV/vehicle cradle with clamp bands, sacrificial anode pad, drain path, lifting tab
- `p7` Leak Test Port + Label Set: Leak test plug, pressure label, inspection witness groove, serial plate

### liquid_rocket_engine_academic

- domain: academic liquid rocket propulsion/chamber/cooling/feed/instrumentation boundary

- `p1` Combustion Chamber Heat-Transfer Study Section: Academic chamber section with liner/jacket zones, heat-transfer labels, sensor bosses, flange datums, and no operational pressure/thrust sizing
- `p2` Injector Architecture Taxonomy Plate: Non-buildable injector concept plate comparing injector families with blocked detail holes, manifold zones, face datum, and no orifice dimensions
- `p3` Nozzle Contour Phenomena Study Shell: Nozzle contour study shell with throat/exit/station labels, thermal/structural callouts, cutaway window, and no expansion-ratio performance claim
- `p4` Regenerative Cooling Path Study Jacket: Cooling-path teaching jacket with channel-route vocabulary, inlet/outlet interface labels, leak-inspection path, and no flow-rate/sizing recipe
- `p5` Feed-System Architecture Manifold: Conceptual oxidizer/fuel feed manifold map with valve/filter/check-element placeholders, port labels, isolation zones, and no propellant handling instruction
- `p6` Turbopump Energy-Path Study Module: Academic turbopump module showing pump/turbine/shaft/bearing regions, energy-path arrows, service covers, and no performance/speed sizing
- `p7` Instrumentation + Data Acquisition Ring: Sensor boss ring, harness channels, DAQ connector zones, calibration labels, and safe measurement vocabulary without operating procedure
- `p8` Control Logic + Interlock Panel: Conceptual control/interlock panel with state labels, inhibit blocks, connector keying, and no ignition/start sequence instructions
- `p9` Thrust-Frame Load-Path Study Mount: Academic thrust-frame/mount interface with trunnion pads, load-path arrows, bolted datum pads, and no flight qualification claim
- `p10` Cutaway Safety Boundary + Annotation Cover: Transparent cutaway cover and annotation frame that marks non-buildable academic boundaries, blocked parameters, and inspection labels

## Overlap Audit

These are token-overlap candidates, not automatic duplicates. Many are intentional reusable engineering vocabulary such as cable, bearing, sensor, mount, gasket, or service cover.

| Score | Classification | Part A | Part B | Shared Terms |
| ---: | --- | --- | --- | --- |
| 0.522 | review_same_seed_possible_duplicate | `small_launch_vehicle/p2` Stage 1 Bell Nozzle Cutaway Study Shell | `small_launch_vehicle/p7` Stage 2 Engine Academic Study Section | academic, bell, cartridge, cutaway, engine, label, non, nozzle, operational, shell, stage, window |
| 0.500 | possible_functional_overlap | `inline_6_engine_gasoline/p1` Cylinder Block + Crankcase | `inline_6_engine_diesel/p1` Reinforced Cylinder Block | block, bores, cap, coolant, cues, cylinder, deck, gallery, jacket, main, oil, six |
| 0.500 | possible_functional_overlap | `inline_6_engine_gasoline/p4` Cylinder Head + DOHC Valvetrain | `inline_6_engine_diesel/p4` Cylinder Head + Injector Wells | cylinder, datum, exhaust, gasket, head, intake, plug, ports, valve, wells |
| 0.444 | generic_engineering_vocabulary_overlap | `inline_6_engine_gasoline/p2` Crankshaft + Main Bearing Set | `inline_6_engine_diesel/p2` Forged Crankshaft + Bearing Ladder | bearing, crankshaft, face, flange, flywheel, main, oil, thrust |
| 0.400 | intentional_cross_domain_harness_overlap | `long_range_recon_wing/p9` Integration Service Backbone | `tiltrotor/p9` Tilt-Axis Harness + Datum Service Bay | connector, datum, harness, hatch, inspection, integration, keying, load, path, wing |
| 0.370 | intentional_cross_domain_power_overlap | `haptic_glove/p9` Wiring Loom + Service Loop Set | `haptic_glove/p12` Service Port + Flex-Wiring Inspection Cover | bend, flex, loop, power, radius, relief, separation, signal, strain, wiring |
| 0.367 | intentional_study_boundary_overlap | `small_launch_vehicle/p1` Stage 1 Combustion Chamber Academic Study Section | `small_launch_vehicle/p7` Stage 2 Engine Academic Study Section | academic, cartridge, cutaway, educational, engine, non, operational, rail, slide, stage, window |
| 0.357 | possible_functional_overlap | `small_launch_vehicle/p4` Propellant Tank Reference Article (LOX) | `small_launch_vehicle/p5` Propellant Tank Reference Article (Fuel) | academic, alignment, article, barrel, key, only, propellant, reference, structure, tank |
| 0.353 | generic_engineering_vocabulary_overlap | `inline_6_engine_gasoline/p7` Timing Chain Front Cover | `inline_6_engine_diesel/p9` Timing Gear Housing | bore, cam, crank, front, seal, timing |
| 0.346 | intentional_cross_domain_harness_overlap | `cubesat/p12` Integration Harness + Datum Spine | `long_range_recon_wing/p9` Integration Service Backbone | connector, datum, harness, hatch, inspection, integration, keying, marks, pads |
| 0.333 | possible_functional_overlap | `centrifugal_pump/p7` Coupling Guard + Motor Adapter | `cnc_axis_carriage/p4` Servo Motor Mount + Coupling Guard | alignment, coupling, guard, motor, slots |
| 0.333 | possible_functional_overlap | `cubesat/p12` Integration Harness + Datum Spine | `small_launch_vehicle/p13` Integration Inspection Ring | checklist, closure, datum, inspection, integration, labels, marks, pads |
| 0.333 | possible_functional_overlap | `liquid_cold_plate/p5` Leak Test + Drain Ports | `underwater_sealed_sensor_housing/p7` Leak Test Port + Label Set | leak, plug, port, pressure, test |
| 0.308 | intentional_cross_domain_harness_overlap | `cubesat/p12` Integration Harness + Datum Spine | `tiltrotor/p9` Tilt-Axis Harness + Datum Service Bay | channel, connector, datum, harness, hatch, inspection, integration, keying |
| 0.308 | generic_engineering_vocabulary_overlap | `gearbox_reducer/p2` Input Shaft + Pinion | `gearbox_reducer/p4` Output Shaft + Bull Gear | bearing, gear, keyway, shaft |
| 0.300 | generic_engineering_vocabulary_overlap | `robot_arm/p1` Base Joint (J1) | `robot_arm/p7` Wrist Roll (J6) | 9409, drive, flange, harmonic, iso, joint |
| 0.294 | possible_functional_overlap | `robot_arm/p2` Shoulder Joint (J2) | `robot_arm/p6` Wrist Pitch (J5) | 120deg, drive, harmonic, joint, pitch |
| 0.294 | intentional_study_boundary_overlap | `small_launch_vehicle/p1` Stage 1 Combustion Chamber Academic Study Section | `small_launch_vehicle/p2` Stage 1 Bell Nozzle Cutaway Study Shell | academic, article, cartridge, cutaway, engine, non, operational, reference, stage, window |
| 0.292 | possible_functional_overlap | `long_range_recon_wing/p2` Wing Spar (2-piece) | `tiltrotor/p2` Main Wing (2-piece) | cfrp, half, main, piece, span, spar, wing |
| 0.280 | possible_functional_overlap | `small_launch_vehicle/p3` Turbopump Assembly Academic Study Section | `small_launch_vehicle/p7` Stage 2 Engine Academic Study Section | academic, cutaway, label, non, operational, rail, slide |
| 0.276 | possible_functional_overlap | `small_launch_vehicle/p4` Propellant Tank Reference Article (LOX) | `small_launch_vehicle/p9` Fin Set x 4 Academic Study Structure | academic, alignment, article, claim, inspection, key, reference, structure |
| 0.276 | possible_functional_overlap | `small_launch_vehicle/p5` Propellant Tank Reference Article (Fuel) | `small_launch_vehicle/p9` Fin Set x 4 Academic Study Structure | academic, alignment, article, bolt, circle, key, reference, structure |
| 0.269 | intentional_cross_domain_harness_overlap | `inline_6_engine_gasoline/p9` Fuel Rail + Injector Harness | `inline_6_engine_diesel/p5` Common Rail + Injector Harness | harness, injector, low, pockets, rail, reference, structure |
| 0.269 | possible_functional_overlap | `long_range_recon_wing/p9` Integration Service Backbone | `small_launch_vehicle/p13` Integration Inspection Ring | datum, inspection, integration, load, marks, pads, path |
| 0.267 | generic_engineering_vocabulary_overlap | `gearbox_reducer/p2` Input Shaft + Pinion | `gearbox_reducer/p3` Intermediate Shaft + Gear Pair | bearing, gear, seats, shaft |
| 0.263 | intentional_cross_domain_harness_overlap | `battery_pack_module/p6` HV Connector + Service Disconnect Reference Structure | `underwater_sealed_sensor_housing/p4` Cable Gland + Strain Relief | connector, reference, relief, strain, structure |
| 0.261 | possible_functional_overlap | `battery_pack_module/p4` Cooling Plate Interface | `liquid_rocket_engine_academic/p4` Regenerative Cooling Path Study Jacket | channel, cooling, inlet, inspection, leak, outlet |
| 0.250 | possible_functional_overlap | `inline_6_engine_gasoline/p3` Piston + Connecting Rod Set x 6 | `inline_6_engine_diesel/p3` Piston/Rod Assembly x 6 | educational, pin, piston, ring, rod, wrist |
| 0.250 | generic_engineering_vocabulary_overlap | `inline_6_engine_gasoline/p5` Intake Manifold + Throttle Body | `inline_6_engine_gasoline/p9` Fuel Rail + Injector Harness | boss, fuel, gasoline, injector, rail, sensor |
| 0.250 | possible_functional_overlap | `small_launch_vehicle/p2` Stage 1 Bell Nozzle Cutaway Study Shell | `small_launch_vehicle/p3` Turbopump Assembly Academic Study Section | academic, article, cutaway, label, non, operational, reference |
| 0.242 | possible_functional_overlap | `small_launch_vehicle/p1` Stage 1 Combustion Chamber Academic Study Section | `small_launch_vehicle/p3` Turbopump Assembly Academic Study Section | academic, article, cutaway, non, operational, rail, reference, slide |
| 0.233 | possible_functional_overlap | `small_launch_vehicle/p5` Propellant Tank Reference Article (Fuel) | `small_launch_vehicle/p6` Interstage Adapter + Separation Datum | academic, alignment, article, instruction, key, reference, structure |
| 0.227 | intentional_cross_domain_harness_overlap | `small_launch_vehicle/p10` Avionics Bay Reference Structure Tray | `battery_pack_module/p3` BMS Electronics Bay | board, connector, emi, harness, shield |
| 0.226 | possible_functional_overlap | `small_launch_vehicle/p2` Stage 1 Bell Nozzle Cutaway Study Shell | `small_launch_vehicle/p5` Propellant Tank Reference Article (Fuel) | academic, article, bolt, circle, operational, reference, structure |
| 0.222 | intentional_cross_domain_power_overlap | `cubesat/p9` EPS Solar Charging Module | `small_launch_vehicle/p11` Battery/Power Academic Study Module | battery, budget, connector, mass, panel, power |
| 0.222 | possible_functional_overlap | `inline_6_engine_gasoline/p6` Exhaust Manifold + Heat Shield | `inline_6_engine_diesel/p6` Turbocharger + Exhaust Manifold Reference Structure | exhaust, heat, manifold, reference, shield, structure |
| 0.214 | possible_functional_overlap | `small_launch_vehicle/p3` Turbopump Assembly Academic Study Section | `small_launch_vehicle/p9` Fin Set x 4 Academic Study Structure | academic, article, claim, inspection, performance, reference |
| 0.211 | generic_engineering_vocabulary_overlap | `inline_6_engine_diesel/p10` Engine Mount + Bellhousing Interfaces | `gearbox_reducer/p7` Mounting Feet + Torque Arm | bolt, groups, mount, pads |
| 0.211 | possible_functional_overlap | `robot_arm/p6` Wrist Pitch (J5) | `robot_arm/p7` Wrist Roll (J6) | drive, harmonic, joint, wrist |
| 0.207 | possible_functional_overlap | `small_launch_vehicle/p8` Payload Fairing Cutaway Study Shell | `liquid_rocket_engine_academic/p3` Nozzle Contour Phenomena Study Shell | claim, cutaway, labels, performance, shell, window |
| 0.200 | generic_engineering_vocabulary_overlap | `centrifugal_pump/p3` Pump Shaft | `gearbox_reducer/p4` Output Shaft + Bull Gear | bearing, keyway, shaft |
| 0.200 | generic_engineering_vocabulary_overlap | `gearbox_reducer/p3` Intermediate Shaft + Gear Pair | `gearbox_reducer/p4` Output Shaft + Bull Gear | bearing, gear, shaft |
| 0.200 | possible_functional_overlap | `haptic_glove/p2` Finger Exo Linkage Cartridge x 10 | `haptic_glove/p6` Finger Thimble Interface Set | finger, hinge, pin, slip, thimble |
| 0.200 | possible_functional_overlap | `inline_6_engine_gasoline/p1` Cylinder Block + Crankcase | `inline_6_engine_diesel/p8` Oil Cooler + Filter Module | cap, coolant, face, gasket, oil |
| 0.200 | possible_functional_overlap | `small_launch_vehicle/p6` Interstage Adapter + Separation Datum | `small_launch_vehicle/p9` Fin Set x 4 Academic Study Structure | academic, alignment, article, key, reference, structure |
| 0.200 | possible_functional_overlap | `small_launch_vehicle/p8` Payload Fairing Cutaway Study Shell | `small_launch_vehicle/p9` Fin Set x 4 Academic Study Structure | claim, flight, inspection, performance, readiness, structure |
| 0.194 | possible_functional_overlap | `small_launch_vehicle/p2` Stage 1 Bell Nozzle Cutaway Study Shell | `small_launch_vehicle/p9` Fin Set x 4 Academic Study Structure | academic, article, bolt, circle, reference, structure |
| 0.194 | possible_functional_overlap | `small_launch_vehicle/p4` Propellant Tank Reference Article (LOX) | `small_launch_vehicle/p6` Interstage Adapter + Separation Datum | academic, alignment, article, key, reference, structure |
| 0.192 | generic_engineering_vocabulary_overlap | `haptic_glove/p3` Flexion-Resistance Actuator x 10 | `haptic_glove/p10` Knuckle Mount Rail x 2 | actuator, knuckle, mount, plug, row |
| 0.192 | generic_engineering_vocabulary_overlap | `inline_6_engine_gasoline/p5` Intake Manifold + Throttle Body | `inline_6_engine_gasoline/p6` Exhaust Manifold + Heat Shield | boss, flange, manifold, sensor, six |
| 0.192 | intentional_study_boundary_overlap | `small_launch_vehicle/p3` Turbopump Assembly Academic Study Section | `liquid_rocket_engine_academic/p6` Turbopump Energy-Path Study Module | academic, performance, pump, sizing, turbopump |
| 0.190 | intentional_cross_domain_harness_overlap | `inline_6_engine_gasoline/p9` Fuel Rail + Injector Harness | `battery_pack_module/p6` HV Connector + Service Disconnect Reference Structure | connector, low, reference, structure |
| 0.190 | possible_functional_overlap | `small_launch_vehicle/p13` Integration Inspection Ring | `liquid_cold_plate/p6` Cover Plate | datum, inspection, marks, window |
| 0.188 | possible_functional_overlap | `centrifugal_pump/p7` Coupling Guard + Motor Adapter | `cnc_axis_carriage/p6` Way Cover + Wiper Set | fastener, guard, tabs |
| 0.188 | generic_engineering_vocabulary_overlap | `centrifugal_pump/p3` Pump Shaft | `gearbox_reducer/p2` Input Shaft + Pinion | bearing, keyway, shaft |
| 0.185 | intentional_cross_domain_power_overlap | `haptic_glove/p12` Service Port + Flex-Wiring Inspection Cover | `robot_arm/p12` Drive Electronics Bay | connector, inspection, keying, power, signal |
| 0.185 | possible_functional_overlap | `tiltrotor/p9` Tilt-Axis Harness + Datum Service Bay | `small_launch_vehicle/p13` Integration Inspection Ring | datum, inspection, integration, load, path |
| 0.174 | possible_functional_overlap | `cubesat/p2` Solar Panel x 4 (deploy) | `cubesat/p3` Antenna Deployer x 2 | burn, release, spring, wire |
| 0.174 | intentional_cross_domain_harness_overlap | `haptic_glove/p4` Adjustable Wrist Band x 2 | `haptic_glove/p5` Cable Raceway + Harness Cover x 2 | band, cable, raceway, wrist |
| 0.172 | possible_functional_overlap | `small_launch_vehicle/p3` Turbopump Assembly Academic Study Section | `inline_6_engine_diesel/p5` Common Rail + Injector Harness | academic, non, operational, rail, reference |
| 0.167 | possible_functional_overlap | `small_launch_vehicle/p3` Turbopump Assembly Academic Study Section | `small_launch_vehicle/p4` Propellant Tank Reference Article (LOX) | academic, article, claim, inspection, reference |
| 0.162 | possible_functional_overlap | `small_launch_vehicle/p1` Stage 1 Combustion Chamber Academic Study Section | `inline_6_engine_diesel/p5` Common Rail + Injector Harness | academic, injector, non, operational, rail, reference |
| 0.161 | intentional_cross_domain_harness_overlap | `cubesat/p10` CDH Avionics Stack | `small_launch_vehicle/p10` Avionics Bay Reference Structure Tray | avionics, board, connector, harness, labels |
| 0.161 | intentional_cross_domain_power_overlap | `cubesat/p11` Thermal Path / Radiator Strap Evidence | `small_launch_vehicle/p11` Battery/Power Academic Study Module | battery, budget, label, mass, note |
| 0.161 | intentional_study_boundary_overlap | `small_launch_vehicle/p2` Stage 1 Bell Nozzle Cutaway Study Shell | `liquid_rocket_engine_academic/p3` Nozzle Contour Phenomena Study Shell | cutaway, nozzle, shell, throat, window |
| 0.160 | intentional_cross_domain_power_overlap | `haptic_glove/p8` Battery + Power Module x 2 | `robot_arm/p12` Drive Electronics Bay | connector, keying, power, window |
| 0.160 | intentional_cross_domain_harness_overlap | `robot_arm/p11` Encoder Cover + Sensing Set | `underwater_sealed_sensor_housing/p4` Cable Gland + Strain Relief | cable, pocket, relief, strain |
| 0.160 | possible_functional_overlap | `small_launch_vehicle/p13` Integration Inspection Ring | `liquid_rocket_engine_academic/p9` Thrust-Frame Load-Path Study Mount | datum, load, pads, path |
| 0.156 | possible_functional_overlap | `small_launch_vehicle/p2` Stage 1 Bell Nozzle Cutaway Study Shell | `inline_6_engine_diesel/p5` Common Rail + Injector Harness | academic, non, operational, reference, structure |
| 0.154 | intentional_cross_domain_harness_overlap | `cubesat/p12` Integration Harness + Datum Spine | `robot_arm/p12` Drive Electronics Bay | channel, connector, inspection, keying |
| 0.154 | intentional_cross_domain_harness_overlap | `haptic_glove/p5` Cable Raceway + Harness Cover x 2 | `robot_arm/p11` Encoder Cover + Sensing Set | cable, inspection, relief, strain |
| 0.154 | possible_functional_overlap | `robot_arm/p11` Encoder Cover + Sensing Set | `small_launch_vehicle/p13` Integration Inspection Ring | closure, inspection, labels, marks |
| 0.154 | possible_functional_overlap | `small_launch_vehicle/p3` Turbopump Assembly Academic Study Section | `inline_6_engine_gasoline/p8` Oil Pan + Pump Pickup | article, pump, rail, reference |
| 0.154 | intentional_cross_domain_harness_overlap | `tiltrotor/p9` Tilt-Axis Harness + Datum Service Bay | `robot_arm/p12` Drive Electronics Bay | channel, connector, inspection, keying |
| 0.152 | possible_functional_overlap | `small_launch_vehicle/p2` Stage 1 Bell Nozzle Cutaway Study Shell | `small_launch_vehicle/p4` Propellant Tank Reference Article (LOX) | academic, article, reference, structure, window |
| 0.148 | generic_engineering_vocabulary_overlap | `haptic_glove/p10` Knuckle Mount Rail x 2 | `liquid_rocket_engine_academic/p9` Thrust-Frame Load-Path Study Mount | datum, mount, pads, path |
| 0.148 | generic_engineering_vocabulary_overlap | `inline_6_engine_gasoline/p6` Exhaust Manifold + Heat Shield | `inline_6_engine_diesel/p7` Intake/EGR Cooler Path Reference Structure | gasket, reference, sensor, structure |
| 0.148 | generic_engineering_vocabulary_overlap | `inline_6_engine_gasoline/p6` Exhaust Manifold + Heat Shield | `inline_6_engine_gasoline/p9` Fuel Rail + Injector Harness | boss, reference, sensor, structure |
| 0.148 | possible_functional_overlap | `small_launch_vehicle/p3` Turbopump Assembly Academic Study Section | `small_launch_vehicle/p11` Battery/Power Academic Study Module | academic, article, label, reference |
| 0.148 | possible_functional_overlap | `small_launch_vehicle/p7` Stage 2 Engine Academic Study Section | `small_launch_vehicle/p12` Recovery Bay Academic Study Section | academic, educational, label, window |

## Readout

- No exact duplicate BOM part IDs exist across seeds because IDs are seed-local.
- Repeated themes like battery, harness, cable, bearing, sensor, mount, seal, and service cover are expected; they are shared engineering primitives.
- Real duplication to watch is same seed/same function duplication, or cross-seed items with identical role and no domain-specific boundary.
- The rocket/launch entries intentionally overlap with `liquid_rocket_engine_academic`, but the latter is held to a non-buildable academic propulsion-study boundary.