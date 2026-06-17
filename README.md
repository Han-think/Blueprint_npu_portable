# Blueprint NPU

Portable, browser-first design system for local blueprint review, engineering domain presets, and design-to-print output documentation.

This repository is a file-first package. Most pages can be opened locally as static HTML and do not require Python, npm, pip, a model download, or a running backend. The optional `Minimal.html` validation flow uses the bundled Python helper in `10_execution/server/serve.py`.

## Current Baseline

- Static HTML design-system pages for local browser use
- `00_contract/schema_v6.json` as the canonical output contract
- Preset/domain resources under `10_execution/prompts/presets/`
- First-class advanced propulsion, aero, combustion, CFD, and mechanical engineering resources
- Configuration contracts in `00_contract/` and `10_execution/`
- Local static server and schema validation helper under `10_execution/server/`
- Future notes for an optional proxy-style Ollama IPEX bridge

## Current Status In Plain Terms

The UI concept exists as static HTML pages. `Minimal.html` has first-pass local wiring for direct Ollama calls and schema validation, but the packaged runtime/proxy bridge is not built yet.

- Present: browser-first UI mockups/design-system pages
- Present: schema contract and preset prompts
- Present: planning docs for IPEX/Ollama and future design-model tuning
- Present: optional local static server with `/schema` and `/validate`
- Present: browser-side Ollama tag/model discovery and generation calls in `Minimal.html`
- Not present: curated training/fine-tuning dataset
- Not present: real save/retrain loop

Start with `docs/START_HERE_NEXT_STEPS.md` before building the runtime.

## Open Locally

Open `10_execution/ui/index.html` directly in a browser, or run `start.ps1` / `start.bat`.

The HTML pages are intended to remain useful without a server for static reading/demo mode. `10_execution/ui/Minimal.html` can also be served through `10_execution/server/serve.py` so schema validation works through `POST /validate`.

## Canonical Contract

`00_contract/schema_v6.json` is the source of truth for generated Blueprint NPU output packages. Do not rename it, remove fields, or replace it with preset-specific contracts.

The contract currently covers:

- project brief and constraints
- part tree / BOM structure
- geometry operation intent
- CAD brief
- verification and risk records
- print profile and slicer job structure

## Preset Domains

Preset resources are first-class domain material, not disposable demos. The file-only package includes, where available:

- `10_execution/prompts/presets/propulsion`
- `10_execution/prompts/presets/general_mechanical`
- `10_execution/prompts/presets/drone_aero`
- `10_execution/prompts/presets/electronics_enclosure`
- `10_execution/prompts/presets/repair_fixture`

The propulsion preset includes propulsion, aero, combustion, CFD, and advanced engineering framing as a primary selectable domain.

## Project Layout (상속 트리 3축)

폴더만 봐도 `계약 → 실행 / 데이터 / 모델` 흐름이 보이도록 재편됨.

```text
.
├── 00_contract/            # 뿌리 계약 (모든 축이 상속/소비)
│   ├── schema_v6.json      #   출력 계약 (source of truth)
│   └── presets.json        #   preset → schema 섹션 매핑
├── 10_execution/           # 실행 축
│   ├── server/serve.py     #   정적 서버 + /schema /validate
│   ├── ui/                 #   HTML 화면 + vendor/assets/css/jsx (정적 자산 일체)
│   ├── prompts/presets/    #   preset 5종 (도메인)
│   └── backend.json
├── 20_dataset/             # 데이터셋·학습 축
│   ├── seeds/              #   5-seed 고정 (_common 부모 + 5 seed 폴더)
│   ├── scripts/            #   part_tree_inherit.py, validate_common.py
│   ├── train/  eval/  image_lineage/
│   └── README.md
├── 30_model/               # 모델 생성 축
│   ├── Modelfile.template  HOWTO.md
│   └── roadmap/            #   설계모델/시드 파이프라인 문서
├── docs/                   # 스펙·감사 문서 + TREE_MIGRATION_MAP.md
├── codex/  start.ps1  start.bat  README.md
```

