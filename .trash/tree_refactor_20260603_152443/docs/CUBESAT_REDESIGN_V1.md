# CubeSat Redesign V1

This document defines the first Blueprint NPU design-thinking sample.

## Purpose

The goal is not to generate a decorative 3D model. The goal is to read an existing product-like structure, reason about its engineering tradeoffs, and produce a better 3D-printable assembly package.

V1 uses a 3U CubeSat-style educational mockup because it has clear modules, panels, rails, board mounts, and service access. It is not a flight-certified spacecraft design.

## Target Object

```text
Object: 3U CubeSat educational / exhibition mockup
Envelope: 100 x 100 x 340.5 mm class
Manufacturing: FDM 3D printing
Primary material: PETG
Primary metric: assembly / serviceability efficiency
Success output: design package before STL generation
```

## Engineering Rule Set

- Reducing part count is only a success when service access remains clear.
- Integrate panel + standoff, rail + frame, and board dummy mount + cable guide when the integration removes fasteners without hiding service access.
- Do not integrate removable covers, replaceable board carriers, hinge/antenna mockups, or fragile exposed parts into the main frame.
- Preserve datum surfaces, rail straightness, board replacement paths, and visible assembly order.
- Treat over-integration, blocked board access, and lost print datums as design failures.

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
- `schema_v6`-compatible output for the redesigned structural core

## Baseline Expansion Path

After CubeSat V1 proves the pipeline, apply the same structure to:

1. drone frame
2. robot arm link / joint housing
3. rocket display motor / launch vehicle mockup
4. fighter educational cutaway mockup

