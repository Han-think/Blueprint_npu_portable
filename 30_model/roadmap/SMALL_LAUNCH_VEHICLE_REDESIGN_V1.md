# Small Launch Vehicle Redesign V1

This document defines the fourth Blueprint NPU design-thinking sample.

## Purpose

The goal is not to create a flight vehicle, propulsion system, or launch-ready engine. The goal is to read an existing small launch vehicle structure, reason about stage, tank, engine-display, service-bay, fairing, and flow-path tradeoffs, and produce a better 3D-printable educational cutaway mockup package.

V1 uses the `small_launch_vehicle` asset because it has a clear teaching structure: first-stage body, tank shells, engine display area, interstage, upper-stage dummy, payload fairing, fins, and avionics/service bay. It is ideal for teaching the boundary between printable integration and serviceable, readable modules.

## Target Object

```text
Object: small launch vehicle educational / exhibition cutaway mockup
Envelope: desktop vertical display reference, scaled for printable mockup
Manufacturing: FDM 3D printing
Primary material: PETG structural parts + clear PETG windows + TPU feet / pads
Primary metric: assembly / serviceability efficiency + flow-path readability
Success output: design package before STL generation
```

## Engineering Rule Set

- Reducing part count is only a success when engine dummy, tank modules, interstage alignment, fairing split, avionics/service bay, and visible flow path remain clear.
- Integrate outer shell halves + alignment keys, tank dummy + flow labels, interstage ring + datum faces, and service bay label + cable guide when the integration removes small parts without hiding inspection access.
- Do not integrate the engine display cartridge, slide-in tank modules, fairing separation, fin replacement mounts, or service bay cover into a fixed closed body.
- Preserve cutaway visibility from tank modules to engine display cartridge, stage separation datum, fairing access, and visible assembly order.
- Treat over-integration, hidden flow path, blocked engine/tank service, lost interstage datum, and unsafe functional-propulsion drift as design failures.

## V1 Design Package Contents

The package must include:

- existing BOM
- redesigned BOM
- explicit integration decisions
- assembly step reduction
- retained service access and flow-readability points
- print orientation and support strategy
- assembly sequence
- risk register
- `schema_v6`-compatible output for the redesigned educational cutaway mockup

## Safety Boundary

This seed is limited to a non-functional educational mockup. It must not include propellant formulas, ignition instructions, pressure-vessel design, flight performance calculations, launch hardware, or dimensions intended for a working propulsion system.

## Expansion Role

Small Launch Vehicle V1 extends the design-thinking seed set into staged aerospace assemblies. It adds flow-path readability to the established serviceability metric while keeping the output in the same rule+data package format used by CubeSat, Tiltrotor, and Robot Arm V1.
