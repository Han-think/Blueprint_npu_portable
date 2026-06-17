# Blueprint XPU — 시스템 현황 · 구조 설명 · 남은 작업 핸드오프
_작성 2026-06-15 · **갱신 2026-06-16(6-step 갭 로드맵 반영)** · 대상: 이어서 작업할 사람/에이전트_

> **2026-06-16 업데이트 요약 (먼저 읽기):** "엔진 출력 ≠ 데모 품질" 갭을 토대부터 메우는 6-step을 완료.
> ① 생성물 빌드가 detail급 프리미티브 + `args.at` 좌표로 렌더(프롬프트 키↔빌더 키 별칭 일치). ②
> 실제 굽힘 FoS 사이징 + `structural_sizing` criteria. ③ 조립 배치 1D 타일링 → **joint 기반 방향성
> 트리 + 간이 충돌해소**(blocked_pairs=0은 간섭 audit으로 재검증). ④ **실제 빔 FE 솔버**(numpy,
> `solve_fea.py`) + OpenFOAM 드라이버/폴백(`solve_cfd.py`), 리포트에 solver/proxy provenance 표기.
> ⑤ `train_lora.py` 포맷 불일치 수정(레코드→messages 유도). ⑥ 계보 view(`/lineage`, `lineage.html`).
> 상세는 §3 끝 "2026-06-16 변경" + §4 갱신된 GAP 상태 참조.

---

## 0. 이 문서를 읽는 법 (코덱스/에이전트에게)

이 프로젝트는 "예쁜 CAD 그림 생성기"가 아니라 **공학적 판단을 하며 세대를 거쳐 진화하는 설계 모델**을 만드는 것이다.
코드를 고치기 전에 **반드시 아래 §2 "핵심 사고방식"을 먼저 이해하라.** 개별 함수만 보고 고치면 구조가 무너진다.

핵심 원칙 4가지 (이걸 어기는 변경은 거부):
1. **가르친 것 = 재는 것.** 모델에게 지시한 기준(`criteria/*.json`)은 반드시 scorecard로 측정돼야 한다. 프롬프트에만 넣고 채점 안 하면, 모델이 무시해도 점수가 안 깎여 영원히 안 배운다.
2. **원인을 고치고 임계값을 낮추지 마라.** audit가 BLOCK을 내면 audit 기준을 완화하는 게 아니라 설계/데이터를 고친다. (audit threshold 상수는 성역)
3. **점진적 침습(coarse→fine).** 전체를 한 번에 생성하지 않는다. 골격 → 서브시스템 → 통합 패스로 쪼개 부하를 일정하게. 한 번에 한 가지만 조정.
4. **정직하게.** 솔버 아닌 근사는 "근사"라고 명시. mock은 "mock"이라고. 안전경계(교육용/비무장/비행인증 아님)는 유지.

---

## 1. 전체 아키텍처 (한 장)

```
[지식층]  criteria/*.json (판단기준) + connection_types + assembly_integration
          + subsystem_taxonomy (서브시스템 분해) + design_pass_protocol (패스)
              │  build_context_pack.py 가 seed별 packs/ 로 분배
              ▼
[생성층]  Minimal.html : 시드 선택 → 점진 침습 생성
          PASS-0 골격 → PASS-1 서브시스템별 (P0계획→S1 part_tree→S2 geometry→S3 verify→S4 print)
          각 호출에 해당 서브시스템 마이크로팩만 주입 (LM Studio :1234, 폴백 Ollama :11434)
              ▼
[채점층]  scorecard = criteria 커버리지(단일 진실원천) + P0사고 + 좌표/형상
          + subsystem_completeness + interface_consistency + budget_closure
          + placement_interference(실제 조립) + analysis_estimate(공력/구조/열)
              ▼
[판정/축적]  keep/reject → localStorage 큐 + **디스크 영구화** 30_model/curation/*.jsonl
              ▼
[진화 루프]  evolve = 낮은 카테고리의 loop_feedback 모아 다음 세대 프롬프트로 주입
              ▼
[CAD/해석]  serve.py /export-bundle·/audit-bundle → build_solid → 분할/조립 →
            STEP(파트+어셈블리, CATIA호환) + 간섭 audit + 해석근사
              ▼
[학습(예정)]  쌓인 corpus → LoRA(7B 학생모델) → 더 나은 모델 → 루프 재투입
```

