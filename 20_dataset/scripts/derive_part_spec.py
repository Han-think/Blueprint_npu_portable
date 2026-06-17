"""
derive_part_spec.py — 파트 단위 구체 도안(part_spec) 통합 빌더
==============================================================

한 파트의 흩어진 구체 정보(part_tree·geometry_ops·assembly·cad_brief·print_profile)를
파트당 1 레코드로 통합한다. "상상의 그림이 아닌 구체적 도안."

출력: 20_dataset/seeds/<seed>/part_spec.jsonl  (L1 파트 = redesigned_bom 단위)

사용:
    python derive_part_spec.py <seed>      # 예: cubesat
    python derive_part_spec.py --all       # 5 seed 전체
"""
from __future__ import annotations
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEEDS = ROOT / "seeds"
SEED_LIST = ["cubesat", "tiltrotor", "robot_arm", "small_launch_vehicle", "long_range_recon_wing", "haptic_glove"]

# anchor 토큰 → 사람이 읽는 face 표기 (mate face 보강)
ANCHOR_FACE = {
    "face_+X": "+X", "face_-X": "-X", "face_+Y": "+Y", "face_-Y": "-Y",
    "face_+Z": "+Z", "face_-Z": "-Z", "face_X_both": "+X/-X",
    "corners_4": "4 corners", "internal": "internal", "axis_Z": "Z axis", "center": "center",
}


def find_node(node, pid):
    if node.get("id") == pid:
        return node
    for c in node.get("children", []):
        r = find_node(c, pid)
        if r:
            return r
    return None


def child_ids(node):
    return {node["id"]} | {c["id"] for c in node.get("children", [])}


def envelope_of(ops, ids):
    """파트(또는 자식) 의 box/cylinder 에서 대표 envelope 추출."""
    for op in ops:
        if op.get("target") in ids and op["op"] == "box" and "size_mm" in op.get("args", {}):
            return op["args"]["size_mm"]
    for op in ops:
        if op.get("target") in ids and op["op"] == "cylinder" and "diameter_mm" in op.get("args", {}):
            a = op["args"]; d = a["diameter_mm"]; h = a.get("height_mm", a.get("length_mm", d))
            return [d, d, h]
    return None


def print_orientation(env):
    """파트 형상비율 기반 출력방향 휴리스틱."""
    if not env:
        return "longest axis vertical"
    longest = max(range(3), key=lambda i: env[i])
    return ["X axis vertical", "Y axis vertical", "Z axis vertical"][longest]


def build(seed: str) -> int:
    pkg = json.loads((SEEDS / seed / "package.json").read_text(encoding="utf-8"))
    bp = pkg["schema_v6_blueprint"]
    cad = bp.get("cad_brief", {})
    pp = bp.get("print_profile", {})
    ops = bp.get("geometry_ops", [])
    target = pkg["target"]["vehicle_id"]
    root = bp["part_tree"]
    asm_p = SEEDS / seed / "assembly.json"
    asm = json.loads(asm_p.read_text(encoding="utf-8")) if asm_p.exists() else {"fasteners": [], "joints": []}

    # fastener anchor → face 룩업
    f_anchor = {}
    for f in asm.get("fasteners", []):
        for pid in f.get("joins", []):
            f_anchor.setdefault(pid, f.get("anchor"))

    records = []
    for part in pkg.get("redesigned_bom", []):
        pid = part["id"]
        node = find_node(root, pid) or {}
        ids = child_ids(node) if node else {pid}
        env = envelope_of(ops, ids)
        features = [{"op": o["op"], "target": o.get("target"), "args": {k: v for k, v in o.get("args", {}).items() if k != "purpose"}}
                    for o in ops if o.get("target") in ids]

        # interfaces: joints + fasteners 통합
        interfaces = []
        for j in asm.get("joints", []):
            if pid in (j["partA"], j["partB"]):
                other = j["partB"] if j["partA"] == pid else j["partA"]
                fa = next((f for f in asm["fasteners"] if pid in f.get("joins", []) and other in f.get("joins", [])), None)
                interfaces.append({
                    "to": other, "mate": j["mate"], "clearance_mm": j.get("clearance_mm"),
                    "fastener": ({"std": fa["standard"], "kind": fa["kind"], "qty": fa["qty"], "hole": fa.get("hole")} if fa else None),
                    "face": ANCHOR_FACE.get(fa.get("anchor")) if fa else None,
                })

        records.append({
            "schema": "blueprint_part_spec_v1",
            "target": target,
            "part_id": pid,
            "name": part.get("label", node.get("name", pid)),
            "material": node.get("material", cad.get("material", "")),
            "process": node.get("process", ""),
            "qty": node.get("qty", part.get("qty", 1)),
            "envelope_mm": env,
            "features": features,
            "interfaces": interfaces,
            "print": {"orientation": print_orientation(env), "supports": pp.get("supports", "min")},
            "tolerances_mm": cad.get("tolerances_mm", {}),
            "printable_as": part.get("printable_as", ""),
            "service_access_preserved": part.get("service_access_preserved", []),
            "verify": [f"check {pid} envelope {env} prints within bed",
                       f"verify interfaces ({len(interfaces)}) mate with stated clearance"],
        })

    out = SEEDS / seed / "part_spec.jsonl"
    out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n", encoding="utf-8")
    filled = sum(1 for r in records if r["envelope_mm"] and r["features"])
    print(f"[{seed}] part_spec {len(records)} parts → {out.relative_to(ROOT.parent)}")
    print(f"  envelope+features 채워진 파트: {filled}/{len(records)} · "
          f"interfaces 총 {sum(len(r['interfaces']) for r in records)}")
    return 0


def main(argv):
    if "--all" in argv:
        for s in SEED_LIST:
            build(s)
        return 0
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args:
        print("사용: python derive_part_spec.py <seed> | --all"); return 1
    return build(args[0])


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
