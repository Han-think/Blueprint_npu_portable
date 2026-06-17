# Codex Task — File-Only Blueprint NPU Migration

You are working in a local clone of `Han-think/Blueprint_npu`.

Goal: migrate toward the uploaded portable `Blueprint NPU Design System` package without installing or running anything.

Constraints:
- File operations only.
- Do not run package installs.
- Do not create virtual environments.
- Do not start Ollama.
- Do not download models.
- Do not remove propulsion/aero resources.
- Treat `schema_v6.json` as the canonical output contract.
- Preserve old Python/OpenVINO implementation under `_legacy/python_openvino_app/` if it still exists.
- Place portable HTML design-system files at repository root.
- Add `config/presets.json` and `config/backend.json` from this patch pack.
- Add `docs/FILE_ONLY_MIGRATION.md` and `server/README.md`.
- Keep the project browser-first and local/portable.

Expected outcome:
- Repo root opens via `index.html` without install.
- Preset config makes `propulsion` a first-class selectable preset.
- Backend config documents Ollama IPEX intent but does not execute it.
- README/PORTABLE docs should clearly say this step is static/file-only and live Ollama bridge is a later phase.

Do not implement the live Python bridge yet.
