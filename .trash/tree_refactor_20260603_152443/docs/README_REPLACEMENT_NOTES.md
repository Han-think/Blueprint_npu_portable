# README Replacement Notes — Portable Baseline

Use this text to update the repository README when moving to the uploaded portable design-system baseline.

## Project identity

Blueprint NPU is now a portable, browser-first design-system package for local blueprint review and design-to-print documentation.

Current baseline:
- Static HTML design-system pages
- `schema_v6.json` output contract
- First-class domain presets, including Propulsion / Combustion / Aero
- Offline-friendly learning loop documentation for Ollama IPEX

Not part of this file-only step:
- No dependency installation
- No model download
- No Python backend
- No live Ollama bridge
- No OpenVINO conversion

## Runtime modes

1. Static portable mode: open `index.html` directly.
2. Future live mode: local bridge server connects the UI to portable Ollama IPEX.

## Canonical contract

`schema_v6.json` is the canonical output contract for future generated packages.
