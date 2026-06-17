# Start Here — What Exists And What To Build Next

This is the main orientation document for the next development phase.

The current repository is upload-ready as a file-first/static Blueprint NPU Design System. It also includes a small optional local server for static serving and schema validation. It is not yet a bundled local AI runtime.

## Current Status

### Already Present

- Static browser UI pages:
  - `index.html`
  - `Minimal.html`
  - `Dashboard.html`
  - `Assembly.html`
  - `CFD.html`
  - `FMEA.html`
  - `Materials.html`
  - `PrintQueue.html`
  - other design-system/reference pages
- Shared visual system:
  - `colors_and_type.css`
  - `TopNav.jsx`
  - `assets/`
  - `preview/`
  - `ui_kits/`
- Canonical output contract:
  - `schema_v6.json`
- First-class design presets:
  - `prompts/presets/propulsion`
  - `prompts/presets/general_mechanical`
  - `prompts/presets/drone_aero`
  - `prompts/presets/electronics_enclosure`
  - `prompts/presets/repair_fixture`
- Future runtime notes:
  - `config/backend.json`
  - `server/README.md`
  - `server/serve.py`
  - `docs/IPEX_OLLAMA_DOWNLOADS.md`
- Future model behavior notes:
  - `learning/HOWTO.md`
  - `learning/Modelfile.template`
  - `docs/DESIGN_MODEL_TUNING_ROADMAP.md`
  - `docs/FIVE_SEED_DESIGN_MODEL_PIPELINE.md`
  - `docs/DESIGN_MODEL_BUILDING_REALITY_AND_TREE.md`
- First design-thinking baseline:
  - `docs/CUBESAT_REDESIGN_V1.md`
  - `data/blueprint/cubesat_redesign_package_v1.json`
  - `data/blueprint/cubesat_design_thinking_v1.jsonl`
  - `scripts/validate_cubesat_redesign_v1.py`
- Second design-thinking baseline:
  - `docs/TILTROTOR_REDESIGN_V1.md`
  - `data/blueprint/tiltrotor_redesign_package_v1.json`
  - `data/blueprint/tiltrotor_design_thinking_v1.jsonl`
  - `scripts/validate_tiltrotor_redesign_v1.py`
- Third design-thinking baseline:
  - `docs/ROBOT_ARM_REDESIGN_V1.md`
  - `data/blueprint/robot_arm_redesign_package_v1.json`
  - `data/blueprint/robot_arm_design_thinking_v1.jsonl`
  - `scripts/validate_robot_arm_redesign_v1.py`
- Fourth design-thinking baseline:
  - `docs/SMALL_LAUNCH_VEHICLE_REDESIGN_V1.md`
  - `data/blueprint/small_launch_vehicle_redesign_package_v1.json`
  - `data/blueprint/small_launch_vehicle_design_thinking_v1.jsonl`
  - `scripts/validate_small_launch_vehicle_redesign_v1.py`
- Fifth design-thinking baseline:
  - `docs/LONG_RANGE_RECON_WING_REDESIGN_V1.md`
  - `data/blueprint/long_range_recon_wing_redesign_package_v1.json`
  - `data/blueprint/long_range_recon_wing_design_thinking_v1.jsonl`
  - `scripts/validate_long_range_recon_wing_redesign_v1.py`

### Not Present Yet

- No bundled backend runtime
- No proxy-style browser-to-model bridge endpoint
- No downloaded model
- No bundled Ollama/IPEX runtime
- No npm app or build system
- No training or fine-tuning script
- No curated fine-tuning dataset
- No live save/retrain loop
- No live NPU/OpenVINO implementation

## Important Clarification About The UI

The UI is partially present as static HTML/design-system screens.

`Minimal.html` already shows the intended user flow:

```text
pick model -> enter brief -> generate 3 variants -> choose best/worst -> retrain
```

That screen is no longer purely static. It has first-pass browser-side wiring for:

```text
Minimal.html
  -> direct Ollama-compatible API calls at 127.0.0.1:11434
  -> schema validation through server/serve.py at 127.0.0.1:8080/validate
```

It still does not include a packaged runtime, proxy bridge, training system, or real save/retrain loop.

So the correct statement is:

```text
UI concept exists.
Minimal local wiring exists.
Packaged runtime/proxy bridge does not exist yet.
```

## Current Learning Data Situation

There is some useful source material already:

- HTML design/reference pages
- engineering domain pages such as CFD, FMEA, Materials, Loads, Risk, Test
- `schema_v6.json`
- preset prompts in `prompts/presets/`
- learning notes in `learning/`
- roadmap docs in `docs/`

But this is not yet a model-training dataset.

What exists now is best described as:

```text
raw local context + prompt templates + schema contract
```

What still needs to be made later:

```text
curated training/evaluation examples
```

Do not start with fine-tuning. Start with prompt + retrieval + schema-aware output.

## Simplest Build Order

### Phase 0 — Upload The Static Repository

Goal:

```text
Put this file-only package on GitHub.
```

Done when:

- repository opens on GitHub
- `README.md` explains static/file-only status
- no runtime archives or model files are committed
- `schema_v6.json` is visible at repo root
- preset folders are visible

This phase is effectively complete in the prepared folder.

### Phase 1 — External Portable Runtime

Goal:

```text
Get Ollama IPEX-LLM portable running outside the repo.
```

Use later:

