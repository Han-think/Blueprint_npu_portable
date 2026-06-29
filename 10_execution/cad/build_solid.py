"""
build_solid.py -- schema_v6 geometry_ops -> visible mock assembly STL
=====================================================================

The first CAD builder produced valid STL, but most seed parts collapsed into
one center blob. This version builds one local solid per root part in
part_tree, applies each part's visible feature ops, then places those parts in
a seed-specific educational mock-assembly layout.

Goal: reviewable mock assemblies, not flight/industrial/manufacturing CAD.

Usage:
    python build_solid.py <seed>
Output:
    10_execution/cad/output/<seed>/<seed>.stl
"""
from __future__ import annotations

import json
import logging
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    from build123d import (Axis, Box, Compound, Cone, Cylinder, Pos, RegularPolygon, Rotation,
                           ShapeList, Sphere, chamfer, export_stl, extrude, fillet)
except ImportError:
    print("build123d is not installed.")
    print("  install: pip install build123d")
    sys.exit(2)

REPO = Path(__file__).resolve().parents[2]
SEEDS = REPO / "20_dataset" / "seeds"
OUT = Path(__file__).resolve().parent / "output"
MARGIN = 8.0


def exportable(shape):
    if hasattr(shape, "wrapped"):
        return shape
    if isinstance(shape, ShapeList) or isinstance(shape, (list, tuple)):
        return Compound(list(shape))
    return shape


def is_exportable_shape(shape) -> bool:
    try:
        shape = exportable(shape)
        return hasattr(shape, "wrapped")
    except Exception:
        return False


def positioned_shape(shape, pos, fallback=None):
    """Place a shape, but never let build123d Location/list quirks kill a batch.

    Some generated op combinations leave part.solid as a non-shape build123d
    object. `Pos * object` then raises "other must be a list of Locations".
    For audit/corpus recovery, replace that bad local solid with a simple
    fallback body and record the skip at the caller.
    """
    candidate = shape if is_exportable_shape(shape) else fallback
    if not is_exportable_shape(candidate):
        return None
    try:
        return exportable(Pos(*pos) * exportable(candidate))
    except Exception as exc:
        if fallback is not None and fallback is not candidate and is_exportable_shape(fallback):
            try:
                return exportable(Pos(*pos) * exportable(fallback))
            except Exception as exc2:
                print(f"[build_solid] positioned_shape fallback failed: {exc2}")
                return None
        print(f"[build_solid] positioned_shape failed: {exc}")
        return None


def boolean_join(base, piece):
    if piece is None:
        return base
    if base is None:
        return piece
    try:
        return base + piece
    except Exception:
        print("[build_solid] boolean_join: union failed, using Compound fallback")
        return Compound([exportable(base), exportable(piece)])


@dataclass
class PartState:
    id: str
    label: str
    index: int
    solid: object | None = None
    dims: tuple[float, float, float] | None = None
    applied: list[tuple[str, str]] = field(default_factory=list)
    skipped: list[tuple[str, str, str]] = field(default_factory=list)
    deferred_edges: list[dict] = field(default_factory=list)