핵심 파일:
- 지식: `20_dataset/criteria/*.json`, `20_dataset/criteria/subsystem_taxonomy.json`, `design_pass_protocol.json`, `connection_types.json`
- 분배: `20_dataset/tools/build_context_pack.py`, `check_taxonomy_match.py`, 결과 `20_dataset/packs/<seed>/`
- 생성·채점·UI: `10_execution/ui/Minimal.html` (단일 거대 파일, text/babel React)
- 서버: `10_execution/server/serve.py` (정적서빙 + LM프록시 + /packs /export-bundle /audit-bundle /persist-curation /curation-stats)
- CAD: `10_execution/cad/{build_solid, export_print_parts, validate_print, export_step_assembly, assembly_interference_audit, analysis_estimate}.py`
- 학습데이터: `30_model/curation/curation_log.jsonl` (+ index)

---

## 2. 핵심 사고방식 (코덱스가 꼭 가져야 할 구조적 사고)

### 2.1 파트 → 어셈블리 → 합체는 데이터 토폴로지 문제다
- 각 파트는 **자기 로컬 좌표계**에서 생성된다(원점 중심 아님 — 주의!).
- 어셈블리는 `assembly.json`의 **joints**(partA→partB, mate, clearance, containment)로 위상이 정의된다.
- 배치(`assembled_layout`)는 데이텀(최다 partB)에서 BFS 트리를 만든 뒤 **각 자식을 부모의 서로 다른 면(FACE_DIRS)에 인접 배치**한다(2026-06-16: 1D 타일링에서 방향성 트리로 교체 → 실제 분기 조립 형태). 분기는 충돌0을 구조적으로 보장하지 못하므로 **간이 AABB 충돌해소 루프**로 겹친 파트를 데이텀 반대방향으로 밀어 분리하고, **assembly_interference_audit으로 반드시 재검증**한다(임계 완화 금지). 회전 mate는 배치 방향에 수직축으로 전개각 부여. 다중부모 mate는 `unsatisfied_mates` 잔차로 정직 보고.
- **audit는 placement_translation을 AABB 중심으로 가정**한다 → export 시 실제 배치 솔리드의 중심/크기를 기록해야 정합. (로컬 중심 보정 필수)

### 2.2 "실제로 만들 수 있고 조립되는가"가 채점의 척추다
- 베드(250mm) 초과 파트는 **세그먼트 분할 + 정렬키 커플러**로 진짜 프린트 가능하게 만든다(임계값 완화 금지).
- 얇은 판(<3mm)은 boss/engrave/드릴이 슬리버→non-manifold를 만든다 → 가드로 솔리드 유지.
- 데이터 정합(유령 파트 joint, self-mate) 같은 건 audit가 잡아준다 — audit를 신뢰하고 원인을 고쳐라.

### 2.3 가르친 기준 = 재는 기준 (단일 진실원천)
- `criteria/*.json`의 각 criterion은 `signals`(키워드/필드/형상) + `loop_feedback`을 가진다.
- `criteriaCoverageAudit`(Minimal.html)가 생성물에서 signal 커버리지를 weight 가중 채점한다. **`weight` 필드는 죽은 데이터가 아니다 — 채점에 쓰인다.**
- 고가치 criterion(connection_type/datum/load_path)은 키워드가 아닌 **구조적 오버라이드**로 실측한다.
- 새 criteria를 추가하면 `build_context_pack --all` 한 번으로 가르침+채점에 자동 반영된다.

### 2.4 진화는 두 층이다
- **세션 내 진화**(있음): scorecard findings → evolve → 다음 세대 프롬프트. 모델은 안 변하고 "더 좋은 지시"를 받는다.
- **모델 진화**(예정): keep/reject corpus → LoRA → 모델 자체가 똑똑해짐. 이게 "세대 진화"의 진짜 끝.
- 그래서 **corpus 영구화가 생명줄**이다(아래 §3).

