"""
validate_common.py — 5 seed thinking.jsonl 의 공통 부모 포맷 검증
================================================================

seeds/_common/judgment_format.md 의 부모 포맷을 모든 seed 가 상속·준수하는지 확인한다.
- schema 고정값
- target 이 seed 별 기대값과 일치 (단일 target)
- input/reasoning/output 필수 필드 존재
- classification 라벨 수집 (공통 목록 점검용)
- 전체 row 수 리포트
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

SEEDS_DIR = Path(__file__).resolve().parents[1] / "seeds"
ONTOLOGY_FILE = SEEDS_DIR / "_common" / "classification_ontology.json"
FIXED_SCHEMA = "blueprint_design_thinking_example_v1"

# 5-seed 고정 target (Stop Rule)
SEED_TARGET = {
    "cubesat": "cubesat_3u",
    "tiltrotor": "tiltrotor_vtol",
    "robot_arm": "arm_6dof",
    "small_launch_vehicle": "small_launch_vehicle",
    "long_range_recon_wing": "wing_long_range",
    "haptic_glove": "haptic_glove_pair",
}

REQUIRED = {
    "input": ("existing_structure", "problem", "constraint"),
    "reasoning": ("classification", "rule", "serviceability_check"),
    "output": ("proposal", "reduced_steps", "retained_access", "verification"),
}


def check_seed(seed: str, target: str) -> tuple[int, list[str], set[str]]:
    path = SEEDS_DIR / seed / "thinking.jsonl"
    errors: list[str] = []
    classes: set[str] = set()
    rows = 0
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        rows += 1
        row = json.loads(line)
        if row.get("schema") != FIXED_SCHEMA:
            errors.append(f"{seed} L{i}: schema != {FIXED_SCHEMA}")
        if row.get("target") != target:
            errors.append(f"{seed} L{i}: target={row.get('target')} != {target}")
        for sect, keys in REQUIRED.items():
            block = row.get(sect, {})
            for k in keys:
                if k not in block:
                    errors.append(f"{seed} L{i}: {sect}.{k} 누락")
        cls = row.get("reasoning", {}).get("classification")
        if cls:
            classes.add(cls)
    return rows, errors, classes


def check_ontology(used_labels: set[str]) -> tuple[list[str], dict]:
    """사용된 모든 라벨이 온톨로지에 등록됐는지 + 라벨→core 매핑 반환."""
    errors: list[str] = []
    if not ONTOLOGY_FILE.exists():
        return [f"온톨로지 파일 없음: {ONTOLOGY_FILE}"], {}
    onto = json.loads(ONTOLOGY_FILE.read_text(encoding="utf-8"))
    label_map = onto.get("labels", {})
    for lab in sorted(used_labels):
        if lab not in label_map:
            errors.append(f"미등록 라벨(온톨로지에 없음): {lab}")
    return errors, label_map


def main() -> int:
    total_rows = 0
    all_errors: list[str] = []
    all_classes: set[str] = set()
    # seed별 core 커버리지 추적
    core_seeds: dict[str, set[str]] = {}
    rows_by_seed_class: list[tuple[str, str]] = []  # (seed, label)
    print("공통 부모 포맷 검증 (5 seed)")
    for seed, target in SEED_TARGET.items():
        rows, errors, classes = check_seed(seed, target)
        total_rows += rows
        all_errors += errors
        all_classes |= classes
        for c in classes:
            rows_by_seed_class.append((seed, c))
        status = "OK" if not errors else f"{len(errors)} 오류"
        print(f"  [{seed}] rows={rows} target={target} -> {status}")
    print(f"\n총 rows: {total_rows}")
    print(f"원본 classification 라벨: {len(all_classes)}종")

    # 온톨로지 검증 + core 분포
    onto_errors, label_map = check_ontology(all_classes)
    all_errors += onto_errors
    if label_map:
        import collections
        core_count = collections.Counter()
        for seed, lab in rows_by_seed_class:
            core = label_map.get(lab, {}).get("core", "UNMAPPED")
            core_count[core] += 1
            core_seeds.setdefault(core, set()).add(seed)
        print(f"\n공통 코어 분포 (라벨→core 통일, 미등록 {len(onto_errors)}건):")
        for core in sorted(core_seeds, key=lambda c: -len(core_seeds[c])):
            print(f"  {core:<18} {len(core_seeds[core])} seed")
        cross5 = [c for c, s in core_seeds.items() if len(s) == 5]
        print(f"\n5개 도메인 전부 커버하는 코어: {sorted(cross5)}")

    if all_errors:
        print(f"\n[FAIL] {len(all_errors)}건:")
        for e in all_errors[:40]:
            print(f"  - {e}")
        return 1
    print("\n[OK] 공통 부모 포맷 + 온톨로지 등록 + 코어 통일 완료")
    return 0


if __name__ == "__main__":
    sys.exit(main())
