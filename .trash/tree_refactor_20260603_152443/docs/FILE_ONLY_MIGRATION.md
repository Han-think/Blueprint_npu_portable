# Blueprint NPU — File-Only Migration Pack

This pack is intentionally **file-only**.

It does not install packages, create a virtual environment, download models, start Ollama, run Python, modify the registry, or touch the host system.

## Intended use

Use this pack as a set of files/instructions to merge into the current `Blueprint NPU Design System` package or the GitHub repository later, from a proper development machine.

## Current source of truth

- `schema_v6.json` remains the canonical output contract.
- The uploaded portable HTML design-system package is the current product baseline.
- Existing propulsion/aero material is a **first-class preset**, not a deprecated example.
- Ollama IPEX integration is a future bridge layer, not a dependency for opening the HTML files.

## Recommended repository direction

```text
Blueprint_npu/
  index.html
  Minimal.html
  Dashboard.html
  ...
  schema_v6.json
  config/
    presets.json
    backend.json
  prompts/
    presets/
      propulsion/
      general_mechanical/
      drone_aero/
      electronics_enclosure/
      repair_fixture/
  server/
    README.md
  docs/
    FILE_ONLY_MIGRATION.md
  codex/
    CODEX_FILE_ONLY_PROMPT.md
```

## Do not do in this step

- Do not run `pip install`.
- Do not create `.venv`.
- Do not run `ollama pull`.
- Do not start `ollama serve`.
- Do not convert models.
- Do not delete the propulsion/aero design resources.
- Do not rewrite `schema_v6.json` unless a schema version bump is explicitly planned.

## Later live bridge step

When working from the real desktop/workstation, add a local bridge server that exposes:

```text
/health
/api/models
/api/generate
/api/session/save
/api/session/load
```

The bridge should call the portable Ollama IPEX endpoint at `http://127.0.0.1:11434/api/generate`.
