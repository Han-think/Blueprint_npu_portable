# Aerospace Superquality Blueprint Spec - 2026-05-13

This document is the design source before generating or hand-authoring higher quality Aerospace assembly and part schematic images.

The goal is not to copy real aircraft drawings. The goal is to use representative aircraft families as structural references, then redraw original blueprint assets that match the project's current part tree and learning-data needs.

## Production Rule

Every Aerospace image must be created from this written brief first.

Required sequence:

1. Confirm representative aircraft family.
2. Define the three drawing axes.
3. Map every `p1...pN` part to visible aircraft structure.
4. Define part-level drawing cues.
5. Generate or hand-author SVG.
6. Validate XML, viewBox, server response, and generator overwrite protection.
7. Record completion in the production snapshot.

## Category Drawing Language

Aerospace images must read as aircraft engineering drawings, not generic vehicle icons.

Require:

- planform or side-view silhouette that reveals the aircraft class
- aerodynamic surfaces with clear spar, hinge, control-surface, or station cues
- inlet, nacelle, rotor, wing box, or landing gear detail where applicable
- datum lines for fuselage centerline, wing station, tail station, rotor mast, or engine axis
- part zones placed on real component footprints
- small callouts for structural function, not decorative labels

Avoid:

- plain fuselage rectangles
- generic wings without leading/trailing edge structure
- engine circles without nacelle, pylon, inlet, gearbox, or exhaust logic
- landing gear drawn as isolated sticks without trunnion/oleo/wheel relation
- control surfaces that do not follow actual aircraft geometry

## Three Drawing Axes

Each Aerospace assembly needs three related drawings:

- Exterior axis: aircraft recognition. It must show the class-defining silhouette, control surfaces, engines, gear, rotors, or inlets.
- Internal axis: functional structure. It must show load paths, wing box, spar/rib system, pressure shell, fuel tanks, gearbox, cabin decks, inlet duct, engine bay, or actuator systems.
- Part-zone axis: app-facing `p1...pN` overlay map. It must align part data with visible aircraft geometry.

Current file convention:

```text
vendor/img/<vehicle_id>_exterior.svg
vendor/img/<vehicle_id>_internal.svg
vendor/img/<vehicle_id>_top.svg
```

## Aerospace Assembly Order

Recommended Aerospace master sequence:

1. `fighter_f_class`
2. `supersonic_sst`
3. `civil_airliner`
4. `turboprop_transport`
5. `heavy_helicopter`

Rationale:

- F-15-class fighter and SST expose silhouette quality problems immediately.
- Civil airliner establishes clean transport-aircraft surface language.
- Turboprop adds prop/nacelle/high-wing cargo logic.
- Heavy helicopter adds rotor transmission and ramp/cabin structure.

## Assembly Specs

### fighter_f_class

Representative basis:

- F-15 Eagle / F-15EX family for twin-engine air-superiority fighter structure.
- NASA F-15 research aircraft as a clean official basis for twin-engine layout, twin tails, two F100-class engines, high-speed research use, and three-view discipline.
- The output should be an original F-15-class homage rather than a direct aircraft copy.

Three axes:

- Exterior: sharp nose, tandem/canopy cockpit cue if Strike Eagle-inspired, broad center fuselage, shoulder/trapezoidal wing, twin vertical tails, all-moving stabilators, twin side/shoulder inlets, twin exhaust nozzles, main/nose landing gear.
- Internal: radar/avionics bay, cockpit/ejection-seat rail, center fuel/wing carry-through, twin inlet ducts, twin engine bays, accessory gearbox areas, gear bays, speedbrake/arrestor hook cues, control actuator paths.
- Part-zone: exact `p1...p10` overlay on forward/center/aft fuselage, wings, twin tails, stabilators, twin inlets, twin nozzles, and landing gear.

Part image direction:

- `p1` forward fuselage: radome, avionics bay, canopy frame, cockpit tub, ejection seat rails.
- `p2` center fuselage: wing carry-through, fuel cavities, gear bay openings, load frames.
- `p3` aft fuselage: twin engine bays, dual tailpipe access, accessory gearbox mounts, dorsal speedbrake and arrestor-hook bay cues.
- `p4` main wing: spar, ribs, hardpoints, leading-edge slat track, flap/aileron hinge.
- `p5` vertical stabilizer: twin vertical-tail logic, rudder hinge, RWR tip fairing, formation light strips.
- `p6` stabilator: all-moving pivot shaft, actuator yoke, anti-flutter mass balance.
- `p7` engine inlet duct: twin side/shoulder inlets, ramp/lip geometry, boundary-layer bleed, FOD screen mount, duct centerlines.
- `p8` TVC exhaust nozzle: twin afterburning nozzles, convergent-divergent petals, actuator rings, optional axisymmetric TVC cue.
- `p9` main landing gear: oleo strut, trunnion, wheel/brake, retract link.
- `p10` nose landing gear: steerable fork, shimmy damper, tow fitting, forward retract path.

### turboprop_transport

Representative basis:

- ATR 72 high-wing regional turboprop.
- Regional cargo/passenger aircraft logic: high wing, twin nacelles, large propellers, T-tail, cabin barrel, cargo/ramp variants.

Three axes:

- Exterior: high-mounted straight wing, twin nacelles, large prop disks, fuselage cabin, nose cockpit, aft ramp/tail cone, T-tail, main gear sponsons.
- Internal: pressurized cabin frames, cargo floor, wing box/fuel tank, nacelle gearbox, prop shaft, landing gear sponson, aft ramp hinge/actuator.
- Part-zone: map fuselage sections, wing, nacelles, props, empennage, and gear.

Part image direction:

- `p1` forward fuselage: cockpit windows, radome, crew door frame, avionics bay.
- `p2` main cabin: pressure frames, window belt, passenger/cargo door, cargo floor beams.
- `p3` tail cone/ramp: rear ramp hinge, actuator, tail bumper, APU bay cue.
- `p4` high wing: spars, ribs, integral fuel, nacelle attach frames, flap tracks.
- `p5` engine nacelle: reduction gearbox, oil cooler inlet, exhaust stack, anti-icing duct.
- `p6` propeller: constant-speed hub, blade roots, pitch-change mechanism, spinner.
- `p7` T-tail: vertical fin, horizontal stabilizer, elevator/rudder hinges, trim tab links.
- `p8` main gear: fuselage sponson, twin wheel, oleo strut, retract link.

### civil_airliner

Representative basis:

- Airbus A320 family for single-aisle civil transport structure.
- Use A320neo-family cues: wingtip devices, modern nacelles, fly-by-wire cockpit, high-lift surfaces.
- The current label says twin-aisle, but the representative basis in code is A320 family. Keep the drawing language single-aisle until the template text is changed.

Three axes:

- Exterior: nose/radome, cockpit, fuselage barrel/window belt, wing box, leading/trailing-edge devices, twin underwing engines, pylons, empennage, landing gear.
- Internal: frames/stringers, cargo floor, wing box/wet tank, slat/flap mechanisms, pylon load path, nacelle systems, gear bay.
- Part-zone: map nose, barrel, wing box, slats, flaps, pylons, nacelles, empennage, landing gear.

Part image direction:

- `p1` nose/radome: weather radar, cockpit windscreen, avionics bay, crew rest cue if retained.
- `p2` fuselage barrel: circumferential frames, longitudinal stringers, windows, doors, cargo door.
- `p3` wing box: front/rear spars, ribs, upper/lower skin panels, fuel tank sealant grooves.
- `p4` leading edge/slats: slat tracks, anti-icing manifold, Krueger/slat segmentation.
- `p5` trailing edge/flaps: flap track fairings, spoilers, aileron, double-slotted flap cue.
- `p6` engine pylon: fail-safe load path, firewall, fluid/electrical disconnects.
- `p7` turbofan nacelle: fan cowl, thrust reverser cascade, acoustic liner, exhaust nozzle.
- `p8` empennage: vertical/horizontal tail, rudder/elevator, trimmable horizontal stabilizer.
- `p9` main gear: four-wheel bogie, oleo strut, brake/anti-skid, retraction link.

### heavy_helicopter

Representative basis:

- Boeing CH-47 Chinook for tandem heavy-lift mission logic.
- The code label says coaxial, but `wikiTitle` and representative intent point to Chinook. Use tandem-rotor heavy-lift visual language unless the template is later renamed.

Three axes:

- Exterior: tandem rotor disks, long fuselage, forward/aft pylons, rear ramp, side sponsons, landing gear, twin engine pods.
- Internal: rotor mast/gearbox structure, driveshaft path, cargo floor, ramp hinge, fuel tanks, engine bay, avionics/cockpit.
- Part-zone: map upper/lower or forward/aft rotor hubs according to current part labels, gearbox, blades, cabin, tail boom/ramp, engine bays, gear.

Part image direction:

- `p1` rotor hub upper/forward: rotor head, blade grip, pitch links, swashplate.
- `p2` rotor hub lower/aft: counter/tandem rotor hub, blade grip, gearbox interface.
- `p3` gearbox housing: reduction gears, mast bearing, oil manifolds, accessory pads.
- `p4` rotor blade: composite spar, honeycomb core, erosion strip, tip cap.
- `p5` fuselage cabin: cargo floor, side door, troop seats, cargo hook attach.
- `p6` twin tail boom/ramp: rear ramp, aft pylon, stabilizers, anti-collision lights.
- `p7` engine bay: turboshaft pod, intake particle separator, exhaust IR suppressor, fire loop.
- `p8` landing gear: quadricycle strut, oleo, wheel, sponson mount.

### supersonic_sst

Representative basis:

- Concorde for ogival/double-delta wing, droop nose/visor, four paired engine nacelles, variable intake ramps, tall landing gear, high-Mach thermal structure.

Three axes:

- Exterior: needle nose with droop/visor cue, long slender fuselage, ogival delta wing, paired engine nacelles, vertical fin, tall landing gear.
- Internal: pressure shell, CG trim/fuel tanks, intake ramp/shock system, reheat bay, elevon actuators, droop nose jack/visor rails.
- Part-zone: map delta wing, nose/visor, center tanks, aft/reheat bay, elevons, nacelles, intakes, fin/rudder, gear, droop mechanism.

Part image direction:

- `p1` ogive-delta wing: conical camber, fuel tank cells, leading edge, elevon hinge line.
- `p2` forward fuselage/visor: pressure bulkhead, visor track, cockpit windows, needle nose.
- `p3` center fuselage/tanks: CG trim tanks, frames, fuel-transfer plumbing.
- `p4` aft fuselage/reheat bay: heat shield, engine cluster support, tailcone fairing.
- `p5` elevon: six-section hinge, hydraulic actuator, flutter mass/edge detail.
- `p6` engine nacelle: paired nacelle, nozzle bucket/reverser, reheat liner, firewall.
- `p7` variable intake: primary/secondary ramps, spill door, bleed slots, shock-control cue.
- `p8` fin/rudder: fin spar, rudder hinge, RWR blister, anti-icing leading edge.
- `p9` landing gear: tall bogie, kneeling/retract geometry, spray deflector.
- `p10` droop nose mechanism: screw/hydraulic jacks, hinge, visor carriage, locks.

## Reference Sources

- NASA F-15 Flight Research Facility: https://www.nasa.gov/reference/f-15-flight-research-facility/
- NASA F-15B Aeronautical Research Aircraft: https://www.nasa.gov/image-article/f-15b-aeronautical-research-aircraft/
- U.S. Air Force F-15 Eagle fact sheet: https://www.af.mil/About-Us/Fact-Sheets/Display/Article/104501/f-15-eagle/level/f-15-eagle/
- Airbus A320 Family official page: https://www.airbus.com/en/products-services/commercial-aircraft/passenger-aircraft/a320-family
- ATR turboprop overview: https://www.atr-aircraft.com/turboprop/
- ATR 72-600F official page: https://www.atr-aircraft.com/aircraft-services/aircraft-family/atr-72-600f-freighter/
- Boeing H-47 Chinook official page: https://www.boeing.com/defense/ch-47-chinook
- Heritage Concorde nose/visor design: https://www.heritageconcorde.com/nose-and-visor-design-and-manufacture
- Heritage Concorde air intake system: https://www.heritageconcorde.com/air-in-take-system

## Next Step

Use this document as the prompt/spec source before upgrading Aerospace assembly images or Aerospace single-part preset images.

Recommended immediate implementation:

1. Upgrade `fighter_f_class` exterior/internal/top images as the Aerospace master using F-15 twin-engine layout.
2. Upgrade the fighter's referenced single-part images.
3. Protect hand-authored Aerospace master files from generator overwrite.
4. Continue with `supersonic_sst`, then `civil_airliner`.
