# Blueprint NPU

Portable, browser-first design system for local blueprint review, engineering domain presets, and design-to-print output documentation.

This repository is a file-first package. Most pages can be opened locally as static HTML and do not require Python, npm, pip, a model download, or a running backend. The optional `Minimal.html` validation flow uses the bundled Python helper in `server/serve.py`.

## Current Baseline

- Static HTML design-system pages for local browser use
- `schema_v6.json` as the canonical output contract
- Preset/domain resources under `prompts/presets/`
- First-class advanced propulsion, aero, combustion, CFD, and mechanical engineering resources
- Configuration contracts in `config/`
- Local static server and schema validation helper under `server/`
- Future notes for an optional proxy-style Ollama IPEX bridge

## Current Status In Plain Terms

The UI concept exists as static HTML pages. `Minimal.html` has first-pass local wiring for direct Ollama calls and schema validation, but the packaged runtime/proxy bridge is not built yet.

- Present: browser-first UI mockups/design-system pages
- Present: schema contract and preset prompts
- Present: planning docs for IPEX/Ollama and future design-model tuning
- Present: optional local static server with `/schema` and `/validate`
- Present: browser-side Ollama tag/model discovery and generation calls in `Minimal.html`
- Not present: curated training/fine-tuning dataset
- Not present: real save/retrain loop

Start with `docs/START_HERE_NEXT_STEPS.md` before building the runtime.

## Open Locally

Open `index.html` directly in a browser.

The HTML pages are intended to remain useful without a server for static reading/demo mode. `Minimal.html` can also be served through `server/serve.py` so schema validation works through `POST /validate`.

## Canonical Contract

`schema_v6.json` is the source of truth for generated Blueprint NPU output packages. Do not rename it, remove fields, or replace it with preset-specific contracts.

The contract currently covers:

- project brief and constraints
- part tree / BOM structure
- geometry operation intent
- CAD brief
- verification and risk records
- print profile and slicer job structure

## Preset Domains

Preset resources are first-class domain material, not disposable demos. The file-only package includes, where available:

- `prompts/presets/propulsion`
- `prompts/presets/general_mechanical`
- `prompts/presets/drone_aero`
- `prompts/presets/electronics_enclosure`
- `prompts/presets/repair_fixture`

The propulsion preset includes propulsion, aero, combustion, CFD, and advanced engineering framing as a primary selectable domain.

## Project Layout

```text
.
├── index.html
├── Dashboard.html
├── Minimal.html
├── Assembly.html
├── CFD.html
├── FMEA.html
├── Materials.html
├── PrintQueue.html
├── TopNav.jsx
├── colors_and_type.css
├── schema_v6.json
├── config/
│   ├── presets.json
│   └── backend.json
├── prompts/
│   └── presets/
├── docs/
├── learning/
├── preview/
├── ui_kits/
├── vendor/
├── assets/
├── server/
└── codex/
```

## Configuration Contracts

`config/presets.json` describes available preset/domain resources.

`config/backend.json` records the intended local runtime shape. It does not install, start, or download anything.

## Future Bridge

An optional proxy-style Ollama IPEX bridge may be added later. The current `Minimal.html` flow calls the Ollama-compatible API directly at `127.0.0.1:11434` and uses `server/serve.py` for static serving and schema validation. The intended external runtime basis is IPEX-LLM `v2.3.0-nightly` using the Ollama IPEX-LLM portable package.

For the simplest later setup, see `docs/IPEX_OLLAMA_DOWNLOADS.md`. In short:

- Windows runtime archive: `ollama-ipex-llm-2.3.0b20250725-win.zip`
- Ubuntu/Linux runtime archive: `ollama-ipex-llm-2.3.0b20250725-ubuntu.tgz`
- first model candidate: `qwen2.5:7b`
- primary acceleration target: Intel GPU/iGPU/Arc through IPEX-LLM
- NPU/OpenVINO remains a separate future evaluation

No OpenVINO conversion, model download, or bundled runtime is required here.

## Included Design-System Resources

- `colors_and_type.css` for visual tokens
- `assets/` for brand and SVG assets
- `preview/` for component and visual reference pages
- `ui_kits/` for browser UI kit references
- `learning/` for optional offline study-loop notes
- `docs/` for migration notes
- `docs/START_HERE_NEXT_STEPS.md` for the build order and current/missing pieces
- `docs/CUBESAT_REDESIGN_V1.md` for the first design-thinking baseline: existing product structure -> printable serviceable redesign package
- `docs/TILTROTOR_REDESIGN_V1.md` for the second design-thinking baseline: moving-interface drone structure -> printable serviceable redesign package
- `docs/ROBOT_ARM_REDESIGN_V1.md` for the third design-thinking baseline: kinematic-chain robot structure -> printable serviceable redesign package
- `docs/SMALL_LAUNCH_VEHICLE_REDESIGN_V1.md` for the fourth design-thinking baseline: staged aerospace cutaway structure -> printable serviceable and flow-readable redesign package
- `docs/LONG_RANGE_RECON_WING_REDESIGN_V1.md` for the fifth design-thinking baseline: long-range recon mission structure -> printable serviceable redesign package
- `docs/FIVE_SEED_DESIGN_MODEL_PIPELINE.md` for the focused five-seed data accumulation -> design model training -> model output review path
- `docs/DESIGN_MODEL_BUILDING_REALITY_AND_TREE.md` for the practical model-building layers, inheritance tree, and data structure
- `docs/DESIGN_MODEL_TUNING_ROADMAP.md` for later design-assistant tuning plans
- `data/blueprint/cubesat_redesign_package_v1.json` and `data/blueprint/cubesat_design_thinking_v1.jsonl` for the first small rule+data design model seed
- `data/blueprint/tiltrotor_redesign_package_v1.json` and `data/blueprint/tiltrotor_design_thinking_v1.jsonl` for the second small rule+data design model seed
- `data/blueprint/robot_arm_redesign_package_v1.json` and `data/blueprint/robot_arm_design_thinking_v1.jsonl` for the third small rule+data design model seed
- `data/blueprint/small_launch_vehicle_redesign_package_v1.json` and `data/blueprint/small_launch_vehicle_design_thinking_v1.jsonl` for the fourth small rule+data design model seed
- `data/blueprint/long_range_recon_wing_redesign_package_v1.json` and `data/blueprint/long_range_recon_wing_design_thinking_v1.jsonl` for the fifth small rule+data design model seed

## Not Included In This Step

- Bundled backend runtime
- npm or pip dependency installation
- downloaded model files
- proxy-style Ollama bridge endpoint
- OpenVINO model conversion
- local runtime outputs or logs
