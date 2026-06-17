# Tiltrotor Drone Redesign V1

This document defines the second Blueprint NPU design-thinking sample.

## Purpose

The goal is not to create a flight-certified aircraft. The goal is to read an existing tiltrotor UAV structure, reason about its assembly and service tradeoffs, and produce a better 3D-printable educational mockup package.

V1 uses the `tiltrotor_vtol` asset because it has a clear serviceability boundary: the fuselage/spar/battery path can be simplified, but the tilting nacelles, tilt linkage, motor/ESC service pods, tail hinges, and landing gear must remain replaceable.

## Target Object

```text
Object: Tiltrotor VTOL Hybrid educational / exhibition mockup
Envelope: 1200 x 900 x 200 mm class reference, scaled for desktop printing
Manufacturing: FDM 3D printing
Primary material: PETG structural parts + TPU pads / bumpers
Primary metric: assembly / serviceability efficiency
Success output: design package before STL generation
```

## Engineering Rule Set

- Reducing part count is only a success when nacelle, tilt axis, servo linkage, battery, motor/ESC, and wiring access remain clear.
- Integrate fuselage spine + spar sockets, battery rail + cable guide, payload nose service labels, and wing root alignment keys when the integration removes setup steps without hiding service access.
- Do not integrate tilting nacelle cores, servo/linkage cartridges, external landing gear, V-tail hinge/control surfaces, or motor/ESC service pods into the main fuselage.
- Preserve tilt-axis datum faces, wing-root alignment, battery CG slide path, cable inspection windows, and nacelle replacement order.
- Treat over-integration, lost tilt-axis datum, blocked motor/ESC access, and blocked battery CG adjustment as design failures.

## V1 Design Package Contents

The package must include:

- existing BOM
- redesigned BOM
- explicit integration decisions
- assembly step reduction
- retained service access points
- print orientation and support strategy
- assembly sequence
- risk register
- `schema_v6`-compatible output for the redesigned structural mockup

## Expansion Role

Tiltrotor V1 is the first drone-family design-thinking seed after CubeSat V1. It should prove that the rule+data approach can handle moving interfaces and service modules, not only static box structures.

