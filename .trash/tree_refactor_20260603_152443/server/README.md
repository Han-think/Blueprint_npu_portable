# server/ — Local Static Server + Validation API

This directory contains the small local HTTP helper for Blueprint NPU.

It serves the static HTML package and exposes schema validation for generated Blueprint JSON.

Current endpoints:

```text
GET  /              -> static files, including Minimal.html
GET  /schema        -> schema_v6.json
POST /validate      -> validate a JSON body against schema_v6.json
```

Run:

```powershell
python server/serve.py --no-browser
python server/serve.py 9090 --no-browser
```

The current browser flow in `Minimal.html` calls Ollama directly at `http://127.0.0.1:11434` and calls this server for `/validate`.

Current runtime shape:

```text
Browser HTML UI
  -> Ollama-compatible API at http://127.0.0.1:11434/api/generate
  -> local validation API at http://127.0.0.1:8080/validate
```

External runtime basis:

- portable Ollama/IPEX runtime outside this repository
- first model candidate in the original plan: `qwen2.5:7b`
- acceleration target: Intel GPU/iGPU/Arc through IPEX-LLM

NPU/OpenVINO support is not implemented here and should be evaluated separately later. A proxy-style bridge endpoint such as `/api/generate` is also not implemented; the browser currently talks to Ollama directly.

Keep the HTML package usable without this server. Direct browser open should remain valid for static reading/demo mode, though schema validation requires this helper.
