# Design Model Building Reality And Data Tree

이 문서는 Blueprint 설계모델을 만들기 위한 실제 구조를 정리한다.

핵심 결론은 단순하다.

```text
처음부터 LLM을 만드는 것은 현재 목표가 아니다.
기존 오픈 모델 위에 Blueprint 설계 판단 능력을 상속시키는 것이 첫 현실적 목표다.
```

하지만 이 방향은 작지 않다. 5개 seed에서 시작해서 개별 설계 판단 모델을 만들고, 나중에는 여러 개별 모델이 서로 평가하고 보완하는 집단지성 구조로 갈 수 있다.

## LLM을 만든다는 것의 층위

모델 만들기는 한 가지가 아니다. 최소 네 층으로 나눠야 한다.

```text
Layer 0. Foundation LLM pretraining
Layer 1. Instruction tuning
Layer 2. Domain adaptation / LoRA / SFT
Layer 3. Retrieval + tools + evaluation loop
```

### Layer 0 — Foundation LLM

처음부터 LLM을 만드는 단계다.

필요한 것:

- 거대한 일반 텍스트/코드 데이터
- tokenizer 설계
- 수십억~수천억 파라미터 모델 구조
- 대규모 GPU/가속기 클러스터
- 긴 사전학습 시간
- 대규모 평가와 안전성 정렬

이 단계는 개인 프로젝트의 첫 목표가 아니다.

OpenAI 같은 대형 연구소는 대략 다음 흐름을 사용한다.

```text
large-scale pretraining
-> instruction tuning
-> preference / feedback alignment
-> safety evaluation
-> tool and product integration
-> continuous evaluation and improvement
```

세부 데이터, 학습 레시피, 모델 구조는 공개되지 않은 부분이 많다. Blueprint에서는 이 전체를 재현하려 하지 않는다.

### Layer 1 — Instruction Model

이미 사전학습된 모델이 사용자의 지시를 따르도록 만든 단계다.

예:

- Qwen instruct 계열
- Llama instruct 계열
- Mistral instruct 계열

Blueprint의 첫 기반은 이런 instruct 모델을 가져와 쓰는 것이다.

### Layer 2 — Blueprint Domain Model

이 문서에서 말하는 "설계모델"의 첫 현실적 의미다.

기존 instruct 모델에 Blueprint 데이터를 학습시켜 다음 능력을 강화한다.

- 기존 구조 읽기
- 문제점 분류
- 통합 가능 / 통합 금지 판단
- service access 보존 판단
- datum, CG, cable, flow, axis, hinge 같은 설계 기준 보존
- risk와 verification 출력
- `schema_v6` 설계패키지로 확장 가능한 사고 출력

이 단계는 LoRA/SFT로 접근할 수 있다.

### Layer 3 — Model System

튜닝된 모델 하나만으로 끝내지 않는다.

실제 사용 구조는 다음과 같다.

```text
local docs / seed packages / schema
-> retrieval
-> model judgment
-> validation script
-> human review
-> accepted output becomes new data
```

즉 모델은 혼자 완성품을 만드는 존재가 아니라, 검증 가능한 설계 판단을 계속 생산하고 축적하는 시스템의 일부다.

## Blueprint의 상속 구조

Blueprint 설계모델은 다음 tree를 상속한다.

```text
Foundation Instruct Model
└── Blueprint Design Judgment Model
    ├── Shared Schema Layer
    │   ├── schema_v6.json
    │   ├── part_tree
    │   ├── geometry_ops
    │   ├── verify
    │   ├── risk
    │   └── print_profile
    ├── Shared Reasoning Layer
    │   ├── existing_structure
    │   ├── problem
    │   ├── constraint
    │   ├── classification
    │   ├── redesign proposal
    │   └── verification
    └── Five Seed Domain Layer
        ├── CubeSat: static frame / panel / maintenance access
        ├── Tiltrotor: moving interface / wiring / nacelle service
        ├── Robot Arm: axis / joint cartridge / cable route
        ├── Small Launch Vehicle: staged cutaway / flow readability
        └── Long-Range Recon Wing: sensor / payload / CG / spar datum
```

상속의 의미:

- 모든 seed는 같은 판단 포맷을 공유한다.
- 각 seed는 다른 공학적 사고 축을 제공한다.
- 모델은 "물체 이름"보다 "판단 구조"를 배운다.
- 새 seed를 나중에 추가해도 기존 판단 구조를 재사용할 수 있다.

## 데이터 Tree

현재 데이터는 다음 구조로 본다.

```text
data/
└── blueprint/
    ├── *_redesign_package_v1.json
    │   └── full design package examples
    └── *_design_thinking_v1.jsonl
        └── compact judgment examples
```

첫 학습에 더 중요한 것은 JSONL이다.

패키지 JSON은 큰 정답 예시다.
JSONL은 모델이 반복해서 배울 판단 단위다.

권장 확장 구조:

```text
data/
├── blueprint/
│   ├── existing five seed package/data files
│   └── source of truth
├── train/
│   ├── blueprint_judgment_sft_train.jsonl
│   └── blueprint_package_sft_train.jsonl
└── eval/
    ├── blueprint_judgment_eval.jsonl
    ├── blueprint_risk_eval.jsonl
    └── blueprint_schema_eval.jsonl
```

처음에는 `train/`과 `eval/` 파일을 자동 생성해도 된다. 원본 seed 파일은 source of truth로 둔다.

## JSONL 학습 포맷

현재 seed row는 이미 좋은 시작점이다.

