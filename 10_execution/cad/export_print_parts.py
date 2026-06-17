"""
export_print_parts.py -- per-part printable STL export + assembly manifest
==========================================================================

build_solid.py merges all root parts into one mock-assembly STL for review.
This exporter keeps each root part separate so it can be printed on its own
bed and assembled afterwards:

  - one STL per part_tree root child, laid flat at the origin (bottom at Z=0)
  - mating clearance from assembly.json joints applied to the male (partA)
    body dims before the solid is built, so printed parts fit first try
  - fastener holes cut per assembly.json (clearance/tap), same as the
    combined build
  - assembly_manifest.json + .md: print counts, joints with applied
    clearance, hardware BOM, assembly order, safety boundary notes

Honest limits: geometry is mock-assembly level. Clearance is applied as a
uniform lateral reduction of the male part body, not as a toleranced mating
feature pair; parts whose base came from explicit geometry ops get a manifest
warning instead.

Usage:
    python export_print_parts.py <seed> | --all
Output:
    10_execution/cad/output/<seed>/print/
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import build_solid as bs
from build_solid import (PartState, REPO, SEEDS, OUT, ensure_base, apply_feature_op,
                         apply_edge_finishes, add_fastener_holes, build_target_parent_map,
                         exportable, nominal_dims, op_parent_id, primitive_for_op,
                         root_children, safe_num)
from build123d import Box, Cylinder, Pos, export_stl

SEED_LIST = ["cubesat", "tiltrotor", "robot_arm", "small_launch_vehicle",
             "long_range_recon_wing", "haptic_glove"]

DISPLAY_ONLY_SEEDS = {"small_launch_vehicle", "cubesat"}

# 프린트 베드 (validate_print.DEFAULT_BED 과 일치). 이 한도를 넘는 파트는 분할한다.
BED_MM = (220.0, 220.0, 250.0)
SEG_SAFETY_MM = 6.0      # 분할 길이 여유
KEY_SIZE_MM = 6.0        # 정렬 키 단면(가로/세로)
KEY_DEPTH_MM = 10.0      # 정렬 키가 면을 파고드는 깊이
KEY_INSET_MM = 9.0       # 단면 모서리에서 안쪽으로


def _flatten(solid):
    """솔리드 바닥을 Z=0, XY 중심으로 정렬."""
    bb = solid.bounding_box()
    return Pos(-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, -bb.min.Z) * solid


def _alignment_keys(face_val, axis, half0, half1, ax0, ax1):
    """절단면(축 axis, 위치 face_val)에 모서리 정렬 키 포켓 커터들을 만든다.
    half0/half1 = 단면(ax0,ax1) 반치수. 면을 ±KEY_DEPTH/2 만큼 양쪽에서 파도록 면 중심에 배치."""
    cutters = []
    size = [0.0, 0.0, 0.0]
    size[axis] = KEY_DEPTH_MM
    size[ax0] = KEY_SIZE_MM
    size[ax1] = KEY_SIZE_MM
    o0 = max(half0 - KEY_INSET_MM, KEY_SIZE_MM)
    o1 = max(half1 - KEY_INSET_MM, KEY_SIZE_MM)
    for s0 in (o0, -o0):
        for s1 in (o1, -o1):
            pos = [0.0, 0.0, 0.0]
            pos[axis] = face_val
            pos[ax0] = s0
            pos[ax1] = s1
            cutters.append(Pos(*pos) * Box(*size))
    return cutters


def segment_oversized(solid, part_id, label):
    """베드를 넘는 파트를 최장 초과축으로 분할. 각 세그먼트에 정렬 키 포켓을 파고,
    바닥 정렬해 반환. (segments, coupler_joints) — 분할 불필요 시 (None, [])."""
    bb = solid.bounding_box()
    size = [bb.max.X - bb.min.X, bb.max.Y - bb.min.Y, bb.max.Z - bb.min.Z]
    over = [size[i] - BED_MM[i] for i in range(3)]
    if max(over) <= 0:
        return None, [], None
    axis = max(range(3), key=lambda i: over[i])
    ax0, ax1 = [i for i in range(3) if i != axis]
    import math as _m
    n = max(2, _m.ceil(size[axis] / (BED_MM[axis] - SEG_SAFETY_MM)))
    lo = [bb.min.X, bb.min.Y, bb.min.Z][axis]
    seg_len = size[axis] / n
    half0, half1 = size[ax0] / 2, size[ax1] / 2
    center = [(bb.min.X + bb.max.X) / 2, (bb.min.Y + bb.max.Y) / 2, (bb.min.Z + bb.max.Z) / 2]

    segments, couplers = [], []
    for i in range(n):
        a_lo = lo + i * seg_len
        a_hi = a_lo + seg_len
        slab_size = [0.0, 0.0, 0.0]
        slab_size[axis] = seg_len + 0.02
        slab_size[ax0] = size[ax0] + 2
        slab_size[ax1] = size[ax1] + 2
        slab_center = list(center)
        slab_center[axis] = (a_lo + a_hi) / 2
        seg = solid & (Pos(*slab_center) * Box(*slab_size))
        # 내부 절단면에 정렬 키 포켓
        cutters = []
        if i > 0:
            cutters += _alignment_keys(a_lo, axis, half0, half1, ax0, ax1)
        if i < n - 1:
            cutters += _alignment_keys(a_hi, axis, half0, half1, ax0, ax1)
        for cut in cutters:
            try:
                seg = seg - cut
            except Exception as e:
                logging.warning("alignment key cut failed: %s", e)
        seg = exportable(seg)
        if seg is None or seg.volume <= 1:
            continue
        seg = _flatten(seg)
        sbb = seg.bounding_box()
        suffix = f"seg{i + 1}"
        segments.append({
            "suffix": suffix,
            "solid": seg,
            "bbox": [round(sbb.max.X - sbb.min.X, 1), round(sbb.max.Y - sbb.min.Y, 1), round(sbb.max.Z, 1)],
            "volume": round(seg.volume, 0),
        })
        if i > 0:
            couplers.append({
                "id": f"SEG-{part_id}-{i}",
                "male_part": f"{part_id}_seg{i}",
                "female_part": f"{part_id}_seg{i + 1}",
                "mate": "alignment_key",
                "clearance_mm": 0.2,
                "note": f"print-segmentation coupler: 4× {KEY_SIZE_MM}mm corner alignment keys join {part_id} segments along axis {'XYZ'[axis]}",
            })
    if not segments:
        return None, [], None
    meta = {"part_id": part_id, "axis": "XYZ"[axis], "segments": len(segments),
            "segment_len_mm": round(seg_len, 1), "key_size_mm": KEY_SIZE_MM}
    return segments, couplers, meta

# process-level print fit defaults; joint clearance_mm from assembly.json wins
PRINT_FIT = {
    "FDM": {"default_clearance_mm": 0.25, "hole_compensation_mm": 0.15},
    "SLA": {"default_clearance_mm": 0.15, "hole_compensation_mm": 0.05},
}


def build_part_states(seed: str, pkg: dict, clearance_by_part: dict[str, float]):
    """Replicates build_solid.build() per-part stage, with male-side clearance
    folded into the base dims before the solid exists."""
    bp = pkg["schema_v6_blueprint"]
    ops = bp.get("geometry_ops", [])
    env = bp.get("cad_brief", {}).get("envelope_mm", [100, 100, 100])
    children = root_children(bp.get("part_tree", {}))
    if not children:
        raise SystemExit(f"[{seed}] part_tree has no root children")

    parent_map = build_target_parent_map(children)
    states, qty = {}, {}
    for idx, child in enumerate(children):
        cid = child.get("id")
        if not cid:
            continue
        states[cid] = PartState(cid, child.get("name", cid), idx)
        qty[cid] = max(1, int(safe_num(child.get("qty"), 1)))
    fallback_id = next(iter(states))

    warnings = []
    # pre-shrink: bake clearance into nominal base dims for male parts
    original_nominal = bs.nominal_dims

    def nominal_with_clearance(s, part, e):
        l, w, h = original_nominal(s, part, e)
        c = clearance_by_part.get(part.id, 0.0)
        if c > 0:
            return (max(l - c, 0.5), max(w - c, 0.5), h)
        return (l, w, h)

    bs.nominal_dims = nominal_with_clearance
    explicit_base = set()  # 명시적 op로 base가 만들어진 파트 → 사후 횡 clearance 적용 대상
    try:
        for idx, op in enumerate(ops):
            pid = op_parent_id(op, parent_map, fallback_id)
            part = states.get(pid) or states[fallback_id]
            primitive, dims, label = primitive_for_op(op, bs.nominal_dims(seed, part, env))
            if primitive is not None and (part.solid is None or op.get("target") == part.id):
                if part.solid is None:
                    part.solid, part.dims = primitive, dims
                    if clearance_by_part.get(part.id, 0.0) > 0:
                        explicit_base.add(part.id)
                else:
                    part.solid = part.solid + (Pos(*bs.feature_offset(part, idx)) * primitive)
                part.applied.append((op.get("id", f"op-{idx}"), label))
                continue
            apply_feature_op(part, op, seed, env, idx)
        for part in states.values():
            ensure_base(part, seed, env)
    finally:
        bs.nominal_dims = original_nominal
    return states, qty, warnings, explicit_base


def apply_lateral_clearance(solid, c):
    """수(male) 파트의 횡 2축(가장 얇지 않은 두 축)을 c만큼 줄여 끼워맞춤 clearance 적용.
    명시적 op base(실린더/박스 등)에도 동작. 실패 시 원본 반환."""
    try:
        bb = solid.bounding_box()
        size = [bb.max.X - bb.min.X, bb.max.Y - bb.min.Y, bb.max.Z - bb.min.Z]
        cx = (bb.min.X + bb.max.X) / 2
        cy = (bb.min.Y + bb.max.Y) / 2
        cz = (bb.min.Z + bb.max.Z) / 2
        # 장축(가장 긴 축)은 길이 유지, 나머지 두 축을 c 축소
        long_axis = max(range(3), key=lambda i: size[i])
        keep = [size[0] + 2, size[1] + 2, size[2] + 2]
        for i in range(3):
            if i != long_axis:
                keep[i] = max(size[i] - c, 0.5)
        return solid & (Pos(cx, cy, cz) * Box(*keep))
    except Exception:
        return solid


def fit_coupon(joint_clearances: list[float], process: str):
    """Small test gauge: one pin + holes at the clearances this seed actually
    uses, printed before the real parts."""
    pin_d = 6.0
    clearances = sorted(set(round(c, 2) for c in joint_clearances if c > 0)) or \
        [PRINT_FIT.get(process, PRINT_FIT["FDM"])["default_clearance_mm"]]
    clearances = clearances[:4]
    plate_l = 18 + 14 * len(clearances)
    plate = Box(plate_l, 16, 5)
    x = -plate_l / 2 + 12
    for c in clearances:
        plate = plate - (Pos(x, 0, 0) * Cylinder(radius=(pin_d + c) / 2, height=8))
        x += 14
    pin = Pos(plate_l / 2 + 8, 0, 5) * Cylinder(radius=pin_d / 2, height=15)
    return exportable(plate + pin), clearances


def export_seed(seed: str, seed_dir: str | None = None) -> int:
    base = bs.resolve_seed_dir(seed, seed_dir)
    out_name = f"{seed}_generated" if seed_dir else seed
    pkg = json.loads((base / "package.json").read_text(encoding="utf-8"))
    bp = pkg.get("schema_v6_blueprint", {})
    process = str(bp.get("print_profile", {}).get("process", bp.get("cad_brief", {}).get("process", "FDM"))).upper()
    if process not in PRINT_FIT:
        process = "FDM"

    asm_path = base / "assembly.json"
    asm = json.loads(asm_path.read_text(encoding="utf-8")) if asm_path.exists() else {}
    joints = asm.get("joints", [])
    fasteners = asm.get("fasteners", [])

    # male side = partA: gets the lateral clearance reduction
    clearance_by_part: dict[str, float] = {}
    for j in joints:
        c = safe_num(j.get("clearance_mm"), PRINT_FIT[process]["default_clearance_mm"])
        pa = j.get("partA")
        if pa:
            clearance_by_part[pa] = max(clearance_by_part.get(pa, 0.0), c)

    states, qty, warnings, explicit_base = build_part_states(seed, pkg, clearance_by_part)

    out_dir = OUT / out_name / "print"
    out_dir.mkdir(parents=True, exist_ok=True)
    # 이전 런의 STL(특히 분할 전 oversized 파일)이 남아 validate를 오염시키지 않도록 청소
    for old in out_dir.glob("*.stl"):
        old.unlink()

    part_entries = []
    segment_joints = []
    segmentation_meta = []
    for part in states.values():
        add_fastener_holes(part, fasteners)
        apply_edge_finishes(part)
        # 명시적 op base 파트도 횡 clearance 적용 (사전 nominal 축소를 못 받은 파트)
        if part.id in explicit_base:
            part.solid = apply_lateral_clearance(part.solid, clearance_by_part.get(part.id, 0.0))
        solid = _flatten(exportable(part.solid))
        safe_label = "".join(ch if ch.isalnum() else "_" for ch in part.label.lower())[:40]

        segments, couplers, seg_meta = segment_oversized(solid, part.id, part.label)
        if segments:
            # 베드 초과 → 정렬 키로 결합되는 세그먼트들로 분할 출력
            for seg in segments:
                fname = f"{part.id}_{seg['suffix']}_{safe_label}.stl"
                export_stl(seg["solid"], str(out_dir / fname))
                part_entries.append({
                    "part_id": f"{part.id}_{seg['suffix']}",
                    "label": f"{part.label} ({seg['suffix']})",
                    "file": fname,
                    "print_count": qty.get(part.id, 1),
                    "bbox_mm": seg["bbox"],
                    "volume_mm3": seg["volume"],
                    "applied_clearance_mm": clearance_by_part.get(part.id, 0.0),
                    "orientation": "bottom face on bed (as exported)",
                    "segment_of": part.id,
                })
            segment_joints.extend(couplers)
            segmentation_meta.append(seg_meta)
        else:
            fname = f"{part.id}_{safe_label}.stl"
            export_stl(solid, str(out_dir / fname))
            bb = solid.bounding_box()
            part_entries.append({
                "part_id": part.id,
                "label": part.label,
                "file": fname,
                "print_count": qty.get(part.id, 1),
                "bbox_mm": [round(bb.max.X - bb.min.X, 1), round(bb.max.Y - bb.min.Y, 1), round(bb.max.Z, 1)],
                "volume_mm3": round(solid.volume, 0),
                "applied_clearance_mm": clearance_by_part.get(part.id, 0.0),
                "orientation": "bottom face on bed (as exported)",
            })

    coupon, coupon_clearances = fit_coupon([safe_num(j.get("clearance_mm"), 0) for j in joints], process)
    export_stl(coupon, str(out_dir / "fit_test_coupon.stl"))

    manifest = {
        "schema": "blueprint_print_assembly_manifest_v1",
        "seed": seed,
        "process": process,
        "print_fit_defaults": PRINT_FIT[process],
        "safety_note": ("EDUCATIONAL DISPLAY MOCKUP — non-functional; do not treat as flight/operational hardware."
                        if seed in DISPLAY_ONLY_SEEDS else
                        "Educational mock assembly for design review; verify all fits with the coupon before committing full prints."),
        "print_first": {
            "file": "fit_test_coupon.stl",
            "purpose": f"pin Ø6 + holes at clearances {coupon_clearances} mm — confirm which clearance fits your printer before printing parts",
        },
        "parts": part_entries,
        "joints": [
            {
                "id": j.get("id"),
                "male_part": j.get("partA"),
                "female_part": j.get("partB"),
                "mate": j.get("mate"),
                "clearance_mm": safe_num(j.get("clearance_mm"), PRINT_FIT[process]["default_clearance_mm"]),
                "containment": bool(j.get("containment")),
                "note": j.get("note", ""),
            } for j in joints
        ] + segment_joints,
        "fasteners": fasteners,
        "hardware_bom": asm.get("hardware_bom", []) + (
            [{"standard": "alignment key 6mm", "qty": 4 * len(segment_joints)}] if segment_joints else []
        ),
        "segmentation": segmentation_meta,
        "assembly_order": [f"{j.get('id')}: {j.get('partA')} → {j.get('partB')} ({j.get('mate')})" for j in joints]
            + [f"{c['id']}: {c['male_part']} → {c['female_part']} ({c['mate']})" for c in segment_joints],
        "warnings": warnings,
    }
    (out_dir / "assembly_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [f"# {seed} — print & assembly guide", "", f"**Process:** {process}", f"**Safety:** {manifest['safety_note']}", "",
          "## 0. Print the fit coupon first",
          f"`fit_test_coupon.stl` — pin Ø6 + holes at {coupon_clearances} mm. Use the loosest hole that still grips.", "",
          "## 1. Parts"]
    for p in part_entries:
        md.append(f"- `{p['file']}` × {p['print_count']} — {p['label']} · bbox {p['bbox_mm']} mm · clearance {p['applied_clearance_mm']} mm")
    md += ["", "## 2. Assembly order"]
    for i, j in enumerate(manifest["joints"], 1):
        md.append(f"{i}. {j['male_part']} → {j['female_part']} ({j['mate']}, {j['clearance_mm']} mm) — {j['note']}")
    md += ["", "## 3. Hardware"]
    for h in manifest["hardware_bom"]:
        md.append(f"- {h.get('standard')} × {h.get('qty')}")
    if warnings:
        md += ["", "## ⚠ Warnings"] + [f"- {w}" for w in warnings]
    (out_dir / "assembly_manifest.md").write_text("\n".join(md), encoding="utf-8")

    print(f"[{seed}] print parts: {len(part_entries)} STL + coupon → {out_dir.relative_to(REPO)}")
    for w in warnings:
        print(f"  warn: {w}")
    return 0


def main(argv):
    rest, seed_dir = bs.parse_dir_flag(argv[1:])
    args = [a for a in rest if a]
    if not args:
        print("usage: python export_print_parts.py <seed> [--dir <package_dir>] | --all")
        return 1
    seeds = SEED_LIST if args[0] == "--all" else [args[0]]
    rc = 0
    for seed in seeds:
        try:
            rc |= export_seed(seed, seed_dir)
        except Exception as exc:
            print(f"[{seed}] FAILED: {exc}")
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
