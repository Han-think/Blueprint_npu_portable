# Blueprint Generation Context Packs - 2026-05-15

The generator should not rely on vague creativity. Every single part and assembly needs a compact design context pack before generation.

The goal is not to reproduce real engineering drawings. The goal is to constrain the model so it produces useful, inspectable, assembly-aware blueprint outputs.

## Current UI Integration

Implemented in `Minimal.html`:

- explicit `2D View` buttons
- 2D reference SVG shown before generated JSON preview
- 3D View remains available as a secondary check
- category design context is injected into assembly part generation prompts
- design reference packs are injected into assembly part prompts
- learning/curation policy is intentionally not injected into design generation prompts

Layer boundary:

```text
docs/BLUEPRINT_LAYER_BOUNDARY_2026-05-15.md
```

## Reference Depth

Rocket and aircraft can benefit from book-level references because public engineering literature is rich.

Other domains also need references, but not always full textbooks. For this project, the minimum useful pack is:

1. Representative product family
2. Typical part breakdown
3. Functional interfaces
4. Manufacturing/process constraints
5. Visual review cues
6. Failure/risk cues

## Category Context Requirements

| Category | Reference Need | Minimum Context |
|---|---|---|
| Space | High | load paths, pressure vessels, thermal protection, separation rings, avionics, harnessing |
| Aerospace | High | aerodynamic surfaces, spars/ribs/frames, ducts, gear, access panels, control hinges |
| Propulsion | High | flow path, rotating/stationary boundaries, seals, bearings, cooling, manifolds, nozzles |
| Drone | Medium | stiffness, mass, electronics routing, vibration isolation, battery retention, airflow clearance |
| Robotics | Medium | joint axes, bearings, encoders, torque paths, cable routes, end stops, actuator interfaces |
| Mechanical | Medium | bearing seats, shafts, fits, pins, fasteners, seals, lubrication, datum surfaces |
| Marine | Medium | watertight boundaries, pressure compensation, cable glands, corrosion, fairings, buoyancy |
| Medical | Medium-High | human interface surfaces, safety stops, cleaning access, soft contact, adjustability |

## Generation Rule

For every generated part:

- use the assembly-specific SVG as visual reference when available
- include the category context in the prompt
- require `8-16` geometry operations for assembly parts
- require at least one body feature, interface feature, subtractive feature, finishing feature, and label/datum feature
- show 2D reference first in the UI
- use 3D only as a structural sanity check unless geometry operations are rich enough

## Next Context Work

The non-Space/Aerospace context specs are now created:

```text
docs/PROPULSION_SUPERQUALITY_BLUEPRINT_SPEC_2026-05-15.md
docs/DRONE_SUPERQUALITY_BLUEPRINT_SPEC_2026-05-15.md
docs/ROBOTICS_SUPERQUALITY_BLUEPRINT_SPEC_2026-05-15.md
docs/MECHANICAL_SUPERQUALITY_BLUEPRINT_SPEC_2026-05-15.md
docs/MARINE_SUPERQUALITY_BLUEPRINT_SPEC_2026-05-15.md
docs/MEDICAL_SUPERQUALITY_BLUEPRINT_SPEC_2026-05-15.md
```

Each spec locks:

- representative basis per assembly
- must-show features
- forbidden generic output
- expected 2D/3D review cues
- promotion criteria from `train_aug_ready` to `train_base_ready`

## Next Step

Promote the remaining categories one vehicle at a time:

1. Propulsion non-turbofan 3-axis upgrades
2. Drone master pass
3. Robotics master pass
4. Mechanical master pass
5. Marine master pass
6. Medical master pass

Do not bulk-promote all coverage assets to `train_base_ready` until each category's 3-axis and generated outputs pass visual review.
