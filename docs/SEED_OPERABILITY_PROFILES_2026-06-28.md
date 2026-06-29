# Seed Operability Profiles - 2026-06-28

All 16 seeds now carry an `operability_profile` in their skeleton and PASS-1 micro-packs.
The profile forces generation toward operation-aware structure, multiphysics path tracing, and solver readiness.

| Seed | Operating Principle | Solver Focus |
| --- | --- | --- |
| `battery_pack_module` | No-live-energy battery module architecture that organizes cell support, busbar covers, BMS, thermal interface, venting, isolation, and service disconnect grammar. | thermal spreading, isolation/clearance review, vent path topology |
| `centrifugal_pump` | Rotating fluid machine that converts shaft power to pressure/flow through impeller and volute while sealing leakage and carrying bearing loads to baseplate. | OpenFOAM volute/impeller domain, bearing/shaft FEA, seal leak path review |
| `cnc_axis_carriage` | Precision linear axis that constrains travel with rails/bearing blocks, drives motion through a screw/motor, protects ways, and routes sensors/lubrication. | carriage stiffness FEA, motion clearance, lube routing |
| `cubesat` | Small spacecraft architecture that routes loads through rails/frame, power through EPS/battery/solar, data through avionics stack, and heat to radiator/structure paths. | modal/launch-load FEA, thermal balance proxy, harness clearance review |
| `gearbox_reducer` | Two-stage reducer that carries torque through gear meshes, supports shafts with bearings, manages lubrication/sealing, and reacts loads through housing mounts. | housing FEA, lubrication topology, thermal heat rejection |
| `haptic_glove` | Wearable robotic hand interface that transfers finger motion through linkages/cables while preserving ergonomic fit, sensor routing, and safe contact surfaces. | linkage clearance, ergonomic contact pressure, cable bend radius |
| `hydraulic_manifold` | Hydraulic block architecture that routes pressure/return/work ports through drilled galleries, cartridge valves, plugs, sensors, and service labels. | gallery pressure-loss CFD, block stress around ports, service access |
| `inline_6_engine_diesel` | Diesel engine architecture study with reinforced block/head, heavy cranktrain, common-rail topology, turbo air path, cooling/lubrication, and service datums. | reinforced housing FEA, air/exhaust routing CFD proxy, thermal shielding |
| `inline_6_engine_gasoline` | Internal combustion engine architecture study that coordinates cranktrain rotation, gas exchange, cooling, lubrication, fuel/ignition harness, and service access. | coolant/oil passage review, block/head thermal path, mount/load FEA |
| `liquid_cold_plate` | Thermal management plate that transfers heat from electronics pads into internal liquid channels and manifold ports while maintaining gasket/leak boundaries. | OpenFOAM channel flow, thermal conduction/convection, gasket compression review |
| `liquid_rocket_engine_academic` | Academic liquid propulsion architecture study linking chamber/nozzle, injector taxonomy, regenerative cooling, feed topology, turbomachinery, instrumentation, controls, and thrust-frame load path. | topology-only CFD/thermal study, thrust-frame FEA, instrumentation/control review |
| `long_range_recon_wing` | Fixed-wing UAV architecture that carries lift through spar/rib stations, routes propulsion/power through the fuselage, and isolates payload/sensor bays. | aero CFD proxy/OpenFOAM case, wing bending FEA, payload bay cooling |
| `robot_arm` | Serial manipulator architecture that carries torque through joints/links, routes cables along the spine, and exposes serviceable actuator/sensor modules. | joint torque/FoS screening, cable bend and service access, link stiffness |
| `small_launch_vehicle` | Academic launch-vehicle architecture study that separates stage shell, tank reference articles, avionics, recovery, and propulsion study sections for reviewable load/path grammar. | stage shell FEA, thermal zone annotation, non-operational topology review |
| `tiltrotor` | VTOL aircraft architecture that transitions thrust vector through nacelle tilt axes while preserving wing load paths, slack-loop harnesses, and control authority. | tilt-axis joint FEA, rotor/wing flow interaction proxy, harness slack clearance |
| `underwater_sealed_sensor_housing` | Sealed marine electronics housing that carries pressure loads through shell/caps, routes cable penetration safely, and supports internal sensor/electronics trays. | pressure shell FEA, seal/gland leak boundary, thermal dissipation to water |

## Applied Files

- profiles: 16
- pack files updated: 127

High-risk seeds keep physics-grounded analysis intent while blocking unsafe operational recipes.
