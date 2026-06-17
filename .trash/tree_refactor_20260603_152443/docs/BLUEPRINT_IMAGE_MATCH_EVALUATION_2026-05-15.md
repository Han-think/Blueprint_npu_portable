# Blueprint Image Match Evaluation - 2026-05-15

This document separates visual/data readiness from simple file coverage.

The project now has full assembly-specific part image coverage. This does not mean every whole-assembly three-axis image is already a final training-base image. The correct interpretation is:

- Part image coverage is complete.
- Space, Aerospace, and `turbofan_engine` are the current high-confidence master image set.
- Remaining assemblies are useful as coverage/structure data, but need category spec and visual review before being promoted to training-base status.

## Evaluation Summary

| Area | Result | Score | Meaning |
|---|---:|---:|---|
| Assembly-specific part image coverage | `359/359` | `9.5/10` | Every mapped assembly part has a dedicated SVG asset. |
| SVG parse validity | `698/698 OK` | `10/10` | The image corpus is structurally readable by tooling. |
| UI path matching | `pass` | `9/10` | Dedicated assembly part paths match the expected `vendor/img/assembly_parts/<vehicle_id>/<part_id>.svg` structure. |
| Master visual fidelity, first wave | `strong` | `8.5/10` | Space, Aerospace, and turbofan have representative bases and refined 3-axis images. |
| Whole-corpus superquality readiness | `mixed` | `6.8/10` | Many later assemblies still have 3-axis `coverage` status even though their part images exist. |
| Learning-data readiness | `usable with filtering` | `7.5/10` | Use master rows first; keep coverage rows as expansion/weak-label data. |

## Training Readiness Rules

| Readiness | Required Conditions | Allowed Use |
|---|---|---|
| `train_base_ready` | 3-axis is `master` or better, part images complete, representative basis locked | High-confidence supervised examples |
| `train_aug_ready` | Part images complete, 3-axis is `coverage`, representative basis locked | Augmentation or weak-label training only |
| `hold_for_spec` | Category spec is missing or visual basis is not reviewed | Do not use for core model training |
| `superquality_candidate` | Master assets plus part-level consistency review and protection | Future high-purity base-model candidate |

## Recommended Dataset Split

| Split | Assemblies | Part Images | Use |
|---|---:|---:|---|
| High-confidence master seed | `11` | `97` | First base-model / adapter seed data |
| Coverage expansion pool | `29` | `262` | Later fine-tuning after visual audit |
| Total | `40` | `359` | Full current assembly part corpus |

The high-confidence master seed is:

- Space: `small_launch_vehicle`, `cubesat_3u`, `lunar_lander`, `space_telescope`, `orbital_module`
- Aerospace: `fighter_f_class`, `supersonic_sst`, `civil_airliner`, `turboprop_transport`, `heavy_helicopter`
- Propulsion: `turbofan_engine`

## Assembly Evaluation Table

