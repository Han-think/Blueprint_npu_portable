# Realism Boundary Matrix - 2026-06-28

This project should push every seed toward real engineering behavior, not
cosmetic geometry. The boundary is not "fake versus real"; it is "reviewable
engineering realism versus unsafe or uncertified operational instruction."

## Status Clarification

- 16 seeds have BOMs, packs, reference-card hooks, and `operability_profile`.
- Reverse-engineering data currently exists mainly for the original 6 seeds.
- The reverse pipeline now supports all 16 seeds, but the expansion seeds need
  fresh generated candidates before full reverse-analysis rows can be produced.

## What We Can Make Real

- Part decomposition and subsystem roles.
- Assembly order, datums, fasteners, service access, and inspection points.
- Load paths, fluid paths, thermal paths, electrical paths, and signal paths.
- CAD feature grammar that supports STEP/STL/export and downstream review.
- First-order FoS, thermal, CFD/OpenFOAM readiness, and electrical/signal review.
- FMEA, tolerance-chain review, DFA/DFM review, cost/weight review.
- Solver-ready metadata: boundary conditions, named surfaces, mesh-risk notes,
  missing inputs, and promotion/blocking decisions.

## What We Must Not Claim Or Generate

- Certified or guaranteed working hardware.
- Unsafe operating setpoints, hazardous procedures, or flight/medical/pressure/
  high-voltage/propulsion operation instructions.
- Build-ready recipes for regulated or dangerous systems.
- Test-stand, ignition, propellant handling, flight qualification, live high-
  voltage, pressure-vessel certification, or medical-use instructions.

## Seed Matrix

| Seed | Push Toward Realism | Keep Blocked |
| --- | --- | --- |
| `cubesat` | Frame rails, PC/104 stack, EPS/solar harness, thermal paths, deployment interfaces, launch-load and thermal-balance readiness. | Flight certification, actual orbital operation approval, pyrotechnic/deployment actuation instructions. |
| `haptic_glove` | Ergonomic fit, finger linkages, cable/tendon routing, sensors, actuator mounting, contact-pressure and service review. | Medical/rehab treatment claims, unsafe force-feedback settings, certified wearable-device claims. |
| `long_range_recon_wing` | Spar/rib/bay layout, payload bay, battery/propulsion mounting, aero/structural topology, CFD/FEA readiness. | Flight-ready aircraft instructions, BVLOS compliance claims, weaponization or operational surveillance instructions. |
| `tiltrotor` | Tilt-axis bearing/linkage, nacelle load path, harness slack loops, rotor/wing flow review, transition-architecture analysis. | Flight qualification, real autopilot tuning, unsafe rotor operating procedures. |
| `robot_arm` | Joint/link load paths, reducers, cable spine, motor/encoder bays, tool flange, stiffness/FoS and service review. | Certified industrial safety claims, unsafe collaborative operation settings. |
| `small_launch_vehicle` | Stage stack, tank reference articles, avionics/recovery bays, chamber/nozzle study zones, thrust/load path, thermal annotations. | Propellant handling, ignition/start/test sequence, flight qualification, buildable propulsion or separation-device instructions. |
| `inline_6_engine_gasoline` | Block/head/cranktrain/manifold/cooling/lubrication/fuel-ignition harness topology and serviceable cutaway CAD. | Running-engine build recipe, emissions/performance certification, fuel handling or dyno operation procedure. |
| `inline_6_engine_diesel` | Reinforced block/head, cranktrain, common-rail topology, turbo air path, thermal shielding, service/inspection geometry. | High-pressure fuel-system build/operation instructions, emissions/performance certification. |
| `centrifugal_pump` | Volute/impeller/shaft/seal/bearing/baseplate assembly, pressure boundary review, OpenFOAM-ready flow topology. | Certified pressure equipment claims, hazardous-fluid operating procedures. |
| `hydraulic_manifold` | P/T/A/B port topology, drilled galleries, cartridge cavities, plugs, sensors, pressure-loss and block-stress review. | Rated hydraulic system certification, live high-pressure operating instructions. |
| `battery_pack_module` | Cell carrier, compression/end plates, busbar covers, BMS bay, cooling interface, vent path, isolation and service-disconnect grammar. | Live high-voltage assembly, charging/discharging procedures, certified battery safety claims. |
| `liquid_cold_plate` | Serpentine channels, manifold caps, gasket/leak boundaries, thermal pad zones, OpenFOAM and thermal solver readiness. | Rated pressure/thermal performance guarantee without solver/test evidence. |
| `cnc_axis_carriage` | Rail/bearing/screw/motor/sensor/lube architecture, stiffness, datum/tolerance stack, service and motion-clearance review. | Certified machine safety claims or unsafe machine operation instructions. |
| `gearbox_reducer` | Gear/shaft/bearing/housing/seal/oil topology, torque load path, lubrication and housing thermal review. | Rated gearbox performance certification without analysis/test evidence. |
| `underwater_sealed_sensor_housing` | Pressure shell/caps/O-rings/cable gland/electronics tray/cradle, leak-test metadata, pressure-shell FEA readiness. | Certified depth rating or pressure-vessel claim without qualified analysis/test. |
| `liquid_rocket_engine_academic` | Chamber/nozzle/feed/cooling/turbomachinery/instrumentation/control/thrust-frame topology, solver metadata, FMEA, review reports. | Buildable injector sizing, propellant handling, ignition/start/test procedures, operating pressure/thrust/mass-flow recipe, flight-use instruction. |

## Practical Rule

For every seed, the generator should answer:

1. What does this subsystem do in the real architecture?
2. Where do load, fluid, heat, power, and signal flow?
3. What geometry proves those paths exist?
4. What must be inspected, serviced, or analyzed?
5. What is missing before this could be promoted from study CAD to real hardware?

The last question is the key. The system should get as close to reality as
reviewably possible, then clearly mark the remaining gap instead of pretending
the design is already certified or safely buildable.
