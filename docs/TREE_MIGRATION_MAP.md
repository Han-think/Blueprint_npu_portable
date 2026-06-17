# Tree Migration Map — 상속 트리 구조 개편

생성: Phase 0 / 백업: `.trash/tree_refactor_20260603_152443/` (vendor 등 정적자원 제외, 128 파일)

3축 트리: `00_contract`(뿌리 계약) → `10_execution` / `20_dataset` / `30_model`

## ✅ 완료 상태 (2026-06-03)
- 00_contract: schema_v6.json + presets.json(내부경로 갱신) — **완료**
- 10_execution: server/ + ui/(정적자산 일체) + prompts/presets/ + backend.json — **완료**, serve.py 재배선
- 20_dataset: seeds 5개 + _common + scripts(part_tree_inherit, validate_common) + train/image_lineage — **완료**
- 30_model: learning→ + roadmap 8문서 — **완료**
- 진입/문서: README, START_HERE, INSTALL, PORTABLE, codex, IPEX, start.ps1/bat 경로 갱신 — **완료**
- 검증: 5 validator 통과 / validate_common 125 / 서버 /schema·/Minimal.html·/vendor·/validate 정상

> ⚠️ **날짜 박힌 스냅샷/감사 문서는 갱신하지 않음** (과거 평면구조 시점 기록 보존):
> `docs/PRODUCTION_STRUCTURE_SNAPSHOT_2026-05-13.md`, `docs/FILE_ONLY_MIGRATION.md`,
> `docs/README_REPLACEMENT_NOTES.md`, `docs/BLUEPRINT_IMAGE_*` (image 계보 역사 명세).

---

## ⚠️ 결정적 제약 — 정적 웹 자산은 통째로 이동

`Minimal.html` 등 HTML들은 `vendor/`, `assets/`, `colors_and_type.css`, `TopNav.jsx`를
**상대경로로 대량 참조**한다 (`vendor/react.js`, `vendor/img/presets/...`, `vendor/img/assembly_parts/...` 등 수십 곳).
HTML만 떼어 옮기면 전부 깨진다.

→ **원칙**: HTML 34개 + `vendor/` + `assets/` + `ui_kits/` + `preview/` + `colors_and_type.css`
  + `TopNav.jsx`는 **한 덩어리**로 `10_execution/ui/` 아래에 함께 이동(상호 상대경로 보존).
  `serve.py`의 정적 서빙 루트를 `10_execution/ui`로 지정하고, schema는 `00_contract`에서 읽도록 분리.

---

## 경로 의존성 (이동 시 반드시 함께 수정)

| 파일 | 현재 의존 | 이동 후 수정 |
|------|-----------|--------------|
| `server/serve.py` | `ROOT = __file__.parent.parent`; `ROOT/'schema_v6.json'`; 정적 `directory=ROOT`; `open .../Minimal.html` | repo-root 재계산(`parent.parent.parent`); schema는 `00_contract/schema_v6.json`; 정적 루트 `10_execution/ui`; `ui/Minimal.html` |
| `start.ps1` | `$servePy = root\server\serve.py`; `index.html` | `10_execution/server/serve.py`; `10_execution/ui/index.html` |
| `start.bat` | `%~dp0server\serve.py`; `:8080/Minimal.html` | `10_execution/server/serve.py`; 경로 동일(서버 루트가 ui면 `/Minimal.html` 유지) |
| `config/presets.json` | `prompts/presets/*`, `schema_v6.json` (상대) | `10_execution/prompts/presets/*`, `00_contract/schema_v6.json` |
| `learning/Modelfile.template` | `./qwen2.5-...gguf` (외부 GGUF, repo무관) | 경로 영향 없음 — 위치만 `30_model/`로 |
| `scripts/build_blueprint_sft_dataset.js` | `data/blueprint/`, **없는** `madang_learning_core_handoff_*` | 입력을 `20_dataset/seeds/*`로; handoff 의존 제거 |

---

## 파일 이동 매핑

### 00_contract/
| 기존 | 신규 |
|------|------|
| `schema_v6.json` | `00_contract/schema_v6.json` |
| `config/presets.json` | `00_contract/presets.json` |

### 10_execution/
| 기존 | 신규 |
|------|------|
| `server/serve.py`, `server/README.md` | `10_execution/server/` |
| `config/backend.json` | `10_execution/backend.json` |
| `prompts/presets/` (5 preset) | `10_execution/prompts/presets/` |
| HTML 34개 + `vendor/` `assets/` `ui_kits/` `preview/` `colors_and_type.css` `TopNav.jsx` | `10_execution/ui/` (통째) |

### 20_dataset/ (개편 핵심 — 3계보 분리)
| 기존 | 신규 |
|------|------|
| `data/blueprint/cubesat_redesign_package_v1.json` + `cubesat_design_thinking_v1.jsonl` + `scripts/validate_cubesat_redesign_v1.py` | `20_dataset/seeds/cubesat/{package.json, thinking.jsonl, validate.py}` |
| (tiltrotor / robot_arm / small_launch_vehicle / long_range_recon_wing 동일 패턴) | `20_dataset/seeds/<seed>/{package.json, thinking.jsonl, validate.py}` |
| `data/blueprint/train_*` (3 파일) | `20_dataset/train/` |
| `data/blueprint/blueprint_image_training_*` (manifest 계보) | `20_dataset/image_lineage/` |
| `scripts/build_blueprint_*.js`, `scripts/evaluate_blueprint_curation.js` (전부 image 계보로 판명) | `20_dataset/image_lineage/scripts/` |
| (신규) judgment 데이터 도구 | `20_dataset/scripts/{part_tree_inherit.py, validate_common.py}` |
| `scripts/generate_blueprint_*.js` (asset/image 생성, 계보 미정) | `scripts/` 잔류 (후속 분류) |
| (신규) JSONL 부모 포맷 명세 | `20_dataset/seeds/_common/judgment_format.md` |
| (신규) part_tree 상속 규칙 | `20_dataset/seeds/_common/part_tree_inheritance.md` |
| (신규) part_tree 상속 정규화기 | `20_dataset/scripts/part_tree_inherit.py` |

**5-seed 고정**: seeds 폴더는 위 5개로 고정. 새 target 추가 금지(Stop Rule).

### 30_model/
| 기존 | 신규 |
|------|------|
| `learning/Modelfile.template`, `learning/HOWTO.md` | `30_model/` |
| `docs/DESIGN_MODEL_*.md`, `docs/FIVE_SEED_*.md`, `docs/*_REDESIGN_V1.md` | `30_model/roadmap/` |

### 유지 (이동 안 함)
- `docs/` 잔여 스펙·감사 문서 (단, 위 roadmap 대상은 30_model로)
- `codex/`, `START_HERE_NEXT_STEPS.md`, `README.md`, `INSTALL.md`, `PORTABLE.md`, `SKILL.md`

---

## 혼동 차단: "5"가 두 축
- **seed 5** (데이터/모델): cubesat_3u, tiltrotor_vtol, arm_6dof, small_launch_vehicle, wing_long_range → `20_dataset/seeds/`
- **preset 5** (실행/프롬프트): propulsion, general_mechanical, drone_aero, electronics_enclosure, repair_fixture → `10_execution/prompts/presets/`
- 개수만 같을 뿐 별개 축. 절대 합치지 않는다.