| Category | Vehicle | 3-Axis Quality | Part Images | Readiness | Recommendation |
|---|---|---|---|---|---|
| Space | `small_launch_vehicle` | `master` | `10/10 master` | `train_base_ready` | Keep as rocket reference seed. |
| Space | `cubesat_3u` | `master` | `8/8 master` | `train_base_ready` | Keep as compact spacecraft reference seed. |
| Space | `lunar_lander` | `master` | `8/8 master` | `train_base_ready` | Keep as lander/mechanism reference seed. |
| Space | `space_telescope` | `master` | `8/8 master` | `train_base_ready` | Keep as optical payload reference seed. |
| Space | `orbital_module` | `master` | `8/8 master` | `train_base_ready` | Keep as orbital module reference seed. |
| Aerospace | `fighter_f_class` | `master` | `10/10 master` | `train_base_ready` | Keep as F-15-class twin-engine reference seed. |
| Aerospace | `supersonic_sst` | `master` | `10/10 master` | `train_base_ready` | Keep as Concorde-class slender transport reference seed. |
| Aerospace | `civil_airliner` | `master` | `9/9 master` | `train_base_ready` | Keep as A320-class transport reference seed. |
| Aerospace | `turboprop_transport` | `master` | `8/8 master` | `train_base_ready` | Keep as ATR72-class transport reference seed. |
| Aerospace | `heavy_helicopter` | `master` | `8/8 master` | `train_base_ready` | Keep as CH-47-class tandem rotor reference seed. |
| Propulsion | `turbofan_engine` | `master` | `10/10 master` | `train_base_ready` | Keep as turbofan propulsion reference seed. |
| Propulsion | `solid_rocket_motor` | `coverage` | `8/8 master` | `train_aug_ready` | Promote after propulsion category spec and 3-axis master pass. |
| Propulsion | `electric_motor_assy` | `coverage` | `8/8 master` | `train_aug_ready` | Promote after motor category spec and 3-axis master pass. |
| Propulsion | `marine_propeller` | `coverage` | `8/8 master` | `train_aug_ready` | Promote after propeller category spec and 3-axis master pass. |
| Propulsion | `ion_thruster_assy` | `coverage` | `8/8 master` | `train_aug_ready` | Promote after electric propulsion spec and 3-axis master pass. |
| Drone | `racing_quad_5in` | `coverage` | `13/13 master` | `train_aug_ready` | Promote after drone category spec and 3-axis master pass. |
| Drone | `cinelifter_x8` | `coverage` | `14/14 master` | `train_aug_ready` | Promote after drone category spec and 3-axis master pass. |
| Drone | `wing_long_range` | `coverage` | `13/13 master` | `train_aug_ready` | Promote after fixed-wing drone spec and 3-axis master pass. |
| Drone | `cyclocopter_demo` | `coverage` | `12/12 master` | `train_aug_ready` | Promote after cyclorotor spec and 3-axis master pass. |
| Drone | `tiltrotor_vtol` | `coverage` | `13/13 master` | `train_aug_ready` | Promote after VTOL spec and 3-axis master pass. |
| Robotics | `arm_6dof` | `coverage` | `9/9 master` | `train_aug_ready` | Promote after robotics category spec and 3-axis master pass. |
| Robotics | `mars_rover` | `coverage` | `9/9 master` | `train_aug_ready` | Promote after rover category spec and 3-axis master pass. |
| Robotics | `quadruped_walker` | `coverage` | `8/8 master` | `train_aug_ready` | Promote after legged robotics spec and 3-axis master pass. |
| Robotics | `delta_parallel_robot` | `coverage` | `9/9 master` | `train_aug_ready` | Promote after parallel robot spec and 3-axis master pass. |
| Robotics | `humanoid_biped` | `coverage` | `9/9 master` | `train_aug_ready` | Promote after humanoid category spec and 3-axis master pass. |
| Mechanical | `harmonic_drive` | `coverage` | `8/8 master` | `train_aug_ready` | Promote after precision drivetrain spec and 3-axis master pass. |
| Mechanical | `suspension_assy` | `coverage` | `8/8 master` | `train_aug_ready` | Promote after suspension category spec and 3-axis master pass. |
| Mechanical | `cnc_tool_changer` | `coverage` | `8/8 master` | `train_aug_ready` | Promote after machine-tool spec and 3-axis master pass. |
| Mechanical | `hydraulic_cylinder` | `coverage` | `8/8 master` | `train_aug_ready` | Promote after actuator spec and 3-axis master pass. |
| Mechanical | `precision_linkage` | `coverage` | `8/8 master` | `train_aug_ready` | Promote after linkage spec and 3-axis master pass. |
| Marine | `rov_inspection` | `coverage` | `9/9 master` | `train_aug_ready` | Promote after marine robotics spec and 3-axis master pass. |
| Marine | `usv_autonomous` | `coverage` | `8/8 master` | `train_aug_ready` | Promote after USV spec and 3-axis master pass. |
| Marine | `underwater_glider` | `coverage` | `8/8 master` | `train_aug_ready` | Promote after underwater glider spec and 3-axis master pass. |
| Marine | `research_submarine` | `coverage` | `8/8 master` | `train_aug_ready` | Promote after submarine spec and 3-axis master pass. |
| Marine | `wave_glider_asv` | `coverage` | `8/8 master` | `train_aug_ready` | Promote after wave glider spec and 3-axis master pass. |
| Medical | `myoelectric_hand` | `coverage` | `8/8 master` | `train_aug_ready` | Promote after medical device spec and 3-axis master pass. |
| Medical | `powered_afo` | `coverage` | `8/8 master` | `train_aug_ready` | Promote after assistive orthosis spec and 3-axis master pass. |
| Medical | `surgical_robot_arm` | `coverage` | `8/8 master` | `train_aug_ready` | Promote after surgical robotics spec and 3-axis master pass. |
| Medical | `cochlear_implant` | `coverage` | `8/8 master` | `train_aug_ready` | Promote after implant device spec and 3-axis master pass. |
| Medical | `powered_exoskeleton` | `coverage` | `8/8 master` | `train_aug_ready` | Promote after exoskeleton spec and 3-axis master pass. |

