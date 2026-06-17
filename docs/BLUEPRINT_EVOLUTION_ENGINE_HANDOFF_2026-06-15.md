# Blueprint Evolution Engine Handoff — 2026-06-15

> **⚠ 2026-06-16 갱신됨 — 아래 "남은 GAP" 일부는 이미 해결.** 최신 상태는
> `SYSTEM_STATUS_AND_HANDOFF_2026-06-15.md`의 "2026-06-16 변경"을 정본으로 본다. 요지:
> GAP-4 placement는 **zero-rotation OBB → joint 기반 방향성 트리 배치 + 충돌해소**로 교체(blocked_pairs=0 재검증).
> GAP-1은 **구조에 실제 빔 FE 솔버**(`solve_fea.py`) 도입, CFD는 OpenFOAM 드라이버+폴백(`solve_cfd.py`).
> GAP-3 계보 view 완료(`/lineage`), `train_lora.py` 포맷 정합 수정. 생성물도 detail급 프리미티브로 렌더.
> 아래 본문은 2026-06-15 시점 기록으로 보존한다.

## 핵심 한 줄

Blueprint는 이제 “LLM이 그럴듯한 설계를 말하는 앱”이 아니라, **생성 후보를 실제 CAD 산출물로 빌드하고, 조립성/프린트성/1차 해석 근거로 심판한 뒤, 그 결과를 다음 세대와 학습 데이터에 먹이는 루프**로 이동했다.

다음 에이전트는 UI나 프롬프트만 보지 말고 항상 이 질문부터 해야 한다.

> 이 후보는 실제 산출물까지 갔다 왔는가?  
> 조립/프린트/해석 report가 후보 scorecard와 loop feedback에 붙었는가?  
> keep/reject 판단이 디스크 코퍼스에 영구화되는가?

## 오늘까지 된 것

### 1. 구조 축 — GAP-2: 파트 -> 조립 -> 조립검증

- `Minimal.html`의 assembly 후보가 curation queue에 쌓인다.
- 후보 row의 `AUDIT` 버튼이 `/audit-bundle`로 assembly bundle을 보낸다.
- `serve.py`가 bundle을 `20_dataset/seeds_generated/<seed>/<run_id>/`에 저장한다.
- 서버가 CAD 파이프라인을 자동 실행한다.
  - `build_solid.py <seed> --dir <run_dir>`
  - `export_print_parts.py <seed> --dir <run_dir>`
  - `validate_print.py <seed>_generated`
  - `export_step_assembly.py <seed> --dir <run_dir>`
  - `assembly_interference_audit.py <seed>_generated`
  - `analysis_estimate.py <seed>_generated`
- 결과 report가 curation record에 붙고, scorecard가 다시 계산된다.
- 즉, 이제 seed 고정 평가가 아니라 **후보별 CAD 검증 결과**가 후보의 운명을 바꾼다.

현재 확인된 generated 예시:

- `cubesat_generated`: placement audit `87/100 watch`, print blocked 없음, spine이 bed-fit segment로 분할됨.
- `robot_arm_generated`: placement audit `80/100 watch`, print blocked 없음.

### 2. 해석 축 — GAP-1: 1차 근사 해석이 루프에 들어옴

- `analysis_estimate.py`가 `assembly_structure.json` 기반으로 1차 근사를 만든다.
- 외부유동 seed는 aero fineness, frontal area, drag index proxy를 계산한다.
- 모든 seed는 structural slenderness/buckling risk와 thermal surface-area-per-watt proxy를 계산한다.
- `Minimal.html` scorecard에 `analysis_estimate` category가 들어간다.
- 이 값은 solver 결과가 아니라 “형상 경향 비교용”이다.

현재 해석 철학:

- tiltrotor / launch vehicle / wing: 외부유동으로 aero score 적용.
- robot arm / haptic glove: 내부형/비유동형으로 aero n/a.
- cubesat: 구조/좌굴/열 proxy 중심.
- OpenFOAM/FEA는 후속 GAP이며, 지금은 빠른 루프용 first-order signal이 목적이다.

### 3. 학습 축 — GAP-3 1단계: 데이터 영구화

- UI localStorage 100개 제한과 별개로 `/persist-curation` 라우트가 생겼다.
- keep/reject row가 `30_model/curation/curation_log.jsonl`에 누적된다.
- `30_model/curation/curation_index.json`은 total/kept/rejected/by_seed/last_ts를 요약한다.
- `/curation-stats`는 lineage depth를 계산할 준비가 되어 있다.
- 현재 corpus는 아직 실제 keep/reject 누적 대기 상태다. LoRA는 지금 할 일이 아니라 데이터가 쌓인 뒤의 일이다.

