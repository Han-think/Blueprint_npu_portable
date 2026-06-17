# 20_dataset — 데이터셋 / 학습 축

상속 트리 3축(`00_contract` → `10_execution` / **`20_dataset`** / `30_model`) 중 데이터 축.
계약(`schema_v6.json`) 포맷을 상속하고, 모델 학습의 원천이 된다.

## 구조

```
20_dataset/
├── seeds/                      ← source of truth (5-seed 고정)
│   ├── _common/                ← 공유 부모 포맷 (상속의 뿌리)
│   │   ├── judgment_format.md          JSONL row 공통 포맷
│   │   └── part_tree_inheritance.md    part_tree 속성 상속 규칙
│   ├── cubesat/                {package.json, thinking.jsonl, validate.py}
│   ├── tiltrotor/              {...}
│   ├── robot_arm/              {...}
│   ├── small_launch_vehicle/   {...}
│   └── long_range_recon_wing/  {...}
├── train/                      ← SFT 학습 산출물 (image 계보 기존본)
├── eval/                       ← held-out 평가셋 (향후)
├── image_lineage/             ← 별개 계보(이미지 매칭/문서) — 격리, 현재 비활성
└── scripts/                    ← judgment 데이터 도구
    ├── part_tree_inherit.py    part_tree 상속 정규화기 + 중복 경고
    └── validate_common.py      5 seed 공통 포맷 일괄 검증
```

## 상속 2종

1. **seed JSONL 상속** — 모든 `thinking.jsonl` row 가 `_common/judgment_format.md` 부모 포맷을
   공유. seed 는 `target`/`metric`/내용만 채운다.
2. **part_tree 노드 상속** — 자식이 부모 `material`/`process` 를 상속, 다를 때만 override.
   `_common/part_tree_inheritance.md` 규칙, `scripts/part_tree_inherit.py` 로 강제.

## 5-Seed 고정 (Stop Rule)

| seed | target |
|------|--------|
| cubesat | cubesat_3u |
| tiltrotor | tiltrotor_vtol |
| robot_arm | arm_6dof |
| small_launch_vehicle | small_launch_vehicle |
| long_range_recon_wing | wing_long_range |

첫 사이클 동안 새 seed 추가 금지. (preset 5개와 혼동 주의 — 그건 실행 축 `10_execution/prompts/presets/`)

## 검증 명령

```bash
# seed별 package/dataset 무결성 (5개)
python 20_dataset/seeds/<seed>/validate.py

# 공통 부모 포맷 일괄
python 20_dataset/scripts/validate_common.py

# part_tree 상속 중복 점검 / effective 트리
python 20_dataset/scripts/part_tree_inherit.py
python 20_dataset/scripts/part_tree_inherit.py 20_dataset/seeds/cubesat/package.json --json
```

## 성장 잠금해제 진행
- ✅ **1단계 라벨 온톨로지 통일** — 38종 → 공통 코어 8종 (`_common/classification_ontology.{md,json}`).
  `INTEGRATE/FAIL/REJECT/RISK` 가 5/5 도메인 커버 = 도메인 초월 판단 골격 확보.
  `validate_common.py` 가 미등록 라벨 0건 강제 + 코어 분포 리포트.
- ✅ **2단계 통합 진화 루프 (5 seed 전체 반영)** — 공학 판단을 인과 사슬로 정식화.
  - `_common/judgment_schema_v2.md` — objective→constraint→trade_off→decision→verification→evolution
  - `scripts/derive_judgment.py` — package 에서 인과 row + eval 케이스 derive (5 seed 경고 0)
  - `seeds/<seed>/judgment_causal.jsonl` × 5 (총 **24 rows**), `eval/<seed>_eval.jsonl` × 5 (총 **15 cases**)
  - `scripts/score_eval.py` — 채점기. 5 seed self-score 전부 100%, 모델 예측 자리는 인터페이스로 개방
  - 진화 의미: trade_off.guardrail 위반 ↔ eval 의 fail 이 인과로 연결 → "왜 실패인가"가 측정 가능
  - core 분포: INTEGRATE/DECOUPLE/PARTIAL_INTEGRATE/GUARDRAIL (도메인별 판단 다양성 확보)
  - 다음: 모델(ollama) 연결 → [판단→채점→보강→재학습] 세대 루프 / 규모 25→100

- ✅ **3단계 깊이 확장** — 각 seed thinking 25→**40** (총 **200 rows**, 수동 생성, Stop Rule 부합).
  코어 5/5 도메인 커버 4종→**7종**(DECOUPLE/GUARDRAIL/PARTIAL_INTEGRATE 전 도메인 진입), 반례 44% 유지.
  SFT train 184/eval 40 재생성. validate.py 행 상한 30→110.

- ✅ **4단계 part_spec(구체 도안)** — 파트당 흩어진 정보(part_tree·geometry_ops·assembly·cad_brief·print_profile)를
  1 레코드로 통합. `derive_part_spec.py` → `seeds/<seed>/part_spec.jsonl` (5 seed **24 파트**, envelope+features+interfaces).
  mate face/출력방향 휴리스틱 보강. `build_sft.py` 가 part_spec→instruct(구체 도안 출력) 학습셋 생성(train20/eval4).
  "상상의 그림 → 구체 도안": new-001 = 96×96×330 PETG, new-002와 M2×8 clr0.25 slot(+X) 체결.

- ✅ **5단계 preference pairs(트레이드오프)** — 공학 사고 ⑤ "비교/대안 선택" 학습.
  `derive_preference.py` → `train/blueprint_preference_dpo.jsonl` (**169 쌍**, 손작업 0).
  approve→과분리(naive) / reject·caution→과통합(naive) 을 rejected 로 → 모델이 "과통합도 과분리도 아닌
  올바른 균형점"을 학습 (DPO). 학습셋 종합: judgment SFT 184 + partspec SFT 20 + preference DPO 169.

- ✅ **진화의 척추 — 마스터 파이프라인 + 무결성 검증**
  - `scripts/check_integrity.py` — 교차 일관성(part_spec↔geometry_ops, core↔온톨로지, interfaces↔assembly,
    classification↔온톨로지) + **stale 탐지**. PASS/FAIL.
  - `scripts/rebuild_all.py` — 소스→전체 산출물 한 방 재생성 + 검증 (`--cad`로 STL/도면 포함).
  - 효과: thinking 확장으로 발생했던 **stale 5건 → 0 해소**. 소스 변경 시 rebuild 한 번으로 전체 일관.
  - 설계(견고)·진화(안전한 변화)·발전(확장)의 공통 토대.

## 공학적 사고 사이클 커버리지
①요구△ ②판단✅(thinking200/judgment24) ③구현✅(part_spec24) ④검증✅(eval59)
⑤비교✅(preference169) ⑥반복⬜(assembly_report 신호만 — closed-loop 미구현)

## 알려진 정리 과제 (향후)
- part_tree 중복 명시 다수(cubesat 22, tiltrotor 25 …) → 상속 생략형으로 단순화 여지
- seed당 25 → 100+ 규모 확장 (반례/위험 비율 유지)
- 검증가능 rule(측정 술어) + 모델출력 자동채점 루프 → self-improve
- train/eval split 생성, judgment SFT 변환 스크립트 (미존재)
