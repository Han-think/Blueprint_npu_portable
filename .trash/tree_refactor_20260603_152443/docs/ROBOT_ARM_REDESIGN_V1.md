# 6-DOF Robot Arm Redesign V1

This document defines the third Blueprint NPU design-thinking sample.

## Purpose

The goal is not to create a certified industrial robot. The goal is to read an existing 6-axis robot arm structure, reason about joint/link/service tradeoffs, and produce a better 3D-printable educational mockup package.

V1 uses the `arm_6dof` asset because it has a clear kinematic chain: J1-J6 axes, joint housings, hollow links, wrist stack, tool flange, and cable spine. It is ideal for teaching the boundary between printable integration and serviceable mechanism modules.

## Target Object

```text
Object: 6-DOF industrial robot arm educational / exhibition mockup
Envelope: desktop 600 mm reach class reference, scaled for printable mockup
Manufacturing: FDM 3D printing
Primary material: PETG structural parts + TPU cable pads / bumpers
Primary metric: assembly / serviceability efficiency
Success output: design package before STL generation
```

## Engineering Rule Set

- Reducing part count is only a success when J1-J6 axes, reducer/bearing dummies, encoder covers, cable path, and tool flange access remain clear.
- Integrate hollow link + cable channel, link cover + datum label, base shell + mounting datum, and tool label + utility guide when the integration removes small parts without hiding service access.
- Do not integrate joint cartridges, reducer/bearing dummies, encoder access covers, cable spine, tool changer latch, or wrist service module into fixed printed links.
- Preserve axis datum faces, cable replacement path, wrist stack access, tool flange visibility, and visible assembly order.
- Treat over-integration, lost axis datum, blocked reducer/encoder access, and hidden cable replacement path as design failures.

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
- `schema_v6`-compatible output for the redesigned educational mockup

## Expansion Role

Robot Arm V1 extends the design-thinking seed set beyond static structures and drone moving interfaces into kinematic-chain reasoning: axes, torque paths, joint cartridges, cable routing, and tool service boundaries.