> 진입: `start.ps1` / `start.bat` 실행 (서버가 `10_execution/ui` 를 서빙).
> 서버 없이 보려면 `10_execution/ui/index.html` 을 직접 연다.

## Configuration Contracts

`00_contract/presets.json` describes available preset/domain resources.

`10_execution/backend.json` records the intended local runtime shape. It does not install, start, or download anything.

## Future Bridge

An optional proxy-style Ollama IPEX bridge may be added later. The current `Minimal.html` flow calls the Ollama-compatible API directly at `127.0.0.1:11434` and uses `10_execution/server/serve.py` for static serving and schema validation. The intended external runtime basis is IPEX-LLM `v2.3.0-nightly` using the Ollama IPEX-LLM portable package.

For the simplest later setup, see `docs/IPEX_OLLAMA_DOWNLOADS.md`. In short:

- Windows runtime archive: `ollama-ipex-llm-2.3.0b20250725-win.zip`
- Ubuntu/Linux runtime archive: `ollama-ipex-llm-2.3.0b20250725-ubuntu.tgz`
- first model candidate: `qwen3:8b`
- fallback candidates: `qwen2.5:7b`, `qwen3:4b`
- primary acceleration target: Intel GPU/iGPU/Arc through IPEX-LLM
- NPU/OpenVINO remains a separate future evaluation

No OpenVINO conversion, model download, or bundled runtime is required here.

## Included Design-System Resources

- `10_execution/ui/colors_and_type.css` for visual tokens
- `10_execution/ui/assets/` for brand and SVG assets
- `10_execution/ui/preview/` for component and visual reference pages
- `10_execution/ui/ui_kits/` for browser UI kit references
- `30_model/` for optional offline study-loop notes
- `docs/` for migration notes
- `docs/START_HERE_NEXT_STEPS.md` for the build order and current/missing pieces
- `30_model/roadmap/CUBESAT_REDESIGN_V1.md` for the first design-thinking baseline: existing product structure -> printable serviceable redesign package
- `30_model/roadmap/TILTROTOR_REDESIGN_V1.md` for the second design-thinking baseline: moving-interface drone structure -> printable serviceable redesign package
- `30_model/roadmap/ROBOT_ARM_REDESIGN_V1.md` for the third design-thinking baseline: kinematic-chain robot structure -> printable serviceable redesign package
- `30_model/roadmap/SMALL_LAUNCH_VEHICLE_REDESIGN_V1.md` for the fourth design-thinking baseline: staged aerospace cutaway structure -> printable serviceable and flow-readable redesign package
- `30_model/roadmap/LONG_RANGE_RECON_WING_REDESIGN_V1.md` for the fifth design-thinking baseline: long-range recon mission structure -> printable serviceable redesign package
- `30_model/roadmap/FIVE_SEED_DESIGN_MODEL_PIPELINE.md` for the focused five-seed data accumulation -> design model training -> model output review path
- `30_model/roadmap/DESIGN_MODEL_BUILDING_REALITY_AND_TREE.md` for the practical model-building layers, inheritance tree, and data structure
- `30_model/roadmap/DESIGN_MODEL_TUNING_ROADMAP.md` for later design-assistant tuning plans
- `20_dataset/seeds/cubesat/package.json` and `20_dataset/seeds/cubesat/thinking.jsonl` for the first small rule+data design model seed
- `20_dataset/seeds/tiltrotor/package.json` and `20_dataset/seeds/tiltrotor/thinking.jsonl` for the second small rule+data design model seed
- `20_dataset/seeds/robot_arm/package.json` and `20_dataset/seeds/robot_arm/thinking.jsonl` for the third small rule+data design model seed
- `20_dataset/seeds/small_launch_vehicle/package.json` and `20_dataset/seeds/small_launch_vehicle/thinking.jsonl` for the fourth small rule+data design model seed
- `20_dataset/seeds/long_range_recon_wing/package.json` and `20_dataset/seeds/long_range_recon_wing/thinking.jsonl` for the fifth small rule+data design model seed

## Not Included In This Step

- Bundled backend runtime
- npm or pip dependency installation
- downloaded model files
- proxy-style Ollama bridge endpoint
- OpenVINO model conversion
- local runtime outputs or logs
