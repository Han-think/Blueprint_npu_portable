# Portable Package

Blueprint NPU is currently packaged as a portable, browser-first design system.

## What This Is

- Static HTML pages for local browser review
- `00_contract/schema_v6.json` as the canonical design-to-print output contract
- First-class engineering preset/domain resources
- Local design tokens, assets, preview pages, and UI kit references
- Documentation for a future optional Ollama IPEX bridge

## Quick Start

1. Copy this folder anywhere.
2. Open `10_execution/ui/index.html` in a browser (or run `start.ps1` / `start.bat`).
3. Review the design-system pages and preset resources locally.

No install. No admin rights. No dependency setup. No model download.

## File Layout

```text
.
├── 00_contract/      # schema_v6.json, presets.json
├── 10_execution/     # server/ · ui/(HTML+vendor+assets+css+jsx) · prompts/presets/ · backend.json
├── 20_dataset/       # seeds/(5-seed) · scripts/ · train/ eval/ image_lineage/
├── 30_model/         # Modelfile.template · HOWTO.md · roadmap/
├── docs/             # specs + TREE_MIGRATION_MAP.md
├── codex/
├── start.ps1  start.bat
└── README.md
```

## Static Mode

The current package should remain useful when opened directly from disk. Pages may include interface concepts for generation, review, or local runtime connection, but this release does not include an active backend.

## Optional Future Runtime

The planned future bridge is:

```text
Browser HTML UI
  -> local bridge server
  -> optional local Ollama IPEX-compatible runtime
```

That bridge is not implemented here. `10_execution/server/README.md` is documentation only.

The intended external runtime basis is IPEX-LLM `v2.3.0-nightly` with the Ollama IPEX-LLM portable archive. See `docs/IPEX_OLLAMA_DOWNLOADS.md` for the exact download notes and simple model candidates.

## Learning Notes

`30_model/` contains optional study-loop notes (Modelfile.template, HOWTO.md). Any Ollama or model workflow described there is optional and outside this file-only package step.
