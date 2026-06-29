# Generation And Reverse Engineering Status - 2026-06-28

## Current Judgment

The seed and prompt foundation is upgraded, but new operability-aware generation
has not yet been proven by a fresh smoke batch. Existing CAD outputs were
created before the new `operability_profile`, `multiphysics_paths`, and
`solver_readiness` requirements, so they do not contain those fields.

## Generation Status

- Seeds configured: 16
- BOM parts: 145
- Pack JSON files with `operability_profile`: 121 / 121
- Prompt injection: active through `generate_batch.py` `micro_pack_clause`
- Existing CAD analysis reports checked: 12
- Existing reports with `solver_readiness`: 0
- Existing reports with `multiphysics_paths`: 0
- Existing reports with `operating_principle`: 0

Conclusion: the next proof step is a small fresh generation smoke test using
2-3 seeds, then CAD/export/audit on those outputs.

## Reverse Engineering Status

Existing `reverse_log.jsonl` rows: 1713

Current historical task counts:

- structural: 231
- thermal: 273
- dfa: 263
- fmea: 171
- cost: 270
- weight: 241
- tolerance: 264
- fluid: 0
- electrical_signal: 0
- solver_readiness: 0

Existing reverse data covers the original 6 seeds:

- cubesat: 493
- haptic_glove: 242
- long_range_recon_wing: 249
- robot_arm: 246
- small_launch_vehicle: 219
- tiltrotor: 264

The expansion seeds do not yet have reverse-analysis rows because they need
fresh generated keep candidates first.

## Upgrade Applied

`generate_reverse.py` now includes:

- `fluid` reverse task for flow path, pressure boundary, and CFD topology review.
- `electrical_signal` reverse task for power, signal, harness, EMI, and control-boundary review.
- `solver_readiness` reverse task for FEA, CFD/OpenFOAM, thermal, electrical/signal, and assembly readiness.
- Seed-level `operability_profile` injection from `20_dataset/packs/<seed>/skeleton.json`.

## Required Next Run

1. Run a small generation smoke batch for representative seeds:
   `centrifugal_pump`, `battery_pack_module`, `liquid_rocket_engine_academic`.
2. Confirm generated blueprints include:
   `cad_brief.operating_principle`, `verify.multiphysics_paths`, and
   `verify.solver_readiness`.
3. Run CAD/export/audit only on passing candidates.
4. Run reverse tasks:
   `fluid,electrical_signal,solver_readiness,structural,thermal,fmea`.
5. Promote only reviewed rows into training.

## Realism Boundary

Use `docs/REALISM_BOUNDARY_MATRIX_2026-06-28.md` as the seed-level boundary for
"as real as possible" generation. The intent is to push real subsystem behavior,
assembly, physics paths, and solver readiness while explicitly blocking unsafe
or uncertified operational instructions.