## 현재 엔진 흐름

```text
LM Studio Gemma 26B
  -> P0 plan
  -> S1 part tree
  -> S2 geometry_ops
  -> S3 verify/risk
  -> S4 print_profile
  -> assembly curation record
  -> AUDIT button
  -> /audit-bundle
  -> generated seed package
  -> CAD build / print export / STEP export
  -> print_readiness + interference_report + analysis_report
  -> live scorecard recalculation
  -> keep / reject / hold
  -> persistent curation JSONL
  -> loop feedback into next generation
```

중요한 점: 모델의 말은 임시 주장이고, **report가 붙은 후보만 학습 가치가 높다.**

## 남은 GAP

### GAP-4: CAD 회전/기구학

현재 placement는 AABB와 zero-rotation OBB 중심이다. 다음 단계는 실제 조립 기구학이다.

- `placement_rotation_deg`를 실제 transform에 반영.
- revolute/prismatic/cylindrical joint axis를 report에 넣기.
- 회전 sweep envelope와 motion collision check 추가.
- robot arm, tiltrotor, hinge/deployment 계열은 정적 간섭보다 motion envelope가 중요하다.

### GAP-3 2단계: LoRA/QLoRA

지금은 LoRA를 시작하지 않는다.

- 먼저 keep/reject가 충분히 쌓여야 한다.
- 최소 기준: seed별 good/bad가 의미 있게 분포하고, audit/analysis score가 함께 있는 row.
- 학습 대상은 “예쁜 JSON 생성”이 아니라 “P0 -> geometry -> CAD audit -> analysis -> decision” 패턴이다.

### GAP-3 lineage view

UI에 계보 view가 필요하다.

- parent candidate
- loop feedback
- score delta
- placement/analysis change
- keep/reject reason
- generated seed dir / report links

이 view가 있어야 모델이 어떻게 발전했는지 사람이 한눈에 본다.

### Audit orchestrator backlog

지금은 row별 `AUDIT` 버튼이다. 다음은 운영 편의다.

- selected candidates 일괄 audit.
- stage별 progress/log display.
- 실패 stage 재시도.
- generated output cleanup/archive policy.

### 자잘한 backlog

- XPU/IPEX naming 정리.
- qwen fallback pull/문서 정리.
- `AUDIT`와 `CAD` 버튼의 역할 라벨을 더 명확히 하기.
- `analysis_estimate.py --all` 결과를 dashboard rollup에 더 선명히 표시.

## 다음 작업 순서

1. UI 대개편 금지. 지금은 엔진 검증이 우선이다.
2. Gemma 26B로 후보를 1~2개만 생성한다.
3. 각 후보에서 `AUDIT`를 누른다.
4. `placement`, `print`, `analysis` finding이 scorecard에 붙는지 본다.
5. `watch/block`이면 그 finding을 그대로 `evolve`에 먹인다.
6. 사람이 판단해서 keep/reject를 누른다.
7. `30_model/curation`에 row가 쌓이는지 확인한다.
8. 데이터가 50~100 row 이상 쌓인 뒤 LoRA/QLoRA 계획을 다시 연다.

## 다음 에이전트 사고 규칙

- 생성 품질을 말로 판단하지 말 것.
- 후보가 CAD pipeline을 지나기 전에는 “검증된 설계”라고 부르지 말 것.
- scorecard category는 반드시 구체 report나 schema field에 연결할 것.
- `schema_v6`는 가능한 유지하고, evidence/report layer로 확장할 것.
- launch vehicle / aircraft / propulsion은 실제 제작/운용 지침이 아니라 educational mock assembly evidence에 머물 것.
- 좋은 후보란 높은 점수 후보가 아니라, **왜 좋은지/왜 나쁜지 다음 세대가 배울 수 있는 후보**다.

## 오늘의 판정

세 바퀴가 모두 돌기 시작했다.

- 구조: part -> assembly -> CAD -> placement/print audit.
- 해석: aero/structure/thermal first-order estimate.
- 학습: keep/reject persistent corpus.

이제 이 프로젝트의 중심은 “모델 선택”보다 **검증된 후보의 계보를 축적하는 것**이다.
