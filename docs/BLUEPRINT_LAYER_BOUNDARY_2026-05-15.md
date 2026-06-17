# Blueprint Layer Boundary - 2026-05-15

This project has two separate responsibilities:

1. Design generation
2. Learning/data accumulation

They must stay connected, but not mixed.

## Design Layer

Purpose:

- Generate or review single-part and assembly blueprints.
- Make each result inspectable in 2D and optionally 3D.
- Use representative product basis and category-specific design rules.

Inputs:

- `BLUEPRINT_REPRESENTATIVE_BASE_LOCKS_2026-05-13.md`
- `SPACE_SUPERQUALITY_BLUEPRINT_SPEC_2026-05-13.md`
- `AEROSPACE_SUPERQUALITY_BLUEPRINT_SPEC_2026-05-13.md`
- `PROPULSION_SUPERQUALITY_BLUEPRINT_SPEC_2026-05-15.md`
- `DRONE_SUPERQUALITY_BLUEPRINT_SPEC_2026-05-15.md`
- `ROBOTICS_SUPERQUALITY_BLUEPRINT_SPEC_2026-05-15.md`
- `MECHANICAL_SUPERQUALITY_BLUEPRINT_SPEC_2026-05-15.md`
- `MARINE_SUPERQUALITY_BLUEPRINT_SPEC_2026-05-15.md`
- `MEDICAL_SUPERQUALITY_BLUEPRINT_SPEC_2026-05-15.md`
- assembly-specific SVG references under `vendor/img/assembly_parts/`

Outputs:

- Visual design result
- `schema_v6` JSON
- 2D reference view
- optional 3D sanity view

Design generation must not mention:

- training rewards
- dataset splits
- curation policy
- SFT conversion
- model fine-tuning

## Learning Layer

Purpose:

- Select, score, store, and convert generated outputs into training data.
- Keep accepted/review/rejected records separate.
- Preserve source model, prompt context, visual asset path, quality label, and human note.

Inputs:

- UI curation queue JSONL
- `BLUEPRINT_IMAGE_MATCH_EVALUATION_2026-05-15.md`
- `blueprint_image_training_manifest_2026-05-15.jsonl`
- `train_blueprint_seed_sft_2026-05-15.jsonl`
- `evaluate_blueprint_curation.js`

Outputs:

- accepted/review/rejected JSONL
- seed SFT dataset
- full labeled SFT dataset
- summary JSON

Learning data must not silently alter design references. If a generated output reveals a design-spec problem, update the design spec first, then regenerate.

## Connection Rule

The bridge is:

```text
Design output -> human/auto curation -> accepted learning record
```

Not:

```text
Training goal -> injected into design prompt
```

The design prompt should know what a good part looks like. The learning system should know whether the generated result is worth keeping.