def safe_num(value, default=0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def axis_open(open_faces, axis):
    if isinstance(open_faces, str):
        open_faces = [open_faces]
    if not isinstance(open_faces, (list, tuple, set)):
        return False
    return any(axis in f for f in (open_faces or []))


def infer_anchor(op: dict) -> str:
    args = op.get("args", {})
    if args.get("anchor"):
        return args["anchor"]
    text = " ".join([
        str(op.get("target", "")),
        str(args.get("purpose", "")),
        str(args.get("feature", "")),
        str(args.get("path", "")),
        str(args.get("text", "")),
    ]).lower()
    if any(k in text for k in ("rail", "corner", "spar", "ring", "axis")):
        return "corners_4"
    if any(k in text for k in ("panel", "groove", "lid", "cover", "window", "label", "cutaway")):
        return "face_+X"
    if any(k in text for k in ("boss", "screw", "fastener", "bolt")):
        return "corners_4"
    if any(k in text for k in ("board", "slot", "shelf", "standoff", "tank", "payload", "battery")):
        return "internal"
    if any(k in text for k in ("cable", "channel", "flow", "harness")):
        return "axis_Z"
    if any(k in text for k in ("hinge", "antenna", "fin", "tail", "gear", "flange", "boom")):
        return "face_+Z"
    return "center"


def anchor_positions(anchor: str, dims) -> list[tuple[float, float, float]]:
    l, w, h = dims
    m = min(MARGIN, max(2.0, min(l, w, h) * 0.18))
    if anchor == "corners_4":
        return [
            (l / 2 - m, w / 2 - m, 0),
            (-(l / 2 - m), w / 2 - m, 0),
            (-(l / 2 - m), -(w / 2 - m), 0),
            (l / 2 - m, -(w / 2 - m), 0),
        ]
    return {
        "face_+X": [(l / 2, 0, 0)],
        "face_-X": [(-l / 2, 0, 0)],
        "face_+Y": [(0, w / 2, 0)],
        "face_-Y": [(0, -w / 2, 0)],
        "face_+Z": [(0, 0, h / 2)],
        "face_-Z": [(0, 0, -h / 2)],
        "face_X_both": [(l / 2, 0, 0), (-l / 2, 0, 0)],
        "internal": [(0, 0, 0)],
        "axis_Z": [(0, 0, 0)],
        "center": [(0, 0, 0)],
    }.get(anchor, [(0, 0, 0)])


def root_children(part_tree: dict) -> list[dict]:
    return part_tree.get("children", []) or []


def _normalize_label(s: str) -> str:
    return str(s or "").lower().replace(" ", "_").replace("-", "_")


def build_target_parent_map(children: list[dict]) -> dict[str, str]:
    out = {}

    def visit(node, parent_id):
        node_id = node.get("id")
        if node_id:
            out[node_id] = parent_id
        node_name = node.get("name") or node.get("label") or ""
        if node_name:
            if node_name not in out:
                out[node_name] = parent_id
            norm = _normalize_label(node_name)
            if norm not in out:
                out[norm] = parent_id
        for child in node.get("children", []) or []:
            visit(child, parent_id)

    for child in children:
        root_id = child.get("id")
        if root_id:
            visit(child, root_id)
    return out


def op_parent_id(op: dict, parent_map: dict[str, str], fallback_id: str) -> str:
    target = op.get("target", "")
    if isinstance(target, list):
        target = target[0] if target else ""
    if target is None:
        target = ""
    target = str(target)
    if target in parent_map:
        return parent_map[target]
    norm = _normalize_label(target) if target else ""
    if norm and norm in parent_map:
        return parent_map[norm]
    for key, parent in parent_map.items():
        if key and key in target:
            return parent
    return fallback_id


def nominal_dims(seed: str, part: PartState, env) -> tuple[float, float, float]:
    x, y, z = [safe_num(v, 100) for v in env[:3]]
    text = f"{part.id} {part.label}".lower()
    if seed == "cubesat":
        if "panel" in text:
            return (x * 0.92, 3, z * 0.45)
        if "ladder" in text or "board" in text:
            return (x * 0.62, y * 0.18, z * 0.72)
        if "hinge" in text:
            return (10, 10, 22)
        return (x * 0.92, y * 0.92, z * 0.96)
    if seed == "tiltrotor":
        if "nacelle" in text:
            return (70, 44, 42)
        if "linkage" in text:
            return (28, 28, 56)
        if "battery" in text or "payload" in text:
            return (95, 42, 30)
        if "tail" in text or "gear" in text:
            return (85, 22, 36)
        return (190, 34, 42)
    if seed == "robot_arm":
        if "base" in text or "shoulder" in text:
            return (92, 92, 52)
        if "link" in text or "forearm" in text:
            return (48, 36, 150)
        if "joint" in text or "wrist" in text:
            return (54, 54, 46)
        if "tool" in text:
            return (50, 50, 28)
        return (18, 18, 230)
    if seed == "small_launch_vehicle":
        if "tank" in text:
            return (46, 46, 130)
        if "engine" in text:
            return (58, 58, 58)
        if "interstage" in text or "avionics" in text:
            return (72, 72, 36)
        if "fairing" in text or "fin" in text:
            return (76, 76, 68)
        return (84, 84, 220)
    if seed == "long_range_recon_wing":
        if "sensor" in text:
            return (78, 38, 34)
        if "payload" in text or "battery" in text:
            return (120, 46, 26)
        if "propulsion" in text or "cable" in text:
            return (90, 40, 32)
        if "wing" in text or "elevon" in text:
            return (260, 34, 20)
        return (230, 52, 32)
    return (x * 0.45, y * 0.45, z * 0.35)


# --- 공통 프리미티브 팩토리 -------------------------------------------------
# detail_parts 경로(build_detailed)와 생성물 geometry_ops 경로가 같은 형상
# 어휘(cyl/tube/cone/sphere/hex/box)를 쓰도록 단일 출처로 모은다. 이렇게 해야
# 모델이 12~24 ops를 좌표와 함께 내면 그게 detail 시드급으로 렌더링된다.
def make_primitive(kind: str, dims) -> object | None:
    """kind + 정규화 치수 dims → build123d 솔리드.
    box  : dims=(l, w, h)
    cyl  : dims=(radius, _, h)          (반지름 기준)
    tube : dims=(outer_r, inner_r, h)   (중공 원통)
    cone : dims=(bottom_r, top_r, h)
    sphere: dims=(r,)
    hex  : dims=(radius, _, h)          (육각 프리즘, 축 Z)
    """
    d = list(dims) + [0.0, 0.0, 0.0]
    try:
        if kind == "box":
            return Box(max(d[0], 0.5), max(d[1], 0.5), max(d[2], 0.5))
        if kind == "cyl":
            return Cylinder(radius=max(d[0], 0.25), height=max(d[2], 0.5))
        if kind == "tube":
            outer = max(d[0], 0.5)
            return Cylinder(radius=outer, height=max(d[2], 0.5)) - Cylinder(
                radius=max(min(d[1], outer - 0.3), 0.1), height=max(d[2], 0.5) + 2)
        if kind == "cone":
            return Cone(bottom_radius=max(d[0], 0.25), top_radius=max(d[1], 0.0), height=max(d[2], 0.5))
        if kind == "sphere":
            return Sphere(radius=max(d[0], 0.5))
        if kind == "hex":
            h = max(d[2], 0.5)
            return Pos(0, 0, -h / 2) * extrude(RegularPolygon(radius=max(d[0], 0.5), side_count=6), amount=h)
    except Exception as exc:
        logging.warning("make_primitive(%s, %s) failed: %s", kind, dims, exc)
    return None


def argf(args: dict, *names, default=None):
    """치수 키 별칭을 흡수한다. S2 프롬프트는 d_mm/h_mm/x_mm 식으로 가르치고
    일부 모델은 diameter_mm/height_mm/size_mm 로 낸다 — 둘 다 받아야
    '가르친 것=재는 것'이 형상 레벨에서 성립한다."""
    for n in names:
        if n in args and args[n] is not None:
            return safe_num(args[n], default if default is not None else 0.0)
    return default


def op_box_dims(args: dict, fallback) -> tuple[float, float, float] | None:
    """box 치수: size_mm=[l,w,h] 또는 x_mm/y_mm/z_mm 별칭."""
    sz = args.get("size_mm")
    if isinstance(sz, list) and len(sz) == 3:
        return tuple(safe_num(v, 1) for v in sz)
    x = argf(args, "x_mm", "l_mm", "length_mm")
    y = argf(args, "y_mm", "w_mm", "width_mm")
    z = argf(args, "z_mm", "h_mm", "height_mm")
    if x and y and z:
        return (x, y, z)
    return None


def op_at(op: dict) -> tuple[float, float, float] | None:
    """모델이 준 로컬 배치 좌표 args.at = [x,y,z]. 없으면 None."""
    at = op.get("args", {}).get("at")
    if isinstance(at, (list, tuple)) and len(at) == 3:
        return tuple(safe_num(v, 0.0) for v in at)
    return None


def primitive_for_op(op: dict, fallback_dims) -> tuple[object | None, tuple[float, float, float] | None, str]:
    t = op.get("op")
    args = op.get("args", {})
    if t == "box":
        dims = op_box_dims(args, fallback_dims)
        if dims:
            return make_primitive("box", dims), dims, "box"
    if t == "cylinder":
        d = argf(args, "diameter_mm", "d_mm")
        h = argf(args, "height_mm", "h_mm", "length_mm", "l_mm")
        if d and h:
            return make_primitive("cyl", (d / 2, 0, h)), (d, d, h), "cylinder"
    if t == "sphere":
        r = argf(args, "radius_mm", "r_mm")
        if r is None:
            dd = argf(args, "diameter_mm", "d_mm")
            r = dd / 2 if dd else None
        if r:
            return make_primitive("sphere", (r,)), (2 * r, 2 * r, 2 * r), "sphere"
    if t == "cone":
        rb = (argf(args, "bottom_diameter_mm", "diameter_mm", "d_mm", default=fallback_dims[0])) / 2
        rt = (argf(args, "top_diameter_mm", default=0)) / 2
        h = argf(args, "height_mm", "h_mm", "length_mm", "l_mm", default=fallback_dims[2])
        return make_primitive("cone", (rb, rt, h)), (2 * rb, 2 * rb, h), "cone"
    if t == "loft":
        h = safe_num(args.get("height_mm", args.get("length_mm")), fallback_dims[2])
        sections = args.get("sections", [])
        if not isinstance(sections, (list, tuple)):
            sections = [sections]
        diams = [safe_num(x, 0) for s in sections for x in re.findall(r"(\d+(?:\.\d+)?)\s*mm", str(s))]
        if diams:
            d = max(sum(diams) / len(diams), 1)
            return make_primitive("cyl", (d / 2, 0, h)), (d, d, h), "loft(approx)"
        return make_primitive("box", fallback_dims), fallback_dims, "loft(box-approx)"
    return None, None, ""


def feature_offset(part: PartState, op_index: int) -> tuple[float, float, float]:
    l, w, h = part.dims or (40, 40, 40)
    angle = (op_index % 8) / 8 * math.tau
    return (
        math.cos(angle) * l * 0.16,
        math.sin(angle) * w * 0.16,
        ((op_index % 5) - 2) * h * 0.08,
    )


def ensure_base(part: PartState, seed: str, env):
    if part.solid is not None and part.dims is not None:
        return
    dims = nominal_dims(seed, part, env)
    part.solid = Box(*dims)
    part.dims = dims
    part.applied.append(("fallback", "nominal-part-body"))


def apply_feature_op(part: PartState, op: dict, seed: str, env, op_index: int):
    t = op.get("op")
    args = op.get("args", {})
    ensure_base(part, seed, env)
    dims = part.dims or nominal_dims(seed, part, env)
    oid = op.get("id", f"op-{op_index}")

    # 얇은 판(min dim < 3mm) 가드: boss/engrave/pocket/channel/shell 은 슬리버→non-manifold 유발.
    # 관통 drill 만 허용(깨끗한 구멍). 나머지는 스킵해 watertight 판을 보존한다.
    THIN_PLATE_MM = 3.0
    if part.dims and min(part.dims) < THIN_PLATE_MM and t in ("boss", "engrave", "pocket", "channel", "shell"):
        part.skipped.append((oid, str(t), "skipped on thin plate to keep watertight"))
        return

    try:
        if t == "shell" and "wall_mm" in args:
            wall = safe_num(args["wall_mm"], 1.5)
            l, w, h = dims
            # 얇은 판은 shell 시 내부 박스가 표면과 일치해 non-manifold 발생 → 솔리드 유지
            MIN_WALL = 0.8
            if min(l, w, h) < 4 * wall:
                part.skipped.append((oid, "shell", "too thin to hollow safely, kept solid (watertight guard)"))
            else:
                open_faces = args.get("open_faces", [])
                ix = l + 2 if axis_open(open_faces, "X") else max(l - 2 * wall, MIN_WALL)
                iy = w + 2 if axis_open(open_faces, "Y") else max(w - 2 * wall, MIN_WALL)
                iz = h + 2 if axis_open(open_faces, "Z") else max(h - 2 * wall, MIN_WALL)
                part.solid = part.solid - Box(ix, iy, iz)
                part.applied.append((oid, "shell(hollow)"))
        elif t in ("pocket", "channel"):
            anchor = infer_anchor(op)
            width = argf(args, "width_mm", "w_mm", default=max(3, min(dims) * 0.12))
            depth = argf(args, "depth_mm", default=max(2, min(dims) * 0.08))
            if t == "channel" or anchor == "axis_Z":
                cutter = Box(width, depth, dims[2] * 1.15)
            else:
                length = argf(args, "l_mm", "length_mm", "x_mm", default=width * 4)
                height = argf(args, "h_mm", "z_mm", default=width * 2)
                cutter = Box(length, max(depth, 0.5), height)
            at = op_at(op)
            for pos in ([at] if at is not None else anchor_positions(anchor, dims)):
                part.solid = part.solid - (Pos(*pos) * cutter)
            part.applied.append((oid, t))
        elif t == "drill":
            dia = argf(args, "diameter_mm", "d_mm", default=2)
            depth = argf(args, "depth_mm")
            height = dims[2] * 1.2 if args.get("through") else (max(depth, 0.5) if depth else max(8, dims[2] * 0.25))
            cutter = Cylinder(radius=max(dia, 0.4) / 2, height=height)
            at = op_at(op)
            for pos in ([at] if at is not None else anchor_positions(infer_anchor(op), dims)):
                part.solid = part.solid - (Pos(*pos) * cutter)
            part.applied.append((oid, "drill"))
        elif t == "boss":
            dia = argf(args, "diameter_mm", "d_mm", default=5)
            height = argf(args, "height_mm", "h_mm", default=4)
            boss = Cylinder(radius=max(dia, 0.4) / 2, height=max(height, 0.5))
            at = op_at(op)
            for pos in ([at] if at is not None else anchor_positions(infer_anchor(op), dims)):
                part.solid = part.solid + (Pos(*pos) * boss)
            part.applied.append((oid, "boss"))
        elif t in ("pattern_linear", "pattern_polar"):
            count = int(safe_num(args.get("count"), 4))
            count = max(2, min(count, 12))
            for i in range(count):
                z = -dims[2] / 2 + dims[2] * (i + 1) / (count + 1)
                x = -dims[0] * 0.28 if i % 2 else dims[0] * 0.28
                marker = Box(max(2, dims[0] * 0.05), max(2, dims[1] * 0.06), max(2, dims[2] * 0.035))
                part.solid = part.solid - (Pos(x, dims[1] / 2, z) * marker)
            part.applied.append((oid, t))
        elif t == "mirror":
            # The LLM often emits mirror as an intent marker, not a concrete
            # build123d operation. Preserve the evidence without invoking
            # location-list APIs that can throw inside OCCT/build123d.
            marker = Box(max(2, dims[0] * 0.045), max(2, dims[1] * 0.045), max(2, dims[2] * 0.045))
            axis = str(args.get("axis", "X")).upper()
            if "Y" in axis:
                pos = (0, -dims[1] * 0.42, 0)
            elif "Z" in axis:
                pos = (0, 0, -dims[2] * 0.42)
            else:
                pos = (-dims[0] * 0.42, 0, 0)
            part.solid = part.solid + (Pos(*pos) * marker)
            part.applied.append((oid, "mirror(reference-marker)"))
        elif t == "engrave":
            cut = Box(min(28, dims[0] * 0.55), 0.8, min(8, dims[2] * 0.16))
            part.solid = part.solid - (Pos(dims[0] / 2, 0, 0) * cut)
            part.applied.append((oid, "engrave(approx)"))
        elif t in ("chamfer", "fillet"):
            part.deferred_edges.append(op)
        elif t == "subtract":
            # Educational cutaway: a large side bite makes internal modules visible.
            cutter = Box(dims[0] * 0.55, dims[1] * 1.4, dims[2] * 0.85)
            part.solid = part.solid - (Pos(dims[0] * 0.32, 0, 0) * cutter)
            part.applied.append((oid, "subtract(cutaway-approx)"))
        else:
            primitive, pdims, label = primitive_for_op(op, nominal_dims(seed, part, env))
            if primitive is None:
                part.skipped.append((oid, str(t), "unsupported feature op"))
                return
            pos = feature_offset(part, op_index)
            part.solid = part.solid + (Pos(*pos) * primitive)
            part.applied.append((oid, label))
    except Exception as exc:
        part.skipped.append((oid, str(t), f"feature build error: {str(exc)[:80]}"))


def place_for_seed(seed: str, part: PartState, env) -> tuple[float, float, float]:
    x, y, z = [safe_num(v, 100) for v in env[:3]]
    text = f"{part.id} {part.label}".lower()
    i = part.index
    if seed == "cubesat":
        if "panel" in text:
            # 패널 dims=(92,3,153): Y가 얇음 → ±Y 면에 부착 (spine 반폭 ~46)
            return (0, (-47 if i % 2 else 47), 0)
        if "ladder" in text or "board" in text:
            return (0, 0, 0)  # 내부 보드 셸프(중앙)
        if "hinge" in text:
            return (0, 0, z * 0.5 + 8)  # 상단 끝 근처
        return (0, 0, 0)
    if seed == "tiltrotor":
        if "nacelle" in text:
            return (0, 120, 12)
        if "linkage" in text:
            return (0, -120, 8)
        if "battery" in text or "payload" in text:
            return (0, 0, -52)
        if "tail" in text or "gear" in text:
            return (-145, 0, 8)
        return (0, 0, 0)
    if seed == "robot_arm":
        return [
            (0, 0, -120),
            (52, 0, -20),
            (96, 0, 82),
            (140, 0, 160),
            (-48, -48, 35),
        ][min(i, 4)]
    if seed == "small_launch_vehicle":
        if "tank" in text:
            return (-74, 0, 78)
        if "engine" in text:
            return (0, 0, -165)
        if "interstage" in text or "avionics" in text:
            return (72, 0, 65)
        if "fairing" in text or "fin" in text:
            return (0, 0, 205)
        return (0, 0, 0)
    if seed == "long_range_recon_wing":
        if "sensor" in text:
            return (-210, 0, 18)
        if "payload" in text or "battery" in text:
            return (0, -48, -12)
        if "propulsion" in text or "cable" in text:
            return (205, 0, 14)
        if "wing" in text or "elevon" in text:
            return (0, 52, 0)
        return (0, 0, 0)
    angle = i / 5 * math.tau
    return (math.cos(angle) * x * 0.4, math.sin(angle) * y * 0.4, 0)


def _part_box(state):
    """파트 솔리드의 (size, local_center). 솔리드가 로컬 원점 중심이 아닐 수 있으므로
    배치 시 translation = desired_center - local_center 로 보정해야 한다."""
    s = getattr(state, "solid", None)
    if s is None:
        d = getattr(state, "dims", None) or (40.0, 40.0, 40.0)
        return tuple(d), (0.0, 0.0, 0.0)
    try:
        bb = s.bounding_box()
        size = (bb.max.X - bb.min.X, bb.max.Y - bb.min.Y, bb.max.Z - bb.min.Z)
        center = ((bb.min.X + bb.max.X) / 2, (bb.min.Y + bb.max.Y) / 2, (bb.min.Z + bb.max.Z) / 2)
        return size, center
    except Exception:
        return (40.0, 40.0, 40.0), (0.0, 0.0, 0.0)


ROTARY_MATES = ("pin", "hinge", "revolute", "tilt", "pivot")
# 6면 단위 방향(+X,+Y,+Z,-X,-Y,-Z): 한 부모의 자식들을 서로 다른 면에 분기 배치.
FACE_DIRS = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (-1, 0, 0), (0, -1, 0), (0, 0, -1)]