## What This Means For Model Training

Use the current corpus in two layers:

1. Seed the model with the 11 high-confidence master assemblies.
2. Add the remaining 29 assemblies only with explicit quality labels.

Do not collapse `coverage`, `master`, and `superquality` into one label. That would teach the model that rough navigation images and high-quality reference drawings are equally authoritative.

Recommended metadata fields for the next JSONL builder:

```json
{
  "vehicle_id": "small_launch_vehicle",
  "category": "Space",
  "asset_kind": "assembly_part",
  "part_id": "p1",
  "part_quality": "master",
  "axis_quality": "master",
  "training_readiness": "train_base_ready",
  "asset_path": "vendor/img/assembly_parts/small_launch_vehicle/p1.svg"
}
```

## Next Actions

1. Build a JSONL export script that reads the assembly rows and emits quality-labeled training examples.
2. Start training only from `train_base_ready` examples.
3. Promote one category at a time from `train_aug_ready` to `train_base_ready` after category spec and 3-axis master review.
4. Reserve `superquality` for assets that pass both visual consistency and protection checks.

## UI Manual Curation Loop

Implemented in:

```text
Minimal.html
```

The UI now supports a small human-in-the-loop selection pass:

- Single Part mode:
  - `generate 3`
  - pick one variant
  - after completion, use `keep data` or `queue`
- Full Assembly mode:
  - `generate assembly`
  - after completion, use `keep data` or `queue`
- Curation Queue:
  - mark rows as `keep`, `reject`, or `hold`
  - add a short review note
  - download `kept jsonl`
  - download `all jsonl`
- Visual review:
  - Single Part output now opens with a `Blueprint` tab first
  - the result card first shows the existing reference SVG asset when available
  - the modal first shows the assembly-specific or preset reference SVG
  - the generated `part_tree` / `geometry_ops` box preview is only a secondary structure check
  - the existing `3D View` remains available for rotation/zoom/STL export
  - Assembly mode keeps its vehicle schematic and 3D assembly view
  - completed assemblies are automatically added to the curation queue as `candidate`

This keeps raw generation separate from selected training data. Only `keep` rows should be merged into the next supervised dataset.

## Curation Auto-Eval

Implemented script:

```text
scripts/evaluate_blueprint_curation.js
```

Usage:

```text
node scripts/evaluate_blueprint_curation.js <downloaded_curation_jsonl>
```

Outputs:

```text
data/blueprint/curation_evaluated/<name>.accepted.jsonl
data/blueprint/curation_evaluated/<name>.review.jsonl
data/blueprint/curation_evaluated/<name>.rejected.jsonl
data/blueprint/curation_evaluated/<name>.summary.json
```

The first pass is intentionally conservative:

- `accept`: structurally good enough to merge after spot-check
- `review`: possible keeper, needs human judgement
- `reject`: schema/validation/detail quality is too weak

Manual `reject` always stays rejected. Manual `keep` can promote a borderline `review` to accepted, but cannot fully override a hard automatic reject.

## Generation Quality Fixes

2026-05-15 follow-up after first live assembly generation:

