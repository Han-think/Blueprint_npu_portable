# Learning loop — optional Ollama IPEX notes

This folder is optional study-loop documentation. The current Blueprint NPU package is file-only/static and does not require Ollama, model downloads, Python, pip, npm, or a running service.

## Why Ollama IPEX-LLM
- Same Ollama API & Modelfile syntax as upstream
- Runs on Intel iGPU (Iris Xe) or Arc GPU via SYCL — no NVIDIA needed
- 100% local: nothing leaves your machine

## Model sizes that fit
| RAM | Sweet spot | Stretch |
|---|---|---|
| 8 GB | 3B Q4 (~2 GB) | 7B Q4 (tight) |
| 16 GB | **7B Q4_K_M (~4.5 GB)** | 9B Q4 |
| 32 GB | 14B Q4 | 32B Q4 (slow) |

## Optional online setup

Only use this later if you are intentionally setting up a separate local Ollama-compatible runtime. It is not required for the portable design-system package.

```
ollama pull qwen2.5:7b           # Korean+English, recommended
# or
ollama pull llama3.1:8b          # English reasoning
ollama pull gemma2:9b            # middle ground
```

## Optional offline setup (USB transfer)

### Method A — copy model folder
On the online PC, find Ollama's models folder (usually `./ollama-models/` next to portable exe, or `~/.ollama/models`).
Copy that whole folder via USB to the same location on the offline PC.

### Method B — GGUF + Modelfile
1. On online PC, download GGUF directly from HuggingFace, e.g.:
   - `huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF` → `qwen2.5-7b-instruct-q4_k_m.gguf`
2. Copy GGUF + `Modelfile.template` to offline PC
3. Edit Modelfile.template, replace path, then run:
   ```
   ollama create qwen-local -f Modelfile.template
   ```

## Daily learning cycle
1. Open one HTML page (e.g., FMEA.html)
2. Copy the visible content (text + tables) into clipboard
3. Paste into Ollama prompt with this template:

```
[CONTEXT: contents of FMEA.html below]
<paste>

[TASK]
1. Explain the top 3 failure modes in plain terms
2. Cross-reference any RPN > 100 with related pages (Loads, Test, Lineage)
3. What's a question I should ask my mentor next?
```

4. Write the answer + your own follow-up into `notes/FMEA-<date>.md`

Repeat for each page. ~21 pages × 30 min = 1 week of focused study.

## Later design-assistant tuning

For the later step where the model becomes more useful for engineering design review, keep the work schema-aware and preset-aware:

- use `schema_v6.json` as the output target
- load the relevant folder from `prompts/presets/`
- start with prompt/retrieval behavior before fine-tuning
- keep advanced propulsion, aero, combustion, and CFD at conceptual design-review level
- avoid unsafe step-by-step manufacturing or operational instructions

See `docs/DESIGN_MODEL_TUNING_ROADMAP.md`.
