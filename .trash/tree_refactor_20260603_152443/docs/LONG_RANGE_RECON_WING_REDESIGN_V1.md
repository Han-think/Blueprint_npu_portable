# Long-Range Recon Wing Redesign V1

This document defines the fifth Blueprint NPU design-thinking sample.

## Purpose

The goal is not to create a real military aircraft, weapon system, stealth aircraft, or high-speed certified airframe. The goal is to read an existing long-range surveillance wing structure, reason about center-spine, spar, sensor, mission payload, battery/CG, elevon, propulsion-display, and landing-service tradeoffs, and produce a better 3D-printable educational mockup package.

V1 uses the `wing_long_range` asset because it already contains the right teaching structure: center body pod, long spar, wing ribs, elevon pockets, pusher mount, GPS/pitot boom, camera bay, battery/CG slide, and long-range electronics placeholders.

The visual language may reference SR-71-like long fuselage, chine-like wing-body blending, and reconnaissance mission layout, but the design remains an original educational serviceability mockup.

## Target Object

```text
Object: long-range recon / mission-payload wing educational mockup
Envelope: desktop long-span aircraft reference, scaled for printable mockup
Manufacturing: FDM 3D printing
Primary material: PETG structural parts + clear PETG sensor windows + TPU skid pads
Primary metric: assembly / serviceability efficiency + long-range mission structure readability
Success output: design package before STL generation
```

## Engineering Rule Set

- Reducing part count is only a success when sensor bay, mission payload bay, battery CG rail, spar datum, elevon hinge, propulsion-display module, and landing skid service remain clear.
- Integrate center spine + spar socket, wing root + alignment key, battery rail + cable guide, and service labels when the integration removes small parts without hiding access.
- Do not integrate the sensor nose module, mission payload insert, battery dummy, elevon hinge module, propulsion-display module, or replaceable skid pads into a fixed closed body.
- Preserve long-range layout readability: sensor nose, mission bay, battery/CG rail, wing spar, elevons, and rear propulsion-display relationship must be visible.
- Treat over-integration, closed payload bay, lost CG rail, hidden spar datum, blocked elevon hinge, and military/weaponized drift as design failures.

## V1 Design Package Contents

The package must include:

- existing BOM
- redesigned BOM
- explicit integration decisions
- assembly step reduction
- retained service access and mission-structure readability points
- print orientation and support strategy
- assembly sequence
- risk register
- `schema_v6`-compatible output for the redesigned educational mockup

## Safety Boundary

This seed is limited to a non-functional educational mockup. It must not include weapons, release mechanisms, stealth performance claims, operational mission planning, military tactics, high-speed thermal design, or flight-ready aircraft manufacturing guidance.

## Expansion Role

Long-Range Recon Wing V1 extends the design-thinking seed set into high-aspect mission-aircraft layout reasoning. It adds mission-structure readability to the established serviceability metric while keeping the same rule+data package format used by CubeSat, Tiltrotor, Robot Arm, and Small Launch Vehicle V1.