- The first run produced many parts with only `4` geometry operations.
- Root cause: the Stage 2 prompt example itself showed only four operations, so small models copied the weak example.
- Stage 2 now requires `8` to `16` geometry operations for assembly parts.
- Stage 2 now asks for main body, mounting/interface, subtract/drill/pocket, fillet/chamfer, and engrave/label operations.
- Assembly part prompts now include the representative basis, reference SVG path, preset fallback SVG, and a requirement to avoid generic block output.
- Output token budget was raised from `1400` to `2200`.
- Visual metadata is now attached after schema validation so reference SVG fields do not create avoidable validation errors.
- Explicit `2D View` buttons were added so users do not need to discover the blueprint tab indirectly.
- Category design context is now injected into assembly part prompts.
- See `BLUEPRINT_GENERATION_CONTEXT_PACKS_2026-05-15.md`.
- Non-Space/Aerospace category specs are now created for Propulsion, Drone, Robotics, Mechanical, Marine, and Medical.
- Design generation and learning accumulation are separated in `BLUEPRINT_LAYER_BOUNDARY_2026-05-15.md`.
- `design-pack-v3`: 3D renderer now understands generated dimension aliases such as `d_mm`, `h_mm`, `radius_mm`, `depth_mm`, `w_mm`, and `l_mm`.
- `design-pack-v3`: Assembly mode has an explicit `2D 설계도` button that scrolls back to the schematic view.
- `design-pack-v4`: assembly part prompts now include part-specific geometry hints so nozzle, chamber, turbopump, tank, fairing, fin, and avionics parts do not all follow the same generic operation pattern.
- `design-pack-v5`: Stage 1/2/3/4 partial outputs are no longer validated against the full `schema_v6`; only final merged outputs are full-schema validated. This removes false retry spam from missing fields that belong to later stages.
- `design-pack-v6`: Assembly mode wording and prompts now treat nozzle/chamber/tank/etc. as fixed BOM subsystems inside one complete vehicle, not as standalone single-part choices.
- `design-pack-v7`: Full Assembly UI now shows only the category selector plus vehicle templates. Single-part type/config chips and the `SINGLE-PART SCHEMATIC` preview are hidden in assembly mode.
- `design-pack-v8`: Stage 2 now requires explicit `args.at: [x,y,z]` coordinates for geometry operations. The blueprint modal shows a coordinate audit and generated X/Y coordinate map, and exported records include `_coord_audit`.
- `design-pack-v9`: Small Launch Vehicle part 3D view now falls back to part-specific reference scaffolds when generated geometry is coordinate-poor or box-dominated, instead of showing only generic boxes.
- `design-pack-v10`: Full Assembly 3D view for Small Launch Vehicle now uses a rocket-shaped reference scaffold instead of extruding schematic zones into generic boxes.
- `design-pack-v11`: Full Assembly 3D reference scaffolds now cover the 11 high-confidence master seed assemblies. Other assemblies are explicitly labeled as schematic extrusion placeholders until their category 3D pass is promoted.
- `design-pack-v12`: Blueprint review now prioritizes actual generated design output. The primary 2D drawing is rendered directly from generated `geometry_ops` coordinates/dimensions, reference SVGs are labeled as non-generated targets, part 3D no longer auto-hides poor generated geometry behind a reference scaffold, and exports include `_generated_design_audit`.
- `design-pack-v13`: Actual generated 2D review now uses three separate orthographic projections from the same generated geometry: TOP `X/Y`, FRONT `X/Z`, and SIDE `Y/Z`. The 3D header now states the same axis convention.
- `design-pack-v14`: Run control now records seed and attempt metadata, passes seed into Ollama generation options, and includes run metadata in blueprint JSON, assembly bundles, and curation JSONL exports.
- `design-pack-v15`: The generated 2D panel is relabeled as a generated operation projection, not a finished CAD drawing, and explicitly reports when `geometry_ops` are missing `args.at` placement coordinates.
- `design-pack-v16`: Assembly mode now has a repeat/batch generator. `generate ×N` runs sequential attempts with auto-incremented seeds and queues each assembly candidate for later 3D review and keep/reject curation.
- `design-pack-v17`: Fixed a JSX compile failure in the three-view empty-state text, restoring the design generation UI after the repeat/batch update.
- `design-pack-v18`: Run Control seed/repeat inputs now use forced dark input styling so typed values remain visible.
- `design-pack-v19`: Curation Queue now supports checkbox selection, selected keep/reject, selected JSONL export, and per-candidate JSON export so review can be done one-by-one or as a batch.
- `design-pack-v20`: Curation Queue rows now include a `3D` review button. Single-part candidates open their generated geometry viewer, and assembly candidates reconstruct the queued assembly bundle in the 3D assembly viewer for visual keep/reject decisions.
- `design-pack-v21`: Curation Queue is persisted in browser `localStorage` so review candidates survive page refreshes while the user is doing visual selection.
- `design-pack-v22`: Added the first Engineering Scorecard pass. Curation records now receive a 0-100 engineering score, `keep_candidate` / `review` / `reject_suggested` verdict, category scores, and short findings based on coordinate placement, operation depth, shape diversity, domain fit, verification/risk, manufacturing context, and assembly role coverage.
- `design-pack-v23`: Added an Engineering Scorecard detail modal from each curation row. Reviewers can inspect category bars, findings, generated geometry audit metrics, and assembly part-level scores before deciding keep/reject.
- `design-pack-v24`: Added the first improvement-loop path. Curation rows now have a `loop` action; assembly candidates inject scorecard findings into a new assembly regeneration run with a separated seed and parent metadata, while single-part candidates load an improved brief for the next `generate 3` run.
- `design-pack-v25`: Shifted curation policy to assembly-primary training data. `kept assembly` exports only kept assembly bundles, single-part outputs are labeled/exported as auxiliary references, and assembly subsystem prompts now require finer internal feature decomposition inside each BOM part.
- `design-pack-v26`: Raised assembly subsystem quality targets. Stage 1 now asks for 5-9 internal child features, Stage 2 asks for 12-24 coordinate-bearing geometry operations with distributed coordinates and richer interfaces, and the Engineering Scorecard now scores internal feature decomposition plus coordinate distribution.
- `design-pack-v27`: Applied assembly part detail profiles across the full vehicle set. Each subsystem prompt now injects domain/keyword-specific internal feature guidance for space, aerospace, propulsion, drone, robotics, mechanical, marine, and medical assemblies, and the Scorecard now also scores interface/service feature depth.
- `design-pack-v28`: Added Assembly Dataset Contract v1 as the guiding data structure. Assembly bundles now carry a `dataset_contract` with assembly intent, coordinate convention, required reasoning chain, physics paths, subsystem contract, integration opportunities, and future CFD/FEA/thermal simulation hooks.
- `design-pack-v29`: Added an internal P0 subsystem-planning stage before CAD generation. Each assembly subsystem now first records role, physics paths, adjacent interfaces, internal feature targets, integration opportunities, and verification focus; downstream S1-S4 prompts use that plan, and assembly exports preserve `_subsystem_plan` plus `_pipeline_stages`.
- `design-pack-v30`: Hardened P0 coverage for all Full Assembly templates. Every fixed BOM subsystem now receives a normalized `_subsystem_plan`; if the model fails to emit a usable P0 JSON, a deterministic local fallback plan is inserted so downstream S1-S4 stages and exports never lose the planning layer.

