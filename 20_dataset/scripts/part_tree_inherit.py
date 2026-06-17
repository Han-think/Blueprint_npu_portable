"""
part_tree_inherit.py — part_tree 노드 속성 상속 정규화기
=========================================================

schema_v6 의 part_tree 는 자기참조 재귀 트리다. 자식이 부모의 material/process 를
물려받고, 다를 때만 override 하는 "상속" 규칙을 코드로 강제한다.

기능:
  1. resolve_inheritance() — 빈 material/process 를 부모 값으로 채운 effective(유효) 트리 산출
  2. 중복 명시 경고 — 자식이 부모와 똑같은 값을 다시 적은 경우, 상속으로 생략 가능하다고 경고

사용:
    python part_tree_inherit.py <package.json | part_tree.json> [--json]
    # 인자 없으면 5개 seed 전체를 점검
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

INHERITABLE = ("material", "process")
SEEDS_DIR = Path(__file__).resolve().parents[1] / "seeds"
SEED_NAMES = ["cubesat", "tiltrotor", "robot_arm", "small_launch_vehicle", "long_range_recon_wing", "haptic_glove"]


def resolve_inheritance(node: dict, inherited: dict | None = None,
                        warnings: list | None = None, path: str = "") -> dict:
    """자식의 빈 상속속성을 부모값으로 채운 effective 노드를 반환. 중복 명시는 warnings 에 기록."""
    inherited = inherited or {}
    warnings = warnings if warnings is not None else []
    node_id = str(node.get("id", "?"))
    here = f"{path}/{node_id}"

    eff = dict(node)
    for attr in INHERITABLE:
        val = node.get(attr)
        if val in (None, ""):
            if attr in inherited:            # 부모로부터 상속
                eff[attr] = inherited[attr]
        elif attr in inherited and val == inherited[attr]:
            warnings.append(f"{here}: '{attr}={val}' 가 부모와 동일 — 상속으로 생략 가능")

    # 자식에게 물려줄 유효값
    child_inherited = {a: eff[a] for a in INHERITABLE if eff.get(a) not in (None, "")}
    children = node.get("children") or []
    if children:
        eff["children"] = [resolve_inheritance(c, child_inherited, warnings, here) for c in children]
    return eff


def extract_part_tree(obj: dict) -> dict | None:
    """package.json(schema_v6_blueprint.part_tree) 또는 raw part_tree 모두 수용."""
    if "part_tree" in obj:
        return obj["part_tree"]
    if "schema_v6_blueprint" in obj and "part_tree" in obj["schema_v6_blueprint"]:
        return obj["schema_v6_blueprint"]["part_tree"]
    return None


def process_file(path: Path, emit_json: bool = False) -> int:
    obj = json.loads(path.read_text(encoding="utf-8"))
    pt = extract_part_tree(obj)
    if pt is None:
        print(f"  [SKIP] {path}: part_tree 없음")
        return 0
    warnings: list = []
    eff = resolve_inheritance(pt, warnings=warnings)
    if emit_json:
        print(json.dumps(eff, ensure_ascii=False, indent=2))
        return len(warnings)
    print(f"  [{path.parent.name}] 중복 명시 {len(warnings)}건")
    for w in warnings:
        print(f"     - {w}")
    return len(warnings)


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    emit_json = "--json" in argv
    if args:
        return 0 if process_file(Path(args[0]), emit_json) >= 0 else 1
    # 인자 없음 → 5 seed 전체 점검
    total = 0
    print("part_tree 상속 점검 (5 seed)")
    for s in SEED_NAMES:
        pkg = SEEDS_DIR / s / "package.json"
        if pkg.exists():
            total += process_file(pkg)
    print(f"\n총 중복 명시: {total}건 — 상속으로 단순화 가능")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
