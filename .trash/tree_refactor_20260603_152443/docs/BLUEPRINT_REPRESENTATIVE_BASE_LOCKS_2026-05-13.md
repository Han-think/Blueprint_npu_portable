# Blueprint Representative Base Locks - 2026-05-13

This document locks the representative product family for every assembly template before superquality image production.

The representative basis is not a copy target. It is the structural reference used to keep silhouette, subsystem layout, and part mapping stable while producing original blueprint images.

## Locking Rules

- Do not change a representative basis during image generation.
- If a basis needs to change, update this document first, then update `Minimal.html`, then regenerate the inventory.
- A locked basis should guide all three assembly axes:
  - exterior
  - internal
  - top / part-zone
- Single-part images should inherit their parent assembly basis when the part is produced for an assembly workflow.

## Current Locked Bases

### Drone

| Vehicle ID | Locked Basis | Image Direction |
|---|---|---|
| `racing_quad_5in` | 5-inch FPV racing quad | X-frame, 5-inch prop disks, FC/ESC stack, camera mount, battery top deck |
| `cinelifter_x8` | DJI Inspire / X8 cinelifter class | Coaxial heavy-lift arms, central hub, gimbal clearance, landing struts |
| `wing_long_range` | Long-range fixed-wing UAV / flying wing | Center pod, long spar, wing ribs, pusher motor, pitot/GPS boom |
| `cyclocopter_demo` | Cyclogyro demonstrator | Four cyclorotor cylinders, pitch-linkage modules, pylon supports |
| `tiltrotor_vtol` | Tiltrotor VTOL UAV | Fixed wing, tilting nacelles, V-tail, battery/payload bays |

### Aerospace

| Vehicle ID | Locked Basis | Image Direction |
|---|---|---|
| `fighter_f_class` | F-15 Eagle / F-15EX class | Twin-engine fighter, twin inlets, twin nozzles, twin tails, stabilators |
| `turboprop_transport` | ATR 72 class | High wing, twin turboprop nacelles, large propellers, T-tail, cabin/ramp logic |
| `civil_airliner` | Airbus A320 family | Single-aisle tube-and-wing airliner, underwing turbofans, wing box, high-lift surfaces |
| `heavy_helicopter` | Boeing CH-47 Chinook class | Tandem rotors, forward/aft pylons, long cargo fuselage, rear ramp |
| `supersonic_sst` | Concorde class | Ogival delta wing, droop nose/visor, paired engine nacelles, variable intakes |

### Space

| Vehicle ID | Locked Basis | Image Direction |
|---|---|---|
| `small_launch_vehicle` | Saturn V structural logic + Rocket Lab Electron scale class | Stage hierarchy, IU ring, tanks, interstage, fin can, clustered engines |
| `cubesat_3u` | 3U CubeSat / deployer rail standard | 3U frame, deployable panels, PC/104 stack, antennas, separation plate |
| `lunar_lander` | Apollo LM / Surveyor class | Central tank, descent engine, four legs, RCS pods, dish, deck structure |
| `space_telescope` | Hubble Space Telescope class | Optical tube, primary/secondary mirrors, service bay, arrays, aperture door |
| `orbital_module` | ISS pressurized module class | Pressure shell, CBM ports, rack decks, truss/radiator/solar structures |

### Marine

| Vehicle ID | Locked Basis | Image Direction |
|---|---|---|
| `rov_inspection` | BlueROV2 / inspection ROV class | Open frame, pressure housing, thrusters, buoyancy, camera dome, lights |
| `usv_autonomous` | Solar-electric survey ASV class | Catamaran hulls, cross deck, solar array, sensor mast, pod propulsion |
| `underwater_glider` | Slocum/Seaglider class | Pressure hull, fixed wings, buoyancy pump, moving battery, tail antenna |
| `research_submarine` | DSV Alvin / research mini-sub class | Pressure hull, viewport dome, ballast, science basket, thruster pods |
| `wave_glider_asv` | Liquid Robotics Wave Glider class | Surface float, submerged glider, tether, passive wave fins, solar deck |

