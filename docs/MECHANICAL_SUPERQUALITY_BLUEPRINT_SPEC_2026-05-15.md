# Mechanical Superquality Blueprint Spec - 2026-05-15

Mechanical images and generated outputs must explain fits, forces, bearings, fasteners, adjustment, lubrication, and inspection.

## Category Rules

- Show shafts, bearings, seals, pins, bolt patterns, datum faces, lubrication points, and adjustment slots.
- Avoid generic housings without internal mechanics.
- Mechanisms must show input, output, constraints, and load path.
- Precision mechanisms must include tolerance/alignment cues.

## Assemblies

| Vehicle | Locked Basis | Must-Show Features | Reject If |
|---|---|---|---|
| `harmonic_drive` | strain-wave harmonic drive | wave generator, flexspline, circular spline, output flange, cross-roller bearing, seals, encoder mount | gear stages indistinguishable |
| `suspension_assy` | double wishbone suspension | upper/lower A-arms, upright, pushrod, rocker, damper, hub, brake mount, ARB link | no suspension kinematics |
| `cnc_tool_changer` | umbrella ATC | carousel, pockets, gripper fingers, cam drive, servo/gearbox, sensors, coolant blow-off, shroud | looks like plain disk |
| `hydraulic_cylinder` | double-acting cylinder | barrel, piston/rod, gland, end cap, tie rods, ports, seals, clevis, position sensor | rod/barrel only |
| `precision_linkage` | four-bar linkage | ground link, crank, coupler, rocker, pivot pins, bearings, encoder, adjustment eccentric | no four-bar geometry |

## Geometry Requirements

- Include fit-critical features: bores, pins, bearing seats, seal grooves, or datum surfaces.
- Include fastener/adjustment/lubrication details.
- Include one label/datum operation.
- For mechanisms, include input and output features.

## Promotion Criteria

- Generated 2D view shows how motion/load transfers.
- 3D output has more than outer shells.
- Validation/review can identify fits and interface surfaces.