---

## 3. 오늘(및 최근)까지 한 것 ✅

### 지식·분배층
- `criteria/`: connection_types(연결 22종 + DOF/공차/실패모드), assembly_integration(연결타입명명·조립순서·데이텀체인·하중경로폐합·구조발전·인터페이스최소화), electronics_routing 신설. seed별 sub-criteria 보강.
- `subsystem_taxonomy.json`: 6 seed × 필수 서브시스템(분과/evidence_features/criteria_refs). **BOM 59개 전부 매칭 0 misses** (`check_taxonomy_match.py`로 검증).
- `design_pass_protocol.json`: PASS-0/1/2/3 점진 침습 명문화. `build_context_pack.py`가 마이크로팩 + skeleton 생성(연결 어휘 주입 포함).

### 생성·채점층 (Minimal.html)
- criteria 단일 진실원천 채점(`criteriaCoverageAudit`) — 파트/번들 scorecard에 `engineering_criteria_coverage`.
- `interface_consistency`(짝/타입 정합), `budget_closure`(질량 산수), `subsystem_completeness`(taxonomy 충족).
- 단계별/전체 **타이머**, 서버·모델 선택(드롭다운), `Reasoning: low`(gpt-oss 폭주 방지), AbortController STOP, 토큰 8000.

### CAD/조립 (10_execution/cad)
- `build_solid`: 데이텀 BFS 1D `assembled_layout`(충돌0) + 얇은판/패스너 watertight 가드.
- `export_print_parts`: 베드 초과 **세그먼트 분할 + 커플러** + 명시적-base 횡 clearance.
- `export_step_assembly`: STEP 파트+어셈블리(CATIA호환) + CFD geometry(fused/fluid_domain) + 실제배치 bbox 기록.
- `assembly_interference_audit`: AABB 간섭/조립성. **6 seed 전부 BLOCK→WATCH, blocked_pairs=0** (임계값 무변경, 원인 수리).
- `analysis_estimate`(신규): 공력(fineness/drag)·구조(좌굴)·열(cm²/W) 1차 근사.

### 서버·루프 폐환 (serve.py)
- `/export-bundle`(다중루트 합성 패키지) + **`/audit-bundle`**(생성물 → 5단계 CAD → 간섭+해석 리포트). → 생성 설계가 **자기 조립성·해석을 실측**하고 scorecard에 반영.
- **`/persist-curation`**(keep/reject 디스크 영구 누적, 중복스킵, 계보필드) + `/curation-stats`(generations).
- 런처: LM Studio 우선·Ollama 옵션(`-WithOllama`)·브라우저 1개·XPU(런처만).

### 3대 진화 바퀴 상태 (2026-06-16 갱신)
- **구조** ✅ 파트→조립→조립검증(GAP-2) + 생성물 detail급 렌더 + joint 방향성 트리 배치(GAP-4 핵심)
- **모델학습** 🟡 corpus 영구화 + `train_lora.py` 포맷 정합 완료(코드 준비) — corpus 0이라 실학습 대기
- **해석** ✅ **실제 빔 FE 솔버**(구조) + 1차 근사(공력/열) + CFD 드라이버(OpenFOAM 설치 대기)

