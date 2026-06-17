# Design Model Tuning Roadmap

This is a planning note for later work. The current repository remains a file-only/static design-system package.

No model training, fine-tuning, download, conversion, backend service, or runtime integration is included in this step.

For the overall build order, start with `docs/START_HERE_NEXT_STEPS.md`.

## Goal

Make the optional local model behave like a Blueprint NPU design-review assistant:

- read project pages and engineering notes
- organize answers around `schema_v6.json`
- use preset/domain context from `prompts/presets/`
- help with requirements, interfaces, risks, verification, materials, print constraints, and traceability
- keep propulsion, aero, combustion, CFD, and advanced engineering as first-class domains
- avoid unsafe step-by-step manufacturing or operational instructions

## Current Focus: Five Seeds Only

The first design-model cycle is fixed around five seed targets only:

- CubeSat Redesign V1
- Tiltrotor Drone Redesign V1
- Robot Arm Redesign V1
- Small Launch Vehicle Redesign V1
- Long-Range Recon Wing Redesign V1

Do not expand the first training direction to more target vehicles yet. The immediate objective is to accumulate better examples on these five axes and use them to teach structured design judgment.

For the focused pipeline, see `docs/FIVE_SEED_DESIGN_MODEL_PIPELINE.md`.

For the model-building reality, inheritance structure, and data tree, see `docs/DESIGN_MODEL_BUILDING_REALITY_AND_TREE.md`.

## Easiest Later Path

Start with prompt and retrieval behavior before any fine-tuning:

1. Use IPEX-LLM Ollama portable as the external runtime.
2. Start with `qwen2.5:7b`.
3. Load the relevant preset prompt, for example `prompts/presets/propulsion/sys_template.txt`.
4. Add the current page or document content as context.
5. Ask the model to return sections that map to `schema_v6.json`.

This keeps the first bridge simple and reversible.

## Later Learning Stages

### Stage 1 — Prompt Pack

Use the existing preset folders:

- `prompts/presets/propulsion`
- `prompts/presets/general_mechanical`
- `prompts/presets/drone_aero`
- `prompts/presets/electronics_enclosure`
- `prompts/presets/repair_fixture`

Expected output style:

- concise design review
- schema-aware sections
- risk and verification focus
- Korean or English as requested

### Stage 2 — Local Retrieval

Index or attach local project material:

- HTML pages
- `schema_v6.json`
- preset templates
- docs
- user-authored design notes

The model should cite which local file or page informed each major recommendation.

### Stage 3 — Evaluation Set

Create a small test set before tuning. For the current first cycle, derive it from the five fixed seed datasets:

- CubeSat: static structure / maintenance access
- Tiltrotor: moving interface / nacelle and battery service
- Robot Arm: axis / joint cartridge / cable service
- Small Launch Vehicle: cutaway flow readability
- Long-Range Recon Wing: mission payload / CG / spar readability

Evaluate whether answers:

- preserve schema fields
- identify missing constraints
- ask useful follow-up questions
- avoid unsupported fabrication details
- separate assumptions from known facts

### Stage 4 — Fine-Tuning Candidate

Only consider fine-tuning after the prompt and retrieval loop is stable.

Possible training examples:

- prompt: `existing_structure` plus `problem` plus `constraint`
- target: `reasoning.classification` and `reasoning.rule`
- target: guarded redesign proposal
- target: retained service access and verification checklist
- later target: partial `schema_v6_blueprint` sections

Do not train on private or export-controlled material unless its use has been reviewed.

## Safety Boundary

For advanced engineering domains, the assistant should stay at conceptual design-review and documentation level unless the user supplies a safe, bounded context.

Preferred behavior:

- ask for missing requirements
- flag risks and uncertainty
- recommend verification categories
- map outputs to `schema_v6.json`
- avoid operational, weaponization, or hazardous step-by-step instructions

## Files To Keep Connected

- `schema_v6.json`
- `docs/FIVE_SEED_DESIGN_MODEL_PIPELINE.md`
- `docs/DESIGN_MODEL_BUILDING_REALITY_AND_TREE.md`
- `config/presets.json`
- `config/backend.json`
- `docs/IPEX_OLLAMA_DOWNLOADS.md`
- `learning/HOWTO.md`
- `learning/Modelfile.template`
- `prompts/presets/*`
