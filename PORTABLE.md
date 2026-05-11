# Portable Package

Blueprint NPU is currently packaged as a portable, browser-first design system.

## What This Is

- Static HTML pages for local browser review
- `schema_v6.json` as the canonical design-to-print output contract
- First-class engineering preset/domain resources
- Local design tokens, assets, preview pages, and UI kit references
- Documentation for a future optional Ollama IPEX bridge

## Quick Start

1. Copy this folder anywhere.
2. Open `index.html` in a browser.
3. Review the design-system pages and preset resources locally.

No install. No admin rights. No dependency setup. No model download.

## File Layout

```text
.
├── index.html
├── Dashboard.html
├── *.html
├── TopNav.jsx
├── colors_and_type.css
├── schema_v6.json
├── config/
├── prompts/presets/
├── docs/
├── learning/
├── preview/
├── ui_kits/
├── vendor/
├── assets/
├── server/
└── codex/
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

That bridge is not implemented here. `server/README.md` is documentation only.

The intended external runtime basis is IPEX-LLM `v2.3.0-nightly` with the Ollama IPEX-LLM portable archive. See `docs/IPEX_OLLAMA_DOWNLOADS.md` for the exact download notes and simple model candidates.

## Learning Notes

`learning/` contains optional study-loop notes. Any Ollama or model workflow described there is optional and outside this file-only package step.
