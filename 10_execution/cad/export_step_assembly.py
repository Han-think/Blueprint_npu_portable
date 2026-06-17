"""
export_step_assembly.py -- CAD-grade STEP part/assembly export
==============================================================

CAD/CATIA workflow parity for the seed designs: every part_tree root part
becomes a standalone B-rep STEP part, and the positioned set becomes one
assembly STEP whose component tree opens with named parts in FreeCAD /
SolidWorks / CATIA. assembly_structure.json records placements and mates so
constraints can be rebuilt in CAD.

With --cfd it also emits analysis pre-processing geometry:
  - <seed>_fused.step      union of all placed parts (closed outer solid)
  - <seed>_fluid_domain.step   farfield box minus fused body (external flow)
  - cfd_meta.json          reference dims / projected areas / domain size

Honest limit: geometry is educational mock-assembly level. CFD on it shows
shape trends and comparative behavior, not absolute performance numbers.

Usage:
    python export_step_assembly.py <seed> [--cfd] [--verify] | --all [--cfd]
Output:
    10_execution/cad/output/<seed>/step/, <seed>_assembly.step, cfd/
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from build123d import Box, Compound, Pos, Rotation, export_step, import_step

import build_solid as bs
from build_solid import REPO, SEEDS, OUT, exportable, place_for_seed, safe_num, assembled_layout
from export_print_parts import build_part_states, SEED_LIST, DISPLAY_ONLY_SEEDS

# joints whose note/mate suggests rotation get a revolute mate label in the
# structure file (STEP AP214 carries geometry + names, not kinematic mates)
ROTARY_HINTS = ("revolute", "hinge", "tilt", "rotate", "pivot", "joint cartridge", "j1", "j2", "j3")

FARFIELD_MULT = {"x": 5.0, "y": 4.0, "z": 6.0}
EXTERNAL_FLOW_SEEDS = {"long_range_recon_wing", "tiltrotor", "small_launch_vehicle"}


def mate_kind(joint: dict) -> str:
    text = f"{joint.get('mate', '')} {joint.get('note', '')} {joint.get('id', '')}".lower()
    return "revolute" if any(h in text for h in ROTARY_HINTS) else "rigid"


def export_seed(seed: str, cfd: bool, verify: bool, seed_dir: str | None = None) -> int:
    base = bs.resolve_seed_dir(seed, seed_dir)
    out_name = f"{seed}_generated" if seed_dir else seed
    pkg = json.loads((base / "package.json").read_text(encoding="utf-8"))
    bp = pkg["schema_v6_blueprint"]
    env = bp.get("cad_brief", {}).get("envelope_mm", [100, 100, 100])

    asm_path = base / "assembly.json"
    asm = json.loads(asm_path.read_text(encoding="utf-8")) if asm_path.exists() else {}
    joints = asm.get("joints", [])

    # nominal solids (no print clearance: analysis uses nominal dimensions)
    states, qty, _, _ = build_part_states(seed, pkg, clearance_by_part={})

    out_dir = OUT / out_name
    step_dir = out_dir / "step"
    step_dir.mkdir(parents=True, exist_ok=True)

    # 조립된 데이텀 레이아웃: mate된 모듈이 실제로 맞붙는 합체 구조 (audit가 이 placement를 읽음)
    layout, layout_meta = assembled_layout(states, joints, env, return_meta=True)

    placed_children = []
    structure_parts = []
    for part in states.values():
        solid = exportable(part.solid)
        safe_label = "".join(ch if ch.isalnum() else "_" for ch in part.label.lower())[:40]
        part_path = step_dir / f"{part.id}_{safe_label}.step"
        export_step(solid, str(part_path))

        # GAP-4: layout = {center, rot}. 파트를 로컬중심에서 회전 후 desired center에 배치.
        lp = layout.get(part.id)
        rot = [0.0, 0.0, 0.0]
        if isinstance(lp, dict):
            dc = lp.get("center") or [0, 0, 0]
            rot = lp.get("rot") or [0.0, 0.0, 0.0]
            try:
                sbb = solid.bounding_box()
                lc = [(sbb.min.X + sbb.max.X) / 2, (sbb.min.Y + sbb.max.Y) / 2, (sbb.min.Z + sbb.max.Z) / 2]
            except Exception:
                lc = [0, 0, 0]
            if any(rot):
                placed = Pos(*dc) * Rotation(*rot) * Pos(-lc[0], -lc[1], -lc[2]) * solid
            else:
                placed = Pos(dc[0] - lc[0], dc[1] - lc[1], dc[2] - lc[2]) * solid
        else:
            placed = Pos(*(lp or place_for_seed(seed, part, env))) * solid
        placed.label = f"{part.id} {part.label}"[:60]
        placed_children.append(placed)
        # audit는 placement_translation_mm 을 AABB 중심으로 사용 → 실제 배치 솔리드의 중심/크기를 기록
        try:
            pbb = placed.bounding_box()
            center = [round((pbb.min.X + pbb.max.X) / 2, 2), round((pbb.min.Y + pbb.max.Y) / 2, 2), round((pbb.min.Z + pbb.max.Z) / 2, 2)]
            bbox = [round(pbb.max.X - pbb.min.X, 2), round(pbb.max.Y - pbb.min.Y, 2), round(pbb.max.Z - pbb.min.Z, 2)]
        except Exception:
            center, bbox = [0, 0, 0], [0, 0, 0]
        structure_parts.append({
            "part_id": part.id,
            "label": part.label,
            "step_file": f"step/{part_path.name}",
            "qty": qty.get(part.id, 1),
            "bbox_mm": bbox,
            "placement_translation_mm": center,
            "placement_rotation_deg": [round(v, 1) for v in rot],
        })

    assembly = Compound(label=f"{seed}_assembly", children=placed_children)
    asm_step = out_dir / f"{seed}_assembly.step"
    export_step(assembly, str(asm_step))

    structure = {
        "schema": "blueprint_step_assembly_structure_v1",
        "seed": seed,
        "assembly_step": asm_step.name,
        "note": ("EDUCATIONAL DISPLAY MOCKUP geometry — analysis results are shape-trend level, not certified performance."
                 if seed in DISPLAY_ONLY_SEEDS else
                 "Educational mock assembly geometry — CFD/FEA on this model is for shape comparison and trend review, not absolute performance."),
        "parts": structure_parts,
        "mates": [
            {
                "id": j.get("id"),
                "kind": mate_kind(j),
                "part_a": j.get("partA"),
                "part_b": j.get("partB"),
                "mate": j.get("mate"),
                "clearance_mm": safe_num(j.get("clearance_mm"), 0),
                "containment": bool(j.get("containment")),
                "note": j.get("note", ""),
            } for j in joints
        ],
        "consistency": {
            "parts_exported": len(structure_parts),
            "part_tree_roots": len(states),
            "mates_recorded": len(joints),
        },
        "layout": {
            "method": "joint_directional_tree",
            "datum": layout_meta.get("datum"),
            "unsatisfied_mates": layout_meta.get("unsatisfied_mates", []),
            "note": "Children placed adjacent to BFS-tree parent on distinct faces; collision-free is "
                    "re-verified by assembly_interference_audit, not assumed. Secondary mates of multi-mate "
                    "parts are reported as unsatisfied residuals (no constraint solver).",
        },
    }
    (out_dir / "assembly_structure.json").write_text(json.dumps(structure, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[{seed}] STEP: {len(structure_parts)} parts + {asm_step.relative_to(REPO)} · mates {len(joints)}")

    if cfd:
        cfd_dir = out_dir / "cfd"
        cfd_dir.mkdir(exist_ok=True)
        fused = None
        for child in placed_children:
            fused = child if fused is None else fused + child
        fused = exportable(fused)
        export_step(fused, str(cfd_dir / f"{seed}_fused.step"))

        bb = fused.bounding_box()
        size = (bb.max.X - bb.min.X, bb.max.Y - bb.min.Y, bb.max.Z - bb.min.Z)
        center = ((bb.min.X + bb.max.X) / 2, (bb.min.Y + bb.max.Y) / 2, (bb.min.Z + bb.max.Z) / 2)
        meta = {
            "schema": "blueprint_cfd_meta_v1",
            "seed": seed,
            "disclaimer": "Mock-level geometry: use for shape-trend CFD only, never for absolute performance or operational claims.",
            "body_bbox_mm": [round(s, 1) for s in size],
            "body_volume_mm3": round(fused.volume, 0),
            "reference_length_mm": round(max(size), 1),
            "projected_area_xy_mm2": round(size[0] * size[1], 0),
            "projected_area_frontal_yz_mm2": round(size[1] * size[2], 0),
        }
        if seed in EXTERNAL_FLOW_SEEDS:
            dom = Box(size[0] * FARFIELD_MULT["x"], size[1] * FARFIELD_MULT["y"], size[2] * FARFIELD_MULT["z"])
            fluid = exportable(Pos(*center) * dom - fused)
            export_step(fluid, str(cfd_dir / f"{seed}_fluid_domain.step"))
            meta["fluid_domain_mm"] = [round(size[0] * FARFIELD_MULT["x"], 0),
                                       round(size[1] * FARFIELD_MULT["y"], 0),
                                       round(size[2] * FARFIELD_MULT["z"], 0)]
            meta["farfield_multipliers"] = FARFIELD_MULT
        (cfd_dir / "cfd_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  cfd: fused{' + fluid_domain' if seed in EXTERNAL_FLOW_SEEDS else ''} → {cfd_dir.relative_to(REPO)}")

    if verify:
        re_asm = import_step(str(asm_step))
        vol = exportable(re_asm).volume
        n_children = len(getattr(re_asm, "children", []) or [])
        ok = vol > 0
        print(f"  verify: reload {'OK' if ok else 'FAIL'} · volume {vol:.0f} mm^3 · components {n_children}")
        if not ok:
            return 1
    return 0


def main(argv):
    rest, seed_dir = bs.parse_dir_flag(argv[1:])
    args = [a for a in rest if a]
    cfd = "--cfd" in args
    verify = "--verify" in args
    args = [a for a in args if not a.startswith("--")] or (["--all"] if "--all" in argv else [])
    if not args and "--all" not in argv:
        print("usage: python export_step_assembly.py <seed> [--cfd] [--verify] [--dir <package_dir>] | --all [--cfd]")
        return 1
    seeds = SEED_LIST if "--all" in argv else args
    rc = 0
    for seed in seeds:
        try:
            rc |= export_seed(seed, cfd, verify, seed_dir)
        except Exception as exc:
            print(f"[{seed}] FAILED: {exc}")
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
