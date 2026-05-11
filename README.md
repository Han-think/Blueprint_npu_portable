# Blueprint NPU

Portable, browser-first design system for local blueprint review, engineering domain presets, and design-to-print output documentation.

This repository is a file-only package. It can be opened locally as static HTML and does not require Python, npm, pip, a model download, or a running backend.

## Current Baseline

- Static HTML design-system pages for local browser use
- `schema_v6.json` as the canonical output contract
- Preset/domain resources under `prompts/presets/`
- First-class advanced propulsion, aero, combustion, CFD, and mechanical engineering resources
- Configuration contracts in `config/`
- Placeholder documentation for a future optional Ollama IPEX bridge

## Current Status In Plain Terms

The UI concept exists as static HTML pages, but the real app wiring is not built yet.

- Present: browser-first UI mockups/design-system pages
- Present: schema contract and preset prompts
- Present: planning docs for IPEX/Ollama and future design-model tuning
- Not present: active background server
- Not present: live model loading from the browser
- Not present: curated training/fine-tuning dataset
- Not present: real save/retrain loop

Start with `docs/START_HERE_NEXT_STEPS.md` before building the runtime.

## Open Locally

Open `index.html` directly in a browser.

The HTML pages are intended to remain useful without a server. Some controls may be visual prototypes or static placeholders until an optional local bridge is added later.

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

`config/backend.json` records the intended future local backend shape. It does not install, start, or download anything.

## Future Bridge

An optional Ollama IPEX bridge is planned for a later integration step. The intended external runtime basis is IPEX-LLM `v2.3.0-nightly` using the Ollama IPEX-LLM portable package.

For the simplest later setup, see `docs/IPEX_OLLAMA_DOWNLOADS.md`. In short:

- Windows runtime archive: `ollama-ipex-llm-2.3.0b20250725-win.zip`
- Ubuntu/Linux runtime archive: `ollama-ipex-llm-2.3.0b20250725-ubuntu.tgz`
- first model candidate: `qwen2.5:7b`
- primary acceleration target: Intel GPU/iGPU/Arc through IPEX-LLM
- NPU/OpenVINO remains a separate future evaluation

That bridge is not implemented in this file-only package. No live Ollama integration, Python backend, OpenVINO conversion, model download, or server startup is required here.

## Included Design-System Resources

- `colors_and_type.css` for visual tokens
- `assets/` for brand and SVG assets
- `preview/` for component and visual reference pages
- `ui_kits/` for browser UI kit references
- `learning/` for optional offline study-loop notes
- `docs/` for migration notes
- `docs/START_HERE_NEXT_STEPS.md` for the build order and current/missing pieces
- `docs/DESIGN_MODEL_TUNING_ROADMAP.md` for later design-assistant tuning plans

## Not Included In This Step

- Active backend runtime
- Python server implementation
- npm or pip dependency installation
- downloaded model files
- live Ollama bridge
- OpenVINO model conversion
- local runtime outputs or logs