- IPEX-LLM `v2.3.0-nightly`
- Windows: `ollama-ipex-llm-2.3.0b20250725-win.zip`
- Ubuntu/Linux: `ollama-ipex-llm-2.3.0b20250725-ubuntu.tgz`
- first model: `qwen2.5:7b`

Keep this outside the GitHub repository, for example:

```text
C:\Ollama-IPEX\
```

Done when:

- external Ollama IPEX runtime starts
- `http://127.0.0.1:11434` responds
- one small model can answer a simple prompt

Do not solve UI, training, or NPU in this phase.

### Phase 2 — Minimal Local Wiring

Goal:

```text
Make the existing Minimal.html flow easy to run and verify locally.
```

Current shape:

```text
Browser HTML
  -> Ollama-compatible API at http://127.0.0.1:11434/api/generate
  -> Blueprint validation API at http://127.0.0.1:8080/validate
```

The local flow should do only a few things at first:

- accept a design brief
- use the selected in-page preset prompt
- include `schema_v6.json` guidance
- call the Ollama-compatible API
- return JSON-like output to the browser
- validate final output against `schema_v6.json`

Done when:

- `python server/serve.py --no-browser` serves `Minimal.html`
- `GET /schema` returns `schema_v6.json`
- `POST /validate` validates a sample object
- `Minimal.html` can send one brief to Ollama
- the model response appears in the UI
- no training, saving, or retraining is attempted yet

### Phase 3 — Schema-Aware Prompting

Goal:

```text
Make the model answer like a Blueprint design-review assistant.
```

Use:

- `schema_v6.json`
- `config/presets.json`
- selected `prompts/presets/*/sys_template.txt`
- selected `prompts/presets/*/usr_template.txt`

Output should include:

- requirements
- constraints
- part tree assumptions
- verification items
- risks
- print/manufacturing constraints
- missing questions

Done when:

- responses are consistently organized around `schema_v6.json`
- the model asks useful missing-data questions
- propulsion/aero/combustion stays conceptual and safe

### Phase 4 — Local Retrieval

Goal:

```text
Let the assistant use local project documents as context.
```

Start simple:

- manually attach or paste one HTML page
- then add a local file picker or index later
- keep citations to local filenames

Useful source files:

- `CFD.html`
- `FMEA.html`
- `Materials.html`
- `Loads.html`
- `Risk.html`
- `Test.html`
- `schema_v6.json`
- `prompts/presets/*`

Done when:

- the model can answer based on selected local files
- major recommendations mention which file informed them
- no hidden internet dependency is required

### Phase 5 — Evaluation Dataset

Goal:

```text
Create test examples before training.
```

Create a small local dataset later, for example:

```text
data/eval/
  general_mechanical.jsonl
  propulsion_review.jsonl
  drone_aero.jsonl
  electronics_enclosure.jsonl
  repair_fixture.jsonl
```

Each row should include:

- brief
- selected preset
- expected missing questions
- expected risk categories
- expected schema sections
- safety notes if needed

This is evaluation data, not training data.

Done when:

- 30-50 examples exist
- model answers can be compared before/after prompt changes

Current seed:

```text
CubeSat Redesign V1 already includes 25 rule+data examples focused on assembly/serviceability efficiency.
Tiltrotor Redesign V1 adds 25 moving-interface drone examples focused on nacelle, tilt-axis, battery, wiring, and service module access.
Robot Arm Redesign V1 adds 25 kinematic-chain examples focused on J1-J6 axes, joint cartridges, cable routing, wrist service, and tool flange access.
Small Launch Vehicle Redesign V1 adds 25 staged cutaway examples focused on tank/engine display modules and flow readability.
Long-Range Recon Wing Redesign V1 adds 25 long-range mission-structure examples focused on sensor bay, mission payload, CG rail, spar datum, and elevon service.
Use these five as the fixed first-cycle design-thinking seeds. Do not expand to more target vehicles until the five-seed model pipeline is stable.
```

### Phase 6 — Training Dataset

Goal:

```text
Only after the prompt/retrieval loop works, prepare tuning data.
```

Possible later structure:

```text
data/train/
  design_review_sft.jsonl
  preference_pairs_dpo.jsonl
```

Start tiny and high quality.

Training examples should teach:

- schema-aware structure
- design-review tone
- missing constraint detection
- risk and verification thinking
- safe handling of advanced engineering topics

For the current first cycle, use the five fixed seed JSONL files as the data accumulation base. The first trained model should output design judgment and verification suggestions before attempting full design-package generation.

Do not train on private, restricted, export-controlled, or unsafe material without review.

### Phase 7 — Optional Fine-Tuning

Goal:

```text
Fine-tune only if prompting and retrieval are not enough.
```

This is not the first move.

Fine-tuning should be considered only after:

- local bridge works
- model response format is stable
- evaluation examples exist
- failure cases are understood

## Recommended First Real Development Task

The first real verification task should be:

```text
Run the local server, confirm Ollama model discovery, and generate one small Blueprint response from Minimal.html.
```

Do not begin with:

- full UI redesign
- fine-tuning
- NPU/OpenVINO
- model conversion
- multi-model management
- save/retrain loop

Those can wait.

## One-Sentence Roadmap

```text
Upload static repo -> run external Ollama IPEX -> add tiny bridge -> make schema-aware prompts -> add local retrieval -> build eval data -> only then consider fine-tuning.
```
