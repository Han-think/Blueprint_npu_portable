# Propulsion Superquality Blueprint Spec - 2026-05-15

Propulsion images and generated outputs must explain energy conversion and flow path. Generic cylinders, boxes, and unlabeled housings are not acceptable.

## Category Rules

- Show inlet, outlet, rotating/stationary boundary, pressure/thermal boundary, and service interfaces.
- Include seals, bearings, flanges, bolt circles, ports, cooling, wiring, or feed lines when relevant.
- Keep the functional axis obvious: airflow, propellant flow, shaft rotation, thrust vector, hydraulic pitch, or plasma plume.
- 2D review must show component hierarchy first; 3D review is secondary unless geometry operations are detailed.

## Assemblies

| Vehicle | Locked Basis | Must-Show Features | Reject If |
|---|---|---|---|
| `turbofan_engine` | CFM56 / LEAP high-bypass turbofan | fan, bypass duct, LPC/HPC, combustor, HPT/LPT, shaft/bearing line, nacelle mounts, accessory gearbox | looks like a plain tube or lacks flow stages |
| `solid_rocket_motor` | HTPB composite SRM | composite case, insulation, star grain, igniter, aft closure, nozzle throat/exit, flex joint/TVC, safe-arm boss | grain/nozzle/case hierarchy missing |
| `electric_motor_assy` | high-performance BLDC outrunner | stator teeth/windings, rotor can, magnets, shaft, bearings, encoder, cooling jacket, controller connector | rotor/stator distinction missing |
| `marine_propeller` | controllable-pitch propeller | hub body, blade root pivots, pitch actuator rod, OD box/slip ring, shaft flange, seal housing, anodes | fixed propeller silhouette only |
| `ion_thruster_assy` | Hall-effect thruster | annular discharge channel, anode, magnetic poles, hollow cathode, xenon feed, PPU connector, plume shield | looks like generic nozzle or no electric/plasma cues |

## Geometry Requirements

For generated part blueprints:

- Use `8-16` operations.
- Include at least one axial/flow feature.
- Include at least one interface feature: flange, boss, bolt circle, trunnion, connector, shaft, or pipe port.
- Include at least one maintenance/manufacturing cue: inspection port, split line, label, datum mark, access pocket, or alignment pin.

## Promotion Criteria

Promote from `train_aug_ready` to `train_base_ready` only when:

- 3-axis master image shows the correct energy/flow hierarchy.
- Part images match parent assembly flow direction.
- Generated outputs consistently include functional interfaces, not just outer shells.