## JSONL Export

Implemented script:

```text
scripts/build_blueprint_training_manifest.js
scripts/build_blueprint_sft_dataset.js
```

Expected outputs:

```text
data/blueprint/blueprint_image_training_manifest_2026-05-15.jsonl
data/blueprint/blueprint_image_training_seed_2026-05-15.jsonl
data/blueprint/blueprint_image_training_manifest_summary_2026-05-15.json
data/blueprint/train_blueprint_full_labeled_sft_2026-05-15.jsonl
data/blueprint/train_blueprint_seed_sft_2026-05-15.jsonl
data/blueprint/train_blueprint_seed_text_2026-05-15.txt
data/blueprint/train_blueprint_sft_summary_2026-05-15.json
madang_learning_core_handoff_20260514_225416/data/blueprint/train_blueprint_seed_sft_2026-05-15.jsonl
madang_learning_core_handoff_20260514_225416/data/blueprint/train_blueprint_seed_text_2026-05-15.txt
```

Verified output counts:

- Full manifest: `359` JSONL records
- High-confidence seed manifest: `97` JSONL records
- Missing assembly part assets: `0`
- Missing evaluation rows: `0`
- Full SFT dataset: `359` JSONL records
- High-confidence seed SFT dataset: `97` JSONL records
- Handoff seed SFT dataset: `97` JSONL records