### 2026-06-16 변경 (6-step 갭 로드맵)
1. **엔진 지오메트리 충실도** [build_solid.py]: `make_primitive`(box/cyl/tube/cone/sphere/hex) 공통화 — detail_parts와 생성 geometry_ops가 같은 어휘 사용. `op_at`로 모델 `args.at` 좌표 실제 반영. `argf`/`op_box_dims`로 프롬프트 키(d_mm/h_mm/x_mm)와 빌더 키 별칭 흡수(**가르친 것=재는 것을 형상 레벨에서 폐합**). 파트당 ops<4면 `geometry_resolution.json`에 LOW-RES 신호.
2. **공학적 치수 도출** [analysis_estimate.py + criteria/structural_sizing.json]: 부재를 외팔보로 보고 σ=M/S, FoS=허용/σ 계산(재료 허용·FDM knockdown·하중계수). 주 부재는 시스템 질량 반력. `structural_sizing.json`을 criteria_index에 등록(applies_to:all) → 모든 팩 주입.
3. **조립 정합** [build_solid.py assembled_layout, export_step_assembly.py]: §2.1 참조. blocked_pairs=0 전 시드 유지(간섭 audit 재검증).
4. **실제 솔버** [solve_fea.py·solve_cfd.py 신규]: Euler–Bernoulli 빔 FE(numpy, K·u=F)가 sizing의 권위 FoS. closed-form 검증 일치. CFD는 OpenFOAM 탐지+graceful 폴백. 리포트에 `provenance: solver:* | proxy:*`.
5. **corpus+LoRA** [30_model/train_lora.py]: serve.py 레코드엔 `messages`가 없어 `record_to_messages`로 payload에서 (system,user,assistant) 유도. `--inspect`/gate-check 안전.
6. **계보 view** [serve.py /curation-records·/lineage, ui/lineage.html 신규]: parent→child 트리 + 세대 점수 추세.

---

## 4. 남은 작업 + 어떻게 (우선순위)

### ▶ GAP-3 2단계 · LoRA 학습 (트리거: corpus ≥ trial 300 / full 1000)
- **지금도 corpus 0개** — 실제 keep/reject가 쌓여야 시작. `/curation-stats`의 `total`로 확인.
- 코드 준비됨: `30_model/train_lora.py` (2026-06-16 포맷 정합 수정). 레코드엔 `messages`가 없어 `record_to_messages`가 payload에서 (system,user,assistant)를 유도한다. keep=정답 / reject=회피. **QLoRA, 7B 학생(qwen2.5:7b-instruct)**, gpt-oss-20B는 교사 유지. `python train_lora.py --inspect`로 첫 행/예시 확인, `--train`은 게이트 통과 시.
- 주의: seed 균등, keep:reject ≈ 7:3. 어댑터 → GGUF 변환 → Ollama/LM Studio 로드.

### ✅ GAP-3 계보 view (2026-06-16 완료)
- `serve.py` `/curation-records`(compact 레코드)·`/lineage`, `10_execution/ui/lineage.html` — parent→child 트리 + 세대별 점수 추세 + by_seed. corpus 0이면 안내 빈 상태.

### ◑ GAP-4 · CAD/CATIA 정합 심화 (2026-06-16 갱신)
1. **방향성 트리 배치** ✅(2026-06-16, 1D 타일링 대체): `assembled_layout`이 BFS 트리에서 자식을 부모의 서로 다른 면(FACE_DIRS)에 인접 배치 → 실제 분기 조립 형태(별·체인·분기 모두). 회전 mate는 배치 방향 수직축 전개각. **분기는 충돌0 비보장 → 간이 AABB 충돌해소 루프 + assembly_interference_audit 재검증**으로 blocked_pairs=0 전 시드 유지(robot_arm 24→68/100). fineness가 실제 형상값으로 수렴.
2. **다중 mate 정합** ◑ **부분/정직**: BFS 1차 부모만 인접 만족, 나머지 secondary mate는 `assembly_structure.json`의 `layout.unsatisfied_mates` 잔차로 보고. 완전 동시 정합은 여전히 실제 constraint solver 필요(후속, 큼).
3. **기구학 DOF/모션** ◑: `analysis_estimate.kinematic_estimate` — 회전 mate swept_radius proxy(정직 표기). 실제 회전 포락 AABB 격상은 작은 후속.