def assembled_layout(states: dict, joints: list[dict], env, return_meta: bool = False):
    """GAP-4: joint 기반 방향성 트리 배치 (1D 일렬 대체).
    데이텀(최다 partB)에서 BFS 트리를 만들고, 각 자식을 부모의 한 '면'에 인접 배치한다.
    한 부모의 여러 자식은 서로 다른 면(FACE_DIRS)에 분기 → 실제 조립 형태(별·체인·분기 모두).
    offset = parent_half + child_half + clearance (면 법선축). containment 자식은 부모 중심.
    회전 mate(pin/hinge/revolute)는 배치 방향에 수직한 축으로 대표 전개각 회전.

    HONEST LIMIT: joint에 mate 축/면 좌표가 없어 방향은 기하 추론이다. 충돌0은 더 이상
    구조적 보장이 아니므로 assembly_interference_audit로 반드시 재검증한다(임계 완화 금지).
    한 파트가 여러 부모와 mate면 BFS 1차 부모만 만족하고 나머지는 미충족 잔차로 보고한다.

    return_meta=True 면 (layout, meta) 반환 — meta.unsatisfied_mates 잔차 포함."""
    from collections import Counter, defaultdict, deque
    ids = list(states.keys())
    if not ids:
        return ({}, {"unsatisfied_mates": []}) if return_meta else {}

    adj = defaultdict(list)
    for j in joints:
        a, b = j.get("partA"), j.get("partB")
        if a in states and b in states and a != b:
            adj[a].append((b, j))
            adj[b].append((a, j))
    deg = Counter(j.get("partB") for j in joints if j.get("partB") in states)
    datum = deg.most_common(1)[0][0] if deg else ids[0]

    # BFS 트리: 노드별 부모 + 부모 joint + 깊이
    order, seen = [datum], {datum}
    parent_of = {datum: None}
    parent_joint = {datum: None}
    depth = {datum: 0}
    q = deque([datum])
    while q:
        node = q.popleft()
        for nb, j in adj.get(node, []):
            if nb not in seen:
                seen.add(nb)
                parent_of[nb] = node
                parent_joint[nb] = j
                depth[nb] = depth[node] + 1
                order.append(nb)
                q.append(nb)
    for pid in ids:        # 그래프에서 끊긴 파트는 데이텀 자식으로
        if pid not in seen:
            parent_of[pid] = datum
            parent_joint[pid] = None
            depth[pid] = 1
            order.append(pid)

    center = {datum: [0.0, 0.0, 0.0]}
    rot = {datum: [0.0, 0.0, 0.0]}
    child_idx = defaultdict(int)
    dlong = max(_part_box(states[datum])[0]) if datum in states else 1.0

    for pid in order:
        if pid == datum:
            continue
        par = parent_of.get(pid, datum)
        j = parent_joint.get(pid) or {}
        mate = str(j.get("mate", "")).lower()
        clr = safe_num(j.get("clearance_mm"), 0.25)
        psize, _ = _part_box(states[par])
        csize, _ = _part_box(states[pid])
        pc = center.get(par, [0.0, 0.0, 0.0])

        if j.get("containment"):     # 선언된 내부 중첩 → 부모 중심
            center[pid] = list(pc)
            rot[pid] = [0.0, 0.0, 0.0]
            continue

        d = FACE_DIRS[child_idx[par] % len(FACE_DIRS)]
        child_idx[par] += 1
        axis = next(i for i, v in enumerate(d) if v != 0)
        sign = d[axis]
        off = psize[axis] / 2 + csize[axis] / 2 + clr
        c = list(pc)
        c[axis] += sign * off
        center[pid] = c

        # 회전 mate: 배치 방향에 수직한 축으로 대표 전개각(작은 파트만 — footprint 영향 제한)
        if mate in ROTARY_MATES and max(csize) < 0.5 * dlong:
            r = [0.0, 0.0, 0.0]
            r[(axis + 1) % 3] = 30.0
            rot[pid] = r
        else:
            rot[pid] = [0.0, 0.0, 0.0]

    # 간이 충돌 해소: 분기 트리는 충돌0을 구조적으로 보장하지 못한다(서로 다른 가지의
    # 큰 파트가 겹칠 수 있다). 겹친 AABB 쌍을 데이텀에서 더 먼/깊은 파트를 데이텀 반대
    # 방향(반경)으로 침투량+여유만큼 밀어 분리한다. 임계 완화가 아니라 배치를 고치는 것.
    def eff_size(pid):
        sz = list(_part_box(states[pid])[0])
        if any(rot.get(pid, [0, 0, 0])):   # 회전 파트는 보수적으로 최장변 정육면체로 본다
            m = max(sz)
            return [m, m, m]
        return sz

    # MARGIN = audit NEAR_CLEARANCE_MM(1.0): 이 간격 이상이면 AABB 비교차 → blocked 아님.
    # 핵심: '최소 침투축'으로 분리한다(가장 작은 이동으로 떼어냄). 주 반경축으로 밀면
    # 큰 침투를 한 번에 밀어 다른 파트와 새 충돌을 만들어 수렴이 안 됐다(blocked 잔존 원인).
    MARGIN = 1.0
    movable = [p for p in ids if p != datum]
    for _ in range(80):
        moved = False
        for i in range(len(movable)):
            for j in range(i + 1, len(movable)):
                a, b = movable[i], movable[j]
                sa, sb = eff_size(a), eff_size(b)
                ca, cb = center[a], center[b]
                pen = [(sa[k] + sb[k]) / 2 + MARGIN - abs(ca[k] - cb[k]) for k in range(3)]
                if min(pen) <= 0:
                    continue   # 한 축이라도 분리 → 충돌 아님
                ax = min(range(3), key=lambda k: pen[k])   # 최소 침투축 = 가장 싼 분리
                push = pen[ax] + 0.5
                s = 1.0 if ca[ax] >= cb[ax] else -1.0
                da, db = depth.get(a, 1), depth.get(b, 1)
                if da > db:                 # 더 깊은(말단) 파트를 민다
                    center[a][ax] += s * push
                elif db > da:
                    center[b][ax] -= s * push
                else:                       # 같은 깊이 → 양쪽 절반씩 (대칭, 빠른 수렴)
                    center[a][ax] += s * push / 2
                    center[b][ax] -= s * push / 2
                moved = True
        if not moved:
            break

    # 보장: 반복 후에도 충돌이 남으면(임의 치수의 어려운 케이스) 트리 배치를 버리고
    # 검증된 1D 타일링으로 폴백한다 — 최장축을 따라 일렬 배치 → AABB가 그 축에서 disjoint →
    # 충돌0 보장(원인 수리, audit 임계는 안 건드림). 큐레이트처럼 안 겹치면 트리 유지.
    def has_overlap():
        for i in range(len(movable)):
            for j in range(i + 1, len(movable)):
                a, b = movable[i], movable[j]
                sa, sb = eff_size(a), eff_size(b)
                ca, cb = center[a], center[b]
                if min((sa[k] + sb[k]) / 2 + MARGIN - abs(ca[k] - cb[k]) for k in range(3)) > 0:
                    return True
        return False
    if has_overlap():
        contained = {pid for pid in ids if (parent_joint.get(pid) or {}).get("containment")}
        main = max(range(3), key=lambda k: _part_box(states[datum])[0][k]) if datum in states else 0
        cursor = 0.0
        for pid in order:                 # containment 제외 일렬 타일링
            if pid in contained:
                continue
            size = eff_size(pid)
            c = [0.0, 0.0, 0.0]
            c[main] = cursor + size[main] / 2
            center[pid] = c
            cursor += size[main] + MARGIN
        for pid in contained:             # containment 파트는 부모 중심
            center[pid] = list(center.get(parent_of.get(pid, datum), [0.0, 0.0, 0.0]))

    # 전체 어셈블리를 원점 중심으로 평행이동
    if center:
        mean = [sum(center[p][i] for p in center) / len(center) for i in range(3)]
        for p in center:
            for i in range(3):
                center[p][i] -= mean[i]

    out = {pid: {"center": center.get(pid, [0.0, 0.0, 0.0]),
                 "rot": rot.get(pid, [0.0, 0.0, 0.0])} for pid in ids}

    if not return_meta:
        return out

    # 잔차: 한 파트가 BFS 부모 외의 파트와도 mate면 그 mate는 트리 배치로 미충족.
    unsatisfied = []
    for j in joints:
        a, b = j.get("partA"), j.get("partB")
        if a not in states or b not in states or a == b:
            continue
        if parent_of.get(a) == b or parent_of.get(b) == a:
            continue   # 트리 부모-자식 → 인접 배치됨
        unsatisfied.append({"id": j.get("id"), "part_a": a, "part_b": b,
                            "mate": j.get("mate"), "reason": "secondary mate not adjacent under BFS tree placement"})
    return out, {"datum": datum, "unsatisfied_mates": unsatisfied}


