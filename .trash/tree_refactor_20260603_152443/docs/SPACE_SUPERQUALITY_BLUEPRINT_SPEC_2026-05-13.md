# Space Superquality Blueprint Spec - 2026-05-13

This document is the design source before generating or hand-authoring higher quality Space assembly and part schematic images.

The goal is not to copy a real vehicle drawing. The goal is to use representative aerospace products as structural references, then redraw original blueprint assets that match the project's current part tree and learning-data needs.

## Production Rule

Every assembly and part image should be generated from a written design brief first.

Required sequence:

1. Define the representative product family.
2. Define the three drawing axes.
3. Map each `p1...pN` part to visible physical structure.
4. Define visual detail requirements.
5. Generate or hand-author SVG.
6. Validate XML, viewBox, server response, and generator overwrite protection.
7. Record the result in the production snapshot.

## Three Drawing Axes

Each assembly needs three related drawings:

- Exterior axis: recognition drawing. It must show the product's silhouette and characteristic external hardware.
- Internal axis: functional structure drawing. It must show tanks, decks, optical paths, pressure shells, electronics, actuators, plumbing, load paths, or mechanisms.
- Part-zone axis: data mapping drawing. It must align app `p1...pN` zones with visible component footprints.

Current file convention:

```text
vendor/img/<vehicle_id>_exterior.svg
vendor/img/<vehicle_id>_internal.svg
vendor/img/<vehicle_id>_top.svg
```

`*_top.svg` is currently the part-zone map used by the overlay system.

## Quality Bar

Avoid:

- plain boxes unless the real component is a rack, deck, panel, or pressure module
- generic circular icons without surrounding structure
- unlabeled decorative lines
- zones floating away from real visible geometry
- one drawing trying to explain exterior, internals, and part data at the same time

Require:

- recognizable representative-product silhouette
- visible structural hierarchy
- datum/station lines where relevant
- subsystem labels that explain design function
- part zones drawn over real component locations
- one or more detail cues per major part: bolts, rails, hinges, truss members, baffles, optical path, docking ring, radiator cells, plumbing, or wire harness paths

## Space Assembly Order

Recommended Space master sequence:

1. `small_launch_vehicle`
2. `cubesat_3u`
3. `lunar_lander`
4. `space_telescope`
5. `orbital_module`

Rationale:

- The rocket is already the first three-axis reference.
- CubeSat has clean modular structure and is ideal for proving assembly-to-part image consistency.
- Lunar lander adds legs, RCS, tank, deck, and engine geometry.
- Space telescope adds optical path and service-bay logic.
- Orbital module adds pressure-shell, docking, truss, rack, radiator, and solar array logic.

## Assembly Specs

### small_launch_vehicle

Representative basis:

- Saturn V structural logic for stage hierarchy, tanks, interstage, IU, and clustered engines.
- Modern small-launcher proportions for compact payload/fairing treatment.

Three axes:

- Exterior: fairing, avionics/IU band, interstage, booster barrel, fin can, engine cluster.
- Internal: avionics ring, upper-stage engine, interstage truss, LOX tank, fuel tank, turbopump/plumbing, thrust frame, engine cluster.
- Part-zone: exact `p1...p10` overlay mapping.

Part image direction:

- `p1` combustion chamber: injector face, chamber barrel, regen channel bands, thrust-frame attach lugs.
- `p2` bell nozzle: expansion bell, throat ring, cooling jacket, gimbal flange.
- `p3` turbopump: turbine housing, LOX/fuel impeller volutes, gearbox, pipe ports.
- `p4` LOX tank: ellipsoidal dome, barrel section, slosh baffles, vent/relief port.
- `p5` fuel tank: dome, barrel, fill/drain ports, sensor boss, anti-slosh detail.
- `p6` interstage: ring frames, diagonal truss, separation bolts, vent cutouts.
- `p7` stage 2 engine: vacuum nozzle, restart plumbing, compact thrust frame.
- `p8` payload fairing: bisector seam, separation rail, acoustic blanket, payload adapter.
- `p9` fin set: root fitting, trapezoid fin, leading edge, skin fasteners.
- `p10` avionics bay: flight computer boxes, IMU block, harness tray, EMI shielding.

### cubesat_3u

Representative basis:

- CubeSat Design Specification style 3U bus.
- P-POD / deployer rail logic.
- PC/104 electronics stack and deployable appendages.

Three axes:

- Exterior: 3U rectangular bus, four long rails, deployable solar panels, antenna deployers, separation plate.
- Internal: stacked avionics boards, ADCS/reaction wheel bay, battery/payload section, harness path, thruster manifold if present.
- Part-zone: map each deployable panel, bus frame, antenna, wheel, star tracker, payload, thruster, and separation spring.

Part image direction:

- `p1` frame: four rails, end plates, PC/104 standoffs, deployer contact surfaces.
- `p2` solar panel: hinge, cells, latch, burn-wire release.
- `p3` antenna deployer: tape spring, stowage slot, release pin.
- `p4` reaction wheel: rotor, stator, isolation mount.
- `p5` star tracker mount: optical baffle, mounting boss, line-of-sight bracket.
- `p6` payload optics bench: lens tube, focal-plane block, thermal strap.
- `p7` cold gas thruster: bracket, nozzle, manifold, pipe feed.
- `p8` separation spring plate: pusher springs, kill switch arm, contact plate.

