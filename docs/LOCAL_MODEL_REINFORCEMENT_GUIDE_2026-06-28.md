# Local Model Reinforcement Guide - 2026-06-28

Use stronger local models as engineering reviewers and candidate generators.
The goal is not to bypass project boundaries; it is to extract more structure,
better reverse analysis, and clearer solver-ready metadata.

## Recommended Role For A Large Local Model

- Generate richer part decomposition and assembly interfaces.
- Fill `operating_principle`, `multiphysics_paths`, and `solver_readiness`.
- Run reverse-analysis tasks: `fluid`, `electrical_signal`,
  `solver_readiness`, `structural`, `thermal`, `fmea`.
- Compare candidate designs and identify missing verification gaps.
- Produce reviewable engineering study data, not certified or unsafe operation
  instructions.

## LM Studio / OpenAI-Compatible Endpoint

Set the model in LM Studio, enable the local server, then run:

```powershell
$env:BP_LM_URL="http://127.0.0.1:1234/v1"
$env:BP_LM_MODEL="Qwen3.6-40B-Claude-4.6-Opus-Deckard-Heretic-Uncensored-Thinking-NEO-CODE-Di-IMatrix-MAX-GGUF"
$env:BP_WORKERS="1"
python -B generate_batch.py --seeds centrifugal_pump,battery_pack_module,liquid_rocket_engine_academic --per-seed 1
```

For local GGUF models, keep workers low unless the server clearly supports
parallel batching. Use `BP_WORKERS=1` first, then try `2` only if VRAM/RAM and
server throughput are stable.

## Reverse Analysis After Smoke Generation

After there are fresh `keep` candidates:

```powershell
$env:BP_LM_URL="http://127.0.0.1:1234/v1"
$env:BP_LM_MODEL="Qwen3.6-40B-Claude-4.6-Opus-Deckard-Heretic-Uncensored-Thinking-NEO-CODE-Di-IMatrix-MAX-GGUF"
$env:BP_WORKERS="1"
python -B generate_reverse.py --tasks fluid,electrical_signal,solver_readiness,structural,thermal,fmea --max 30
```

## Quality Gate

Accept a local-model output only when it includes:

- `cad_brief.operating_principle`
- `cad_brief.failure_modes`
- `cad_brief.inspection_points`
- `verify.multiphysics_paths`
- `verify.solver_readiness`
- traceable `part_tree` children and coordinate-bearing `geometry_ops`
- clear missing-inputs and promotion/blocking decision

Reject or hold outputs that:

- are just impressive prose without geometry evidence
- omit fluid/thermal/electrical/signal paths
- invent certification or guaranteed performance
- provide hazardous operating procedures or build-ready recipes for high-risk systems

## Practical Pattern

1. Use the large local model for generation and reverse critique.
2. Use stricter validators and scorecards to reject vague outputs.
3. Run CAD/FoS/export locally on candidates that pass text-level gates.
4. Feed strong reverse-analysis rows into LoRA/SFT later.