def apply_edge_finishes(part: PartState):
    if part.solid is None:
        return
    for op in part.deferred_edges:
        t = op.get("op")
        args = op.get("args", {})
        oid = op.get("id", t)
        try:
            amt = min(safe_num(args.get("amount_mm", args.get("radius_mm")), 0.6), 0.45)
            edges = part.solid.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-4:]
            if not edges:
                part.skipped.append((oid, t, "no eligible edges"))
                continue
            finished = (chamfer if t == "chamfer" else fillet)(edges, amt)
            if not hasattr(finished, "wrapped"):
                part.skipped.append((oid, t, "edge finish returned non-exportable shape list"))
                continue
            part.solid = finished
            part.applied.append((oid, t))
        except Exception as exc:
            part.skipped.append((oid, t, f"edge finish error: {str(exc)[:80]}"))


def add_fastener_holes(part: PartState, fasteners: list[dict]):
    if part.solid is None or part.dims is None:
        return 0
    # 얇은 판은 모서리 드릴이 가장자리 슬리버(non-manifold)를 만든다 → 구멍 생략
    if min(part.dims) < 3.0:
        return 0
    holes = 0
    for f in fasteners:
        joined = " ".join(f.get("joins", []))
        if part.id not in joined:
            continue
        dia = next((safe_num(x, 2) for x in re.findall(r"[\d.]+", f.get("standard", ""))), 2.0)
        hole = f.get("hole", "clearance")
        hd = dia + 0.2 if hole == "clearance" else dia - 0.4 if hole == "tap" else dia
        depth = part.dims[2] * 1.15 if hole == "through" else max(8, part.dims[2] * 0.22)
        cutter = Cylinder(radius=max(hd, 0.4) / 2, height=depth)
        for pos in anchor_positions(f.get("anchor", "corners_4"), part.dims):
            try:
                part.solid = part.solid - (Pos(*pos) * cutter)
                holes += 1
            except Exception as e:
                logging.warning("hole cut failed at %s: %s", pos, e)
    return holes