### lunar_lander

Representative basis:

- Apollo Lunar Module landing configuration for four-leg landing gear, descent stage, and ascent/deck separation logic.
- Surveyor-style compact lander cues for demonstrator scale.

Three axes:

- Exterior: central body, high-gain dish, solar wings, RCS pods, descent engine, four legs, footpads.
- Internal: central tank, avionics deck, payload deck, RCS feed layout, descent engine thrust path, leg load paths.
- Part-zone: map tank, engine, RCS, legs, avionics, solar wings, dish, payload deck.

Part image direction:

- `p1` tank: spherical/cylindrical tank, dome, bulkhead, retention straps.
- `p2` main engine: throttleable bell, gimbal, heat shield, feed valves.
- `p3` RCS cluster: four-nozzle pod, manifold, mounting bracket.
- `p4` landing leg: crush core, struts, hinge, footpad, contact sensor.
- `p5` avionics deck: computer boxes, IMU, lidar/camera bracket, comm box.
- `p6` solar wing: panel cells, hinge, deployment stop.
- `p7` high-gain dish: parabolic mesh/dish, two-axis gimbal.
- `p8` payload deck: grid plate, thermal isolation, instrument hardpoints.

### space_telescope

Representative basis:

- Hubble Space Telescope optical tube and service module.
- Cassegrain/Ritchey-Chretien light path: primary mirror to secondary mirror and back through the primary to instruments.

Three axes:

- Exterior: aperture door, cylindrical optical tube, solar arrays, equipment section, axial bay.
- Internal: optical path, primary mirror, secondary mirror, metering truss, instrument bay, pointing control hardware.
- Part-zone: map mirror cell, secondary, optical bench, equipment bay, arrays, aperture door, pointing control, axial instruments.

Part image direction:

- `p1` primary mirror cell: circular mirror, honeycomb/backing hint, support points.
- `p2` secondary mirror: small mirror, spider/strut mount, tip-tilt mechanism.
- `p3` optical bench: metering truss, optical axis, baffles.
- `p4` equipment bay: modular instrument slots, harness trays, thermal panels.
- `p5` solar array: deployable wing, cell grid, drive hinge.
- `p6` aperture door: hinge, actuator, sun-exclusion baffle.
- `p7` pointing control: reaction wheels, gyros, fine guidance sensor blocks.
- `p8` axial bay: instrument modules, focal plane interface, cooling straps.

### orbital_module

Representative basis:

- ISS pressurized modules and integrated truss logic.
- CBM/docking ring, rack-based interior, external payload/radiator/solar structures.

Three axes:

- Exterior: cylindrical pressure shell, two docking ports, solar/radiator/truss equipment, external payload platform.
- Internal: pressure shell frames, rack decks, ECLSS racks, hatch/port tunnels, wire/fluid routing.
- Part-zone: map shell, ports, truss attach, radiator, solar tower, interior deck, payload platform, ECLSS racks.

Part image direction:

- `p1` pressure shell: cylindrical barrel, ring frames, MMOD shield layers.
- `p2` docking port: CBM/APAS-like ring, bolt circle, hatch, seal.
- `p3` truss attach: bracket nodes, umbilicals, EVA handrails.
- `p4` radiator: panel cells, hinge/deploy bracket, fluid manifold.
- `p5` solar tower: long array mast, panel blanket cells, rotary joint.
- `p6` interior deck: rack grid, crew passage, floor/ceiling rails.
- `p7` external payload platform: hardpoints, robotic grapple/attach point.
- `p8` ECLSS racks: O2/CO2/water recovery boxes, ducting, service panels.

## Reference Sources

- NASA Saturn V Flight Manual SA-507: https://www.nasa.gov/wp-content/uploads/static/history/afj/ap12fj/pdf/a12_sa507-flightmanual.pdf
- NASA Saturn V Instrument Unit article: https://www.nasa.gov/image-article/manufacturing-saturn-v-instrument-unit/
- NASA Hubble optics/design: https://science.nasa.gov/mission/hubble/observatory/design/optics
- NASA Hubble overview/about: https://science.nasa.gov/mission/hubble/overview/about-hubble
- NASA ISS assembly elements: https://www.nasa.gov/international-space-station/international-space-station-assembly-elements/
- NASA ISS reference/facts: https://www.nasa.gov/reference/international-space-station/
- NASA Apollo 9 Lunar Module landing configuration: https://science.nasa.gov/resource/apollo-9-lunar-module-in-lunar-landing-configuration/

## Next Step

Use this document as the prompt/spec source for the Space part-image pass.

Recommended immediate implementation:

1. Upgrade `small_launch_vehicle` single-part preset images first.
2. Add generated files under the existing preset path convention:
   `vendor/img/presets/space/<type>/<config>.svg`
3. Protect any hand-authored master part images from generator overwrite.
4. Continue with `cubesat_3u` part images after the rocket part set proves the workflow.
