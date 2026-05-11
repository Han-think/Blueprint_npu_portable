# server/ — Placeholder Only

This directory is reserved for a future local bridge server.

No server code is included in this file-only pack because the current task is to prepare structure and configuration only, without installing or running anything.

Future intended bridge:

```text
Browser HTML UI
  -> local bridge server, e.g. http://127.0.0.1:7860/api/generate
  -> portable Ollama IPEX, e.g. http://127.0.0.1:11434/api/generate
```

Planned external runtime basis:

- IPEX-LLM `v2.3.0-nightly`
- Windows archive: `ollama-ipex-llm-2.3.0b20250725-win.zip`
- Ubuntu/Linux archive: `ollama-ipex-llm-2.3.0b20250725-ubuntu.tgz`
- first model candidate: `qwen2.5:7b`
- acceleration target: Intel GPU/iGPU/Arc through IPEX-LLM

NPU/OpenVINO support is not implemented here and should be evaluated separately later.

Keep the HTML package usable without this server. Direct browser open should remain valid for static reading/demo mode.