```json
{
  "schema": "blueprint_design_thinking_example_v1",
  "target": "wing_long_range",
  "metric": "assembly_serviceability_mission_readability",
  "input": {
    "existing_structure": "...",
    "problem": "...",
    "constraint": "..."
  },
  "reasoning": {
    "classification": "integrate_with_guardrail",
    "rule": "...",
    "serviceability_check": "..."
  },
  "output": {
    "proposal": "...",
    "reduced_steps": ["..."],
    "retained_access": ["..."],
    "verification": ["..."]
  }
}
```

LoRA/SFT용으로 변환할 때는 instruct 형태로 바꾼다.

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a Blueprint design judgment assistant. Preserve service access and schema-aware verification."
    },
    {
      "role": "user",
      "content": "Target: wing_long_range\nMetric: assembly_serviceability_mission_readability\nExisting structure: ...\nProblem: ...\nConstraint: ..."
    },
    {
      "role": "assistant",
      "content": "{ \"classification\": \"...\", \"rule\": \"...\", \"proposal\": \"...\", \"retained_access\": [...], \"verification\": [...] }"
    }
  ]
}
```

## 학습 단계

### Step 1 — 데이터 정리

목표:

```text
5개 seed JSONL을 검증하고 하나의 후보 데이터셋으로 합친다.
```

해야 할 일:

- 각 JSONL row가 같은 필드를 갖는지 확인
- classification 목록을 정리
- 성공/실패/리스크 비율을 맞춤
- safety-boundary rejection 예제를 유지
- train/eval을 분리

초기 크기:

```text
현재: 125 rows
1차 목표: 500 rows
2차 목표: 1,000-2,000 rows
```

125개는 방향 seed다. 모델 특성이 보이려면 최소 수백 개가 필요하다.

### Step 2 — RAG 먼저

학습 전에 RAG/prompt로 먼저 실험한다.

```text
schema_v6.json
five seed docs
five package JSON
five JSONL examples
-> prompt context
-> model output
-> validation
```

이 단계에서 좋은 출력과 나쁜 출력을 모아야 한다.

### Step 3 — Judgment SFT / LoRA

첫 LoRA 목표는 full package generation이 아니다.

첫 목표:

```text
input: existing_structure + problem + constraint
output: classification + rule + proposal + verification
```

이게 안정되면 다음으로 간다.

### Step 4 — Package Section SFT

두 번째 목표:

```text
input: existing BOM + redesign goal
output: part_tree / verify / risk / print_profile 일부
```

모델이 전체 JSON을 한 번에 잘 만들 거라고 기대하지 않는다.
부분 섹션을 잘 만들게 한 뒤 조립한다.

### Step 5 — Output Evaluation

모델 출력은 반드시 검사한다.

검사 항목:

- classification이 허용 목록인지
- constraint를 지켰는지
- service access를 보존했는지
- risk가 실제 문제를 잡는지
- verification이 proposal과 연결되는지
- `schema_v6`로 옮길 수 있는지
- unsafe / out-of-scope 내용을 만들지 않는지

## 개별모델과 집단지성 구조

사용자의 방향성은 다음 구조와 잘 맞는다.

```text
Individual Design Models
├── Static Structure Model
├── Moving Interface Model
├── Kinematic Chain Model
├── Flow / Cutaway Readability Model
└── Mission Layout Model
```

각 모델은 한 분야의 판단을 잘하게 만들 수 있다.

그 다음 구조:

```text
model A proposes
model B critiques serviceability
model C checks schema
model D checks risk
human accepts / rejects
accepted output becomes new data
```

이것이 작은 모델들의 집단지성 구조다.

중요한 점:

- 처음부터 하나의 거대 모델을 만들 필요는 없다.
- 작고 명확한 판단 모델 여러 개가 더 현실적이다.
- 각 모델은 검증 가능한 출력 포맷을 가져야 한다.
- 모델끼리 평가하려면 공통 schema와 공통 classification이 필요하다.

## Blueprint의 첫 모델 정의

첫 모델 이름은 다음처럼 잡을 수 있다.

```text
Blueprint-Judge-0.1
```

역할:

```text
설계 구조를 읽고 통합/분리/실패/리스크 판단을 출력하는 작은 설계 판단 모델
```

입력:

```text
target
metric
existing_structure
problem
constraint
optional package context
```

출력:

```text
classification
rule
serviceability_check
proposal
reduced_steps
retained_access
verification
risk
```

성공 기준:

- 5개 seed held-out eval에서 안정적으로 분류한다.
- service access를 막는 제안을 실패로 판정한다.
- `schema_v6` 설계패키지 섹션으로 옮길 수 있는 출력을 만든다.
- 위험하거나 실제 작동/무장/인증 제작으로 가는 요청을 교육용 mockup으로 되돌린다.

## 지금 당장 필요한 다음 데이터

새 seed가 아니라 기존 5개 seed의 깊이다.

우선순위:

1. 각 seed를 25개에서 100개로 확장
2. classification label 목록 통일
3. train/eval split 생성
4. RAG prompt baseline 생성
5. LoRA/SFT 변환 스크립트 작성
6. 모델 출력 검증 스크립트 작성

## Stop Rule

다음 조건 전에는 foundation LLM 제작이나 대형 모델 학습으로 가지 않는다.

- 5개 seed가 각각 최소 100 examples 이상
- held-out eval 존재
- RAG baseline 결과 기록
- LoRA 후보 데이터셋 생성
- 모델 출력 검증 기준 존재

이 순서를 지켜야 모델 만들기가 "느낌"이 아니라 반복 가능한 공학 프로세스가 된다.
