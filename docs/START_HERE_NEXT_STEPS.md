# Start Here — What Exists And What To Build Next

This is the main orientation document for the next development phase.

The current repository is upload-ready as a file-only/static Blueprint NPU Design System. It is not yet a working local AI app.

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
  - `docs/IPEX_OLLAMA_DOWNLOADS.md`
- Future model behavior notes:
  - `learning/HOWTO.md`
  - `learning/Modelfile.template`
  - `docs/DESIGN_MODEL_TUNING_ROADMAP.md`

### Not Present Yet

- No active backend server
- No real browser-to-model API call
- No downloaded model
- No bundled Ollama/IPEX runtime
- No Python implementation
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

But today that screen is a mock/static prototype. Its buttons simulate terminal output in the browser. They do not call a real server or model yet.

So the correct statement is:

```text
UI concept exists.
Real app wiring does not exist yet.
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

### Phase 2 — Minimal Local Bridge

Goal:

```text
Add one tiny local bridge that the browser can call.
```

Planned shape:

```text
Browser HTML
  -> local Blueprint bridge
  -> Ollama IPEX API at http://127.0.0.1:11434/api/generate
```

The bridge should do only a few things at first:

- accept a design brief
- load one selected preset prompt
- include `schema_v6.json` guidance
- call the Ollama-compatible API
- return text or JSON-like output to the browser

Done when:

- `Minimal.html` can send one brief to a local endpoint
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

The first real implementation task should be:

```text
Build a minimal local bridge that sends one brief + one preset prompt to Ollama IPEX and returns the response to Minimal.html.
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