### ◑ GAP-1 실제 솔버 (2026-06-16 부분 완료)
- **구조 ✅ 실제 솔버 도입**: `solve_fea.py` — Euler–Bernoulli 빔 FE(numpy, K·u=F). `analysis_estimate`가 임계 부재를 풀어 sizing의 권위 FoS/응력/변위로 사용(closed-form 검증 일치). provenance `solver:euler_bernoulli_beam_fe_numpy`.
- **CFD ⏳ 드라이버 준비, 솔버 설치 대기**: `solve_cfd.py`가 OpenFOAM(native/WSL) 탐지 → 있으면 fluid_domain.step로 RANS 구동 지점, 없으면 aero proxy를 `proxy:fineness_ratio (CFD solver_unavailable)`로 정직 표기. (현재 환경 미설치)
- **3D 연속체 FEA ⏳**: CalculiX/sfepy 부재로 미도입 — 빔 FE로 갈음. 설치 시 `solve_fea`에 추가.
- 전제였던 GAP-4(조립 정합)는 2026-06-16 완료 → fineness가 실제 형상값으로 수렴(1D 일렬 부풀림 해소).

### ▶ 자잘한 백로그
- **NPU→XPU 리네이밍** ✅: UI 브랜드 문자열 전부 XPU(스키마 키 `blueprint_npu_*` 18개는 데이터 계약이라 보존). TopNav 포함.
- **`/audit-bundle` 가속** ✅: `run_full_pipeline.py` 단일 오케스트레이터(build123d import 1회) → serve.py가 5-subprocess 대신 1회 호출 → **~30~90s → ~5s**.
- **`ollama pull qwen2.5:7b-instruct`** ⏳ **사용자 액션 남음**: GAP-3 학습 베이스 겸 폴백 1순위 복원(현재 폴백 qwen2.5-coder:14b). 대용량 다운로드라 사용자가 직접.
- 참고문서 탭: 숨김 완료(BP_DOCS 보존, `BP_SHOW_DOCS=true`로 복원).

---

## 5. 실행/검증 빠른 참조

```
# 기동
start.bat   (= start.ps1: LM Studio 우선, -WithOllama 로 Ollama)

# CAD 파이프라인 (seed) — 한 방에: run_full_pipeline.py <seed> [--dir <pkg>]
cd 10_execution/cad
python run_full_pipeline.py <seed>            # build→print→step→interference→analysis 6단계
# 개별 실행도 가능:
python build_solid.py <seed>                  # geometry_resolution.json(LOW-RES) 생성
python export_step_assembly.py --all [--cfd]  # assembly_structure.json(layout.unsatisfied_mates 포함)
python assembly_interference_audit.py --all   # 배치 변경 후 blocked_pairs=0 재검증 필수
python analysis_estimate.py --all             # sizing.fea(빔 FE) + aero.solver(CFD provenance)

# 학습/계보
python ../../30_model/train_lora.py --inspect # corpus 첫 행/예시 (gate-check 기본)
# 계보 view: 서버 기동 후 /lineage (GET /curation-records 소비)

# 생성물(번들) — 보통 UI '→ AUDIT' 버튼이 호출
POST /audit-bundle      # 합성패키지 → 위 파이프라인 → 간섭+해석 리포트
POST /persist-curation  # keep/reject 디스크 누적
GET  /curation-stats    # total/kept/rejected/generations

# 검증 습관
- 신규 JSON: python -m json.tool
- Minimal.html 수정 후: vendor/babel.js 로 transform (구문 게이트)
- criteria/taxonomy 수정 후: check_taxonomy_match.py (0 misses)
- audit 임계상수(NEAR/MATE_GAP/EXPLODED/DEFAULT_BED) 변경 금지
- 저작권 reference 책이 criteria source_refs에 새는지 grep (public만 인용)
```

---

## 6. 코덱스에게 한 마디
개별 함수를 "동작하게" 만드는 것과 **구조가 옳은 방향으로 진화하게** 만드는 것은 다르다.
- 증상(BLOCK, 502, non-manifold)을 보면 **근본 원인**을 찾아라(예: 502는 컨텍스트가 아니라 프록시 타임아웃 + reasoning 폭주였다).
- "가르친 것=재는 것", "원인 수리 vs 임계 완화", "한 번에 한 가지" — 이 세 가지를 매 변경마다 자문하라.
- 정직하게: 안 되는 건 안 된다고, 근사는 근사라고 리포트에 박아라. 그게 이 시스템의 신뢰 기반이다.
