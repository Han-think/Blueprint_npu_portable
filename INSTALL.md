# Install — Blueprint NPU File-Only Package

There is nothing to install for the current portable package.

This repository is a static, browser-first Blueprint NPU Design System. Open `index.html` directly in a browser to inspect the UI pages, design-system resources, and schema contract.

## Current Mode

- File-only/static portable package
- No Python backend required
- No npm or pip install required
- No model download required
- No service startup required
- No Ollama or OpenVINO runtime required

## Recommended Local Use

1. Place the folder anywhere on your machine.
2. Open `index.html` in a browser.
3. Review `schema_v6.json` as the canonical output contract.
4. Review domain presets under `prompts/presets/`.

## Preset Resources

The included preset folders are first-class engineering domains:

- `propulsion`
- `general_mechanical`
- `drone_aero`
- `electronics_enclosure`
- `repair_fixture`

Propulsion, aero, combustion, CFD, and advanced engineering material remains part of the primary product direction.

## Configuration Files

`config/presets.json` and `config/backend.json` are configuration contracts only. They do not start a backend, download models, or run local services.

## Later Optional Runtime Work

A future integration may add:

- a local bridge server
- a browser-to-local-runtime API
- an optional Ollama IPEX-compatible runtime

Those pieces are not part of this file-only package. See `server/README.md` for the bridge concept and `docs/IPEX_OLLAMA_DOWNLOADS.md` for the planned download notes.

The easiest later runtime target is:

- IPEX-LLM `v2.3.0-nightly`
- Windows: `ollama-ipex-llm-2.3.0b20250725-win.zip`
- Ubuntu/Linux: `ollama-ipex-llm-2.3.0b20250725-ubuntu.tgz`
- first model to try: `qwen2.5:7b`

Keep those downloads outside this repository.

## Where To Start Next

Before implementing anything, read:

```text
docs/START_HERE_NEXT_STEPS.md
```

The recommended order is:

```text
upload static repo
-> run external Ollama IPEX portable
-> add one minimal local bridge
-> make prompts schema-aware
-> add local retrieval
-> create evaluation data
-> consider fine-tuning only later
```

## Troubleshooting

If pages do not render correctly, check that the folder was copied with its subfolders intact:

- `assets/`
- `vendor/`
- `preview/`
- `ui_kits/`
- `prompts/`
- `config/`

No installer, package manager, model manager, or server command is needed for this release folder.
