# Judgment Schema v2 — 공학 판단 인과 스키마 (진화 루프)

기존 `thinking.jsonl`(v1: classification/rule/serviceability_check)은 보존하되,
**공학 판단의 인과 사슬**을 별도 파일 `judgment_causal.jsonl` 로 정식화한다.
이 데이터는 **package 에서 derive** 한다 (손으로 새로 쓰지 않음).

## 인과 사슬

```
objective(목적)  →  constraint(제약)  →  trade_off(이득↔비용↔가드레일)
   →  decision(판단, core 온톨로지)  →  verification(측정가능 검증)  →  evolution(진화 후크)
```

## row 구조 (`blueprint_judgment_causal_v2`)

```json
{
  "schema": "blueprint_judgment_causal_v2",
  "target": "cubesat_3u",
  "objective": {
    "metric": "assembly_serviceability_efficiency",
    "definition": "...",
    "failure_rule": "..."            // 무엇이 실패인가 (검증의 근거)
  },
  "constraint": "rail datum ribs remain visible and measurable",
  "trade_off": {
    "gain": "reduces alignment operations and corner fasteners",
    "guardrail": "rail datum ribs remain visible and measurable",
    "cost_if_violated": "<objective.failure_rule>"   // 가드레일 깨지면 목적이 실패
  },
  "decision": {
    "core": "INTEGRATE",             // classification_ontology.json 의 코어 8종 중 하나
    "rationale": "integrate rails into a single frame spine"
  },
  "verification": [
    { "check": "rail datum ribs visible and measurable", "measurable": true, "expected": "pass" }
  ],
  "evolution": {
    "leaves_for_next": "datum visibility guardrail carries into next iteration"
  }
}
```

## 출처 매핑 (package → causal row)

| causal 필드 | package 출처 |
|-------------|--------------|
| objective | `primary_metric` (name/definition/failure_rule) |
| constraint / trade_off.guardrail | `integration_decisions[].guardrail` |
| trade_off.gain | `integration_decisions[].expected_gain` |
| trade_off.cost_if_violated | `primary_metric.failure_rule` (가드레일 위반 = 목적 실패) |
| decision.core | `integration_decisions[].decision` 동사 → 온톨로지 코어 추론 |
| decision.rationale | `integration_decisions[].decision` |
| verification | guardrail 을 측정가능 check 로 |
| evolution | guardrail 승계 + 관련 `risk[].mit` |

## decision.core 추론 규칙 (동사 기반)
- `integrate ...` → `INTEGRATE`
- `keep ... separate` / `separate ...` → `DECOUPLE`
- `reduce ... to ...` → `PARTIAL_INTEGRATE`
- `do not integrate` / `reject ...` → `REJECT`
- (그 외는 derive 시 경고하고 수동 매핑 대기)

## 평가 연결 — `eval/*.jsonl` (`blueprint_eval_case_v1`)
`quality_scenarios` 를 평가 케이스로 승격. `expected` 는 `pass|fail|risk`.

```json
{ "schema": "blueprint_eval_case_v1", "target": "cubesat_3u",
  "case": "...", "expected": "fail",
  "expected_polarity": "reject",     // pass→approve, fail→reject, risk→caution
  "reason": "serviceability metric is primary" }
```

**진화 루프**: causal row 의 `trade_off.guardrail` 위반 ↔ eval 의 `fail` 이 인과로 맞물린다.
모델이 case 를 보고 polarity 를 예측 → `score_eval.py` 가 정답과 대조 → 약점 → 데이터 보강 → 재학습.
