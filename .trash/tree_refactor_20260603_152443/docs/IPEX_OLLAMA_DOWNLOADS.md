# IPEX-LLM Ollama Download Notes

This note is for a later optional runtime bridge. The current Blueprint NPU repository remains a file-only/static browser package.

Do not include these runtime archives, downloaded models, logs, or generated runtime folders in this GitHub upload.

## Target Release

- IPEX-LLM release page: <https://github.com/ipex-llm/ipex-llm/releases/tag/v2.3.0-nightly>
- Planned runtime basis: `v2.3.0-nightly`
- Runtime style: Ollama IPEX-LLM portable package
- Primary acceleration target: Intel GPU/iGPU/Arc through IPEX-LLM
- NPU/OpenVINO: separate future evaluation, not part of this file-only package

The release notes state that the `ollama-ipex-llm` portable zip supports Ollama `v0.9.3` starting from `2.3.0b20250630`.

## What To Download Later

For Windows:

```text
ollama-ipex-llm-2.3.0b20250725-win.zip
```

For Ubuntu/Linux:

```text
ollama-ipex-llm-2.3.0b20250725-ubuntu.tgz
```

Download from the GitHub release page above, not from mirror sites.

## Suggested External Runtime Location

Keep the runtime outside this repository, for example:

```text
C:\Ollama-IPEX\
```

The repository's `config/backend.json` may point to that external location later, but it should not vendor the runtime.

## Easy Model Candidates

Start with one small-to-medium Ollama model:

```text
qwen2.5:7b
```

Other candidates to test later:

```text
gemma2:9b
llama3.1:8b
deepseek-r1:7b
```

Choose one first. Do not download all models during repository packaging.

## Future Bridge Shape

```text
Browser HTML UI
  -> optional local Blueprint bridge
  -> http://127.0.0.1:11434/api/generate
  -> Ollama IPEX-LLM portable runtime
```

This repo currently includes only the static package, configuration contracts, and planning notes.
