# Classification Ontology — 공통 판단 코어 (성장 잠금해제 1단계)

5개 seed에 난립하던 38종 classification 라벨을 **공통 코어 8종**으로 통일한다.
모델이 "물체 이름"이 아니라 **도메인을 초월한 판단 구조**를 배우게 하는 추상층.

## 설계 원칙: 비파괴적 2층
- **원본 라벨 보존** — `thinking.jsonl` row 는 바꾸지 않는다 (도메인 특화 전문성 유지, 회귀 위험 0).
- **공통 코어 부여** — `classification_ontology.json` 매핑으로 38라벨 → core 8종 + polarity.

## 코어 8종

| core | polarity | 의미 | 도메인 커버 |
|------|----------|------|-------------|
| `INTEGRATE` | approve | 통합 승인 (정비/검사 보존 하에) | **5/5** |
| `FAIL` | reject | 실패 판정 (사후: 과통합/정비성 위반) | **5/5** |
| `REJECT` | reject | 통합 거부 (사전 차단) | **5/5** |
| `RISK` | caution | 위험 식별 (datum/flow/cable/print) | **5/5** |
| `PARTIAL_INTEGRATE` | approve | 조건부/부분 통합 | 3/5 |
| `DECOUPLE` | neutral | 분리/외부화로 정비 단위 보존 | 3/5 |
| `EXPOSE` | approve | 학습/한계 노출 (교육용 mockup) | 3/5 |
| `GUARDRAIL` | neutral | 설계 기준 보존 제약 | 3/5 |

> **핵심**: `INTEGRATE / FAIL / REJECT / RISK` 4종이 **5개 도메인 전부**에 등장 →
> "통합할까/거부할까/실패인가/위험은 무엇인가"라는 판단 골격이 물체 종류와 무관하게 반복된다.
> 이것이 도메인 초월 일반화의 데이터 근거다.

## 38 → 8 매핑표

| core | 원본 라벨 |
|------|-----------|
| INTEGRATE | integrate_with_guardrail, integrate_low_risk_feature, integrate_hollow_feature, integrate_service_feature, integrate_assembly_guidance, add_assembly_path, add_service_feature |
| PARTIAL_INTEGRATE | partial_integration, reduce_but_preserve_access, fastener_reduction, reduce_fasteners |
| REJECT | do_not_integrate, reject_closed_integration, reject_hidden_integration, reject_functional_drift, reject_weaponized_drift |
| FAIL | fail_over_integration, fail_serviceability, fail_learning_goal |
| DECOUPLE | decouple_fragile_part, decouple_service_module, separate_fragile_and_service_parts, separate_service_paths, externalize_service_fasteners, externalize_service_feature |
| RISK | risk_datum_loss, risk_flow_hidden, risk_hidden_service, risk_print_deformation, risk_wire_motion, print_strategy_risk |
| GUARDRAIL | datum_guardrail, tolerance_guardrail |
| EXPOSE | expose_learning_feature, expose_mechanism_limit, printability_service_detail, print_strategy, serviceability_redesign |

(기계가독 매핑: `classification_ontology.json`)

## 보조 축 `design_axis` (선택적 2차 태그)
판단이 걸린 설계 차원: `serviceability` / `datum` / `printability` / `assembly` / `safety` / `flow` / `cable`.
향후 row 에 부여하면 "어떤 코어를 어떤 축에서 적용했는가"로 더 세밀한 일반화가 가능.

## 규칙 (Stop Rule 연계)
- 새 classification 라벨을 도입하면 **반드시 `classification_ontology.json` 에 등록**한다.
- `validate_common.py` 가 미등록 라벨을 0건으로 강제한다 (등록 안 하면 검증 실패).
- polarity 가 reject 인 코어(REJECT/FAIL)는 "하면 안 되는 것" 학습 신호 — 비율을 유지한다.