### Robotics

| Vehicle ID | Locked Basis | Image Direction |
|---|---|---|
| `arm_6dof` | Universal Robots UR-class cobot | Serial 6-axis arm, joint housings, links, wrist stack, cable routing |
| `mars_rover` | Perseverance rover class | Rocker-bogie suspension, six wheels, body chassis, mast, science arm, HGA |
| `quadruped_walker` | Boston Dynamics Spot / ANYmal class | Four legs, hip/knee modules, body battery bay, sensor head, foot pads |
| `delta_parallel_robot` | Industrial delta robot | Fixed base, three actuated arms, parallelogram links, moving platform |
| `humanoid_biped` | Atlas / humanoid research robot class | Torso, head, arms, hip/knee/ankle chains, backpack/power structure |

### Medical

| Vehicle ID | Locked Basis | Image Direction |
|---|---|---|
| `myoelectric_hand` | Multi-articulating myoelectric prosthetic hand | Palm shell, finger linkages, tendon/cable routing, socket electronics |
| `powered_afo` | Powered ankle-foot orthosis class | Shin cuff, ankle actuator, footplate, linkage, sensor pods |
| `surgical_robot_arm` | Da Vinci surgical system class | Remote-center arm, instrument shaft, sterile interface, wrist/end effector |
| `cochlear_implant` | Cochlear implant receiver/electrode system | Receiver-stimulator coil, magnet, lead, electrode array curl |
| `powered_exoskeleton` | ReWalk/Ekso lower-body exoskeleton class | Hip/knee/ankle actuators, braces, backpack controller, foot sensors |

### Propulsion

| Vehicle ID | Locked Basis | Image Direction |
|---|---|---|
| `turbofan_engine` | CFM56 / LEAP high-bypass turbofan class | Fan, LPC/HPC, combustor, turbine, bypass duct, nacelle |
| `solid_rocket_motor` | HTPB composite SRM class | Case, insulation, star grain, igniter, nozzle, thrust vector/nozzle joint |
| `electric_motor_assy` | High-performance BLDC outrunner class | Stator, rotor can, magnets, windings, bearings, encoder/cooling |
| `marine_propeller` | Controllable-pitch propeller class | Hub, pitch mechanism, blade roots, hydraulic actuation, shaft flange |
| `ion_thruster_assy` | Hall-effect thruster class | Anode, magnetic circuit, discharge channel, cathode, xenon feed |

### Mechanical

| Vehicle ID | Locked Basis | Image Direction |
|---|---|---|
| `harmonic_drive` | Strain-wave harmonic drive | Wave generator, flex spline, circular spline, bearing stack |
| `suspension_assy` | Racing double-wishbone suspension | Upright, upper/lower arms, pushrod, damper, hub, brake mount |
| `cnc_tool_changer` | Umbrella-type CNC automatic tool changer | Carousel, tool pockets, index drive, toolholder gripper, spindle exchange |
| `hydraulic_cylinder` | Double-acting industrial hydraulic cylinder | Barrel, piston, rod, seals, ports, clevis, position sensor |
| `precision_linkage` | Four-bar Chebyshev precision linkage | Ground pivots, coupler, rocker/crank, bearings, straight-line path |

## Direction Corrections Already Applied

- `fighter_f_class` was changed from F-16 single-engine basis to F-15 twin-engine basis.
- `civil_airliner` was corrected from a twin-aisle label to an A320-family single-aisle basis.
- `heavy_helicopter` was corrected from a coaxial label to a CH-47-class tandem-rotor basis.
- `small_launch_vehicle` was corrected from an Electron-only basis to Saturn V structural logic plus Electron-class scale.

## Next Use

Before creating or revising a superquality image:

1. Check this representative lock document.
2. Check the category superquality spec.
3. Check the generated inventory for the exact part list.
4. Produce the image.
5. Protect hand-authored master assets from generator overwrite.
