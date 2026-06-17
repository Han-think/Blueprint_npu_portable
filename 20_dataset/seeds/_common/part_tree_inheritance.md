# Part Tree Inheritance — part_tree 노드 속성 상속 규칙

`schema_v6` 의 `part_tree` 는 자기참조 재귀 트리다. 노드 속성을 **부모→자식 상속**으로
관리해 데이터 중복을 없애고 설계 의도를 명확히 한다.

## 트리 3층 (5 seed 공통 패턴)

```
L0 루트   : 차량 전체 mockup        id = <vehicle>-redesign-v1
 └ L1 모듈 : 서비스/조립 경계 단위   id = new-001 ..        (4~6개)
    └ L2 피처: 출력 가능한 세부 형상  id = f-<기능>          (leaf)
```

L1 모듈 = "removable / serviceable / replaceable / slide-in" 단위.
즉 **part_tree 부모-자식 경계 = 조립·분해 경계 = 출력 단위 경계** 로 3중 정렬된다.

## 상속 대상 속성

| 속성 | 상속 |
|------|------|
| `material` | ✅ 자식이 비어 있으면 부모값 상속 |
| `process` | ✅ 자식이 비어 있으면 부모값 상속 |
| `id`, `name`, `qty`, `children` | ❌ 상속 안 함 (노드 고유) |

## 규칙

1. **상속**: 자식이 `material`/`process` 를 생략하면 부모의 유효값을 물려받는다.
2. **override**: 자식이 다른 값을 적으면 그 값이 우선 (예: 투명창 `clear PETG`, 패드 `TPU`).
3. **중복 명시 금지(권장)**: 자식이 부모와 **똑같은 값**을 다시 적으면 경고. 상속으로 생략해 단순화한다.
4. **부모 material 의 의미**: 부모는 "자식들 소재의 요약/기본값" 역할. override 한 자식만 예외.

## effective(유효) 트리

저장된 트리는 생략형(상속 의존)일 수 있다. 소비(검증/출력/슬라이싱) 시에는
`part_tree_inherit.py` 로 빈 속성을 채운 **effective 트리**를 사용한다.

```bash
# 5 seed 중복 명시 점검
python 20_dataset/scripts/part_tree_inherit.py

# 단일 파일의 effective 트리 출력
python 20_dataset/scripts/part_tree_inherit.py 20_dataset/seeds/cubesat/package.json --json
```

## 현재 데이터 상태 (참고)

기존 5 seed 는 자식이 부모 `PETG/FDM` 을 그대로 반복 명시하고 있어 중복이 많다
(cubesat 22건, tiltrotor 25건 등). 향후 데이터 정리 시 상속 생략형으로 단순화하고,
override(`clear PETG`, `TPU`)만 남기면 트리가 깔끔해진다.
