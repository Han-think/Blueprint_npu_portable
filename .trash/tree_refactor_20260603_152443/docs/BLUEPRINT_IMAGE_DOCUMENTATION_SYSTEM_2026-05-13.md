# Blueprint Image Documentation System - 2026-05-13

This document defines the documentation-first workflow for every blueprint image in the project.

The project should not generate more high-quality images directly from vague prompts. Every image should be produced from a documented design specification first.

## Scope

The image system currently covers:

- 40 assembly templates
- 3 assembly axes per template
  - exterior
  - internal
  - top / part-zone
- 359 assembly part mappings
- 200 single-part preset configurations

The generated inventory lives here:

```text
docs/BLUEPRINT_IMAGE_ASSET_INVENTORY_2026-05-13.md
```

The locked representative bases live here:

```text
docs/BLUEPRINT_REPRESENTATIVE_BASE_LOCKS_2026-05-13.md
```

## Documentation Layers

Use four layers of documentation before making final images.

### 1. Global Image Rules

Applies to all categories.

Each image must answer one clear question:

- Exterior: what does this object look like?
- Internal: how does this object work?
- Part-zone: which visible structure maps to which generated part?
- Single-part: what is the manufacturing-relevant geometry of this part?

Avoid mixing all questions into one image.

### 2. Category Specification

Each category needs its own image spec before superquality work begins:

- `drone`
- `aerospace`
- `space`
- `marine`
- `robotics`
- `medical`
- `propulsion`
- `mechanical`

The Space category has started here:

```text
docs/SPACE_SUPERQUALITY_BLUEPRINT_SPEC_2026-05-13.md
```

The Aerospace category has started here:

```text
docs/AEROSPACE_SUPERQUALITY_BLUEPRINT_SPEC_2026-05-13.md
```

Every other category should get the same kind of spec before hand-authoring master images.

Before writing a category specification, check the representative base lock document. Category specs should refine locked bases, not silently replace them.

### 3. Assembly Specification

Each of the 40 assemblies needs:

- representative product family
- exterior-axis intent
- internal-axis intent
- part-zone intent
- part list and mapping behavior
- required visual details
- forbidden simplifications
- reference links or local notes
- master/protected asset status

### 4. Single-Part Specification

Each single-part preset image needs:

- part function
- representative hardware basis
- required geometry
- required manufacturing cues
- required labels
- avoid-list
- SVG path
- protection status if hand-authored

## Image Production Pipeline

Use this sequence for every category:

1. Generate or update the category documentation.
2. Confirm representative product bases.
3. Generate an asset inventory from code.
4. Pick one assembly as the category master.
5. Create exterior/internal/top images for that assembly.
6. Create single-part images for that assembly's referenced presets.
7. Protect hand-authored images from generator overwrite.
8. Validate all SVGs as XML.
9. Validate a server sample.
10. Record completion in the production snapshot.

## File Conventions

Assembly images:

```text
vendor/img/<vehicle_id>_exterior.svg
vendor/img/<vehicle_id>_internal.svg
vendor/img/<vehicle_id>_top.svg
```

Single-part preset images:

```text
vendor/img/presets/<category>/<type>/<config>.svg
```

Documentation:

```text
docs/<CATEGORY>_SUPERQUALITY_BLUEPRINT_SPEC_YYYY-MM-DD.md
docs/BLUEPRINT_IMAGE_ASSET_INVENTORY_YYYY-MM-DD.md
docs/BLUEPRINT_IMAGE_DOCUMENTATION_SYSTEM_YYYY-MM-DD.md
```

Generator / protection:

```text
scripts/generate_blueprint_assets.js
scripts/generate_blueprint_image_docs.js
```

## Quality Levels

Use explicit quality states so the project does not confuse coverage with final quality.

- `coverage`: file exists and aligns with the UI.
- `structured`: image reflects the correct assembly or part logic.
- `master`: hand-authored or carefully refined to representative-product quality.
- `superquality`: master image plus part-level manufacturing detail and category-consistent drawing language.

Current state:

- All 40 assemblies have three-axis coverage.
- `small_launch_vehicle` is the first hand-authored three-axis reference.
- Space has the first category superquality specification.
- Aerospace has a category superquality specification.
- Remaining categories need documentation before image upgrades.

## Category Documentation Order

Recommended order:

1. Space
2. Aerospace
3. Propulsion
4. Drone
5. Robotics
6. Mechanical
7. Marine
8. Medical

Reason:

- Space has already proved the workflow.
- Aerospace and propulsion need strong representative-model accuracy.
- Drone and robotics share many visible mechanisms and can reuse drawing language.
- Mechanical and marine need section/cutaway logic.
- Medical should come later because it needs careful human-fit and anatomical-device clarity.

## Next Documentation Tasks

Before drawing more images:

1. Finish Space single-part documentation from the Space spec.
2. Create `PROPULSION_SUPERQUALITY_BLUEPRINT_SPEC_2026-05-13.md`.
3. Create `DRONE_SUPERQUALITY_BLUEPRINT_SPEC_2026-05-13.md`.
4. Continue category specs until all 8 categories have a design source.

Only after those specs exist should final superquality image passes begin.
