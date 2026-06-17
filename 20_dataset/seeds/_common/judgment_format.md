# Judgment Format — seed JSONL 공통 부모 포맷

모든 seed의 `thinking.jsonl` 한 줄(row)은 **이 공통 포맷을 상속**한다.
seed는 `target` / `metric` / 내용만 채우는 자식이고, 구조(필드)는 전부 공유한다.
이것이 "공유 reasoning layer"의 데이터화다.

## 공통 row 구조 (부모)

```json
{
  "schema": "blueprint_design_thinking_example_v1",
  "target": "<seed 고유 vehicle_id>",
  "metric": "<seed 고유 평가 지표>",
  "input":     { "existing_structure": "...", "problem": "...", "constraint": "..." },
  "reasoning": { "classification": "...", "rule": "...", "serviceability_check": "..." },
  "output":    { "proposal": "...", "reduced_steps": ["..."], "retained_access": ["..."], "verification": ["..."] }
}
```

## 상속 규칙

| 필드 | 성격 | 비고 |
|------|------|------|
| `schema` | **고정 부모값** | 항상 `blueprint_design_thinking_example_v1` |
| `target` | seed override | 5개 중 하나 (아래) |
| `metric` | seed override | seed별 1개 |
| `input.*`, `reasoning.*`, `output.*` | 구조 상속 / 값 자유 | 필드 키는 공유, 내용만 row마다 다름 |

## 5-Seed 고정 target (새 target 추가 금지 — Stop Rule)

| seed 폴더 | target | metric |
|-----------|--------|--------|
| cubesat | `cubesat_3u` | `assembly_serviceability_efficiency` |
| tiltrotor | `tiltrotor_vtol` | (seed metric) |
| robot_arm | `arm_6dof` | (seed metric) |
| small_launch_vehicle | `small_launch_vehicle` | (seed metric) |
| long_range_recon_wing | `wing_long_range` | (seed metric) |

## classification 허용 라벨 (공통 온톨로지)

판단 클래스는 `classification_ontology.json` 의 등록 라벨만 허용한다.
원본 라벨(38종)은 도메인 특화로 보존되며, **공통 코어 8종**으로 통일 매핑된다:
`INTEGRATE · PARTIAL_INTEGRATE · REJECT · FAIL · DECOUPLE · RISK · GUARDRAIL · EXPOSE`.

- 코어 정의·매핑표: `classification_ontology.md`
- `INTEGRATE/FAIL/REJECT/RISK` 는 5개 도메인 전부에 등장하는 도메인 초월 판단 골격.
- **새 라벨 도입 시 반드시 `classification_ontology.json` 에 등록** (미등록은 `validate_common.py` 가 차단).

## 검증
`20_dataset/scripts/validate_common.py` 가 5개 seed thinking.jsonl 이 이 부모 포맷을
지키는지(필드 일치 + schema 고정값 + target 일치) 일괄 확인한다.