def connector_between(a, b):
    ax, ay, az = a
    bx, by, bz = b
    dx, dy, dz = bx - ax, by - ay, bz - az
    mx, my, mz = (ax + bx) / 2, (ay + by) / 2, (az + bz) / 2
    if abs(dx) >= abs(dy) and abs(dx) >= abs(dz):
        return Pos(mx, my, mz) * Box(max(abs(dx), 1), 3, 3)
    if abs(dy) >= abs(dx) and abs(dy) >= abs(dz):
        return Pos(mx, my, mz) * Box(3, max(abs(dy), 1), 3)
    return Pos(mx, my, mz) * Box(3, 3, max(abs(dz), 1))


def build_detailed(seed: str, pkg: dict):
    """detail_parts(절대 size+pos) 기반 섬세 빌드: spine shell + 내부/외부 부품."""
    dp = pkg["detail_parts"]
    sh = dp.get("spine_shell")
    solid = None
    if sh:
        L, W, H = sh.get("size_mm", [96, 96, 330])
        wall = sh.get("wall_mm", 1.8)
        openax = sh.get("open", "X")
        if sh.get("shape") == "cyl":
            # 둥근 동체(원통 외피) + 측면 컷어웨이 창(내부 가시) — 박스 동체 대신
            R = L / 2
            shell = Cylinder(radius=R, height=H) - Cylinder(radius=R - wall, height=H + 2)
            win_w = sh.get("window_w_mm", R * 1.1)
            win_h = sh.get("window_h_mm", H * 0.66)
            shell = shell - (Pos(R, 0, 0) * Box(2 * wall + 6, win_w, win_h))  # +X 관측 창
            solid = shell
        else:
            shell = Box(L, W, H)
            ix = L + 4 if openax == "X" else L - 2 * wall
            iy = W + 4 if openax == "Y" else W - 2 * wall
            iz = H + 4 if openax == "Z" else H - 2 * wall
            solid = shell - Box(ix, iy, iz)  # 외피(open 면 관통, 내부 가시)
    n = 0
    for p in dp.get("parts", []):
        x, y, z = p["pos_mm"]
        t = p.get("type", "box")
        sz = p["size_mm"]
        # cyl/tube/cone/sphere/hex/box: 공통 팩토리(make_primitive)로 단일화.
        prim = make_primitive(t if t in ("cyl", "tube", "cone", "sphere", "hex") else "box", sz)
        if prim is None:
            prim = make_primitive("box", sz)
        fr = p.get("fillet_mm")
        if fr:  # 모서리 라운드(골판지 박스 느낌 제거) — 실패 시 원본 유지
            try:
                prim = fillet(prim.edges(), radius=fr)
            except Exception as e:
                logging.warning("fillet failed (r=%s): %s", fr, e)
        rot = p.get("rot_deg")
        if rot:
            prim = Rotation(rot[0], rot[1], rot[2]) * prim
        placed = Pos(x, y, z) * prim
        solid = placed if solid is None else solid + placed
        n += 1
    solid = exportable(solid)
    out_dir = OUT / seed
    out_dir.mkdir(parents=True, exist_ok=True)
    stl_path = out_dir / f"{seed}.stl"
    export_stl(solid, str(stl_path))
    print(f"[{seed}] DETAILED STL: {stl_path.relative_to(REPO)}  volume {solid.volume:.0f} mm^3")
    print(f"  spine shell + {n} detail parts (내부 보드/배터리/페이로드 + 외부 레일/태양전지/안테나)")
    return 0


def resolve_seed_dir(seed: str, seed_dir: str | None):
    """--dir 지정 시 그 폴더(절대/REPO 상대)를, 아니면 기본 seeds/<seed>를 사용."""
    if seed_dir:
        p = Path(seed_dir)
        return p if p.is_absolute() else REPO / p
    return SEEDS / seed


def build(seed: str, seed_dir: str | None = None):
    base = resolve_seed_dir(seed, seed_dir)
    out_name = f"{seed}_generated" if seed_dir else seed
    pkg = json.loads((base / "package.json").read_text(encoding="utf-8"))
    if pkg.get("detail_parts"):
        return build_detailed(seed, pkg)
    bp = pkg["schema_v6_blueprint"]
    ops = bp.get("geometry_ops", [])
    env = bp.get("cad_brief", {}).get("envelope_mm", [100, 100, 100])
    children = root_children(bp.get("part_tree", {}))
    if not children:
        print(f"[{seed}] part_tree has no root children")
        return 1

    parent_map = build_target_parent_map(children)
    states = {
        child["id"]: PartState(child["id"], child.get("name", child["id"]), idx)
        for idx, child in enumerate(children)
        if child.get("id")
    }
    fallback_id = next(iter(states))

    for idx, op in enumerate(ops):
        pid = op_parent_id(op, parent_map, fallback_id)
        part = states.get(pid) or states[fallback_id]
        primitive, dims, label = primitive_for_op(op, nominal_dims(seed, part, env))
        t = op.get("op")
        oid = op.get("id", f"op-{idx}")
        op_target = op.get("target", "")
        if isinstance(op_target, list):
            op_target = op_target[0] if op_target else ""
        if primitive is not None and (part.solid is None or op_target == part.id):
            # 모델이 준 로컬 좌표(args.at)를 실제 배치에 반영. 없을 때만 인공 분산 폴백.
            at = op_at(op)
            pos = at if at is not None else (feature_offset(part, idx) if part.solid is not None else (0.0, 0.0, 0.0))
            piece = positioned_shape(primitive, pos)
            if piece is None:
                part.skipped.append((oid, label, "primitive placement failed"))
                continue
            part.solid = boolean_join(part.solid, piece)
            if part.dims is None:
                part.dims = dims
            part.applied.append((oid, label))
            continue
        apply_feature_op(part, op, seed, env, idx)

    asm_path = base / "assembly.json"
    fasteners = []
    joints = []
    if asm_path.exists():
        asm = json.loads(asm_path.read_text(encoding="utf-8"))
        fasteners = asm.get("fasteners", [])
        joints = asm.get("joints", [])

    placements = {}
    total_holes = 0
    final = None
    for part in states.values():
        ensure_base(part, seed, env)
        total_holes += add_fastener_holes(part, fasteners)
        apply_edge_finishes(part)
        pos = place_for_seed(seed, part, env)
        placements[part.id] = pos
        fallback_body = Box(*(part.dims or nominal_dims(seed, part, env)))
        placed = positioned_shape(part.solid, pos, fallback=fallback_body)
        if placed is None:
            part.skipped.append(("placement", "solid", "final placement failed; part omitted"))
            continue
        final = boolean_join(final, placed)

    # Add thin interface beams for visible mating relationships.
    for joint in joints:
        pa, pb = joint.get("partA"), joint.get("partB")
        if pa in placements and pb in placements:
            try:
                final = boolean_join(final, connector_between(placements[pa], placements[pb]))
            except Exception:
                pass

    if final is None:
        print(f"[{seed}] no buildable solid")
        return 1
    final = exportable(final)

    out_dir = OUT / out_name
    out_dir.mkdir(parents=True, exist_ok=True)
    stl_path = out_dir / f"{out_name}.stl"
    export_stl(final, str(stl_path))
    volume = final.volume
    applied = [(oid, name) for p in states.values() for oid, name in p.applied]
    skipped = [(p.id, oid, name, why) for p in states.values() for oid, name, why in p.skipped]
    separated = len([p for p in states.values() if p.solid is not None])

    # 지오메트리 해상도 게이트: 파트당 적용된 형상/피처 op 수가 임계 미만이면 "저해상도".
    # 임계 완화가 아니라 신호 생성 — 다음 세대가 ops를 더 내도록 loop_feedback로 압박.
    MIN_OPS_PER_PART = 4
    part_res = []
    for p in states.values():
        n = len(p.applied)
        part_res.append({"part_id": p.id, "label": p.label, "applied_ops": n,
                         "low_res": n < MIN_OPS_PER_PART})
    low_parts = [r for r in part_res if r["low_res"]]
    resolution = {
        "schema": "blueprint_geometry_resolution_v1",
        "name": out_name,
        "total_ops": len(ops),
        "parts": len(states),
        "low_res_parts": [r["part_id"] for r in low_parts],
        "min_ops_per_part": MIN_OPS_PER_PART,
        "findings": [f"geometry: part '{r['label']}' has only {r['applied_ops']} ops "
                     f"(<{MIN_OPS_PER_PART}) — add coordinate-bearing geometry_ops for service/interface detail"
                     for r in low_parts[:6]],
    }

    (out_dir / "geometry_resolution.json").write_text(
        json.dumps(resolution, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[{seed}] STL: {stl_path.relative_to(REPO)}  volume {volume:.0f} mm^3 ({'OK' if volume > 0 else 'FAIL'})")
    print(f"  root parts placed: {separated}/{len(states)}")
    print(f"  applied op/features {len(applied)}/{len(ops)}: {[name for _, name in applied[:16]]}")
    if low_parts:
        print(f"  LOW-RES parts {len(low_parts)}/{len(states)} (<{MIN_OPS_PER_PART} ops): "
              f"{[r['part_id'] for r in low_parts][:8]}")
    if total_holes:
        print(f"  fastener/interface holes: {total_holes}")
    if skipped:
        print(f"  skipped {len(skipped)}:")
        for pid, oid, name, why in skipped[:12]:
            print(f"    - {pid} {oid} {name}: {why}")
    return 0 if volume > 0 and separated >= min(3, len(states)) else 1


def parse_dir_flag(argv):
    rest = list(argv)
    seed_dir = None
    if "--dir" in rest:
        i = rest.index("--dir")
        seed_dir = rest[i + 1]
        del rest[i:i + 2]
    return rest, seed_dir


def main(argv):
    rest, seed_dir = parse_dir_flag(argv[1:])
    args = [a for a in rest if not a.startswith("--")]
    if not args:
        print("usage: python build_solid.py <seed> [--dir <package_dir>]")
        return 1
    return build(args[0], seed_dir)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
