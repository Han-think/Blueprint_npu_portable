"""
build_drawing.py — 2D 도면(SVG)
================================
detail_parts 있으면 각 부품을 top(XY)/front(XZ)/side(YZ) 3면에 투영(실제 배치도).
없으면 cad_brief envelope 기반 외형 박스(fallback).

사용: python build_drawing.py <seed>
출력: 10_execution/cad/output/<seed>/<seed>_drawing.svg
"""
from __future__ import annotations
import sys
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SEEDS = REPO / "20_dataset" / "seeds"
OUT = Path(__file__).resolve().parent / "output"
ROLE_COLOR = {"internal": "#9fd3ff", "external": "#89ffa8", "structure": "#ffd39f"}


def part_rect(p):
    """부품 → (cx,cy,cz, lx,ly,lz) 중심+치수 (원형류는 직경 박스 근사)."""
    x, y, z = p["pos_mm"]
    t = p.get("type", "box"); sz = p["size_mm"]
    if t in ("cyl", "tube"):
        r = sz[0]; h = sz[2]
        return _rot(p, x, y, z, 2 * r, 2 * r, h)
    if t == "cone":
        r = max(sz[0], sz[1]); h = sz[2]
        return _rot(p, x, y, z, 2 * r, 2 * r, h)
    if t == "hex":
        r = sz[0]; h = sz[2]
        return _rot(p, x, y, z, 2 * r, 2 * r, h)
    if t == "sphere":
        d = 2 * sz[0]
        return _rot(p, x, y, z, d, d, d)
    l, w, h = sz
    return _rot(p, x, y, z, l, w, h)


def _rot(p, x, y, z, lx, ly, lz):
    """rot_deg ±90° 근사: 축 범위 스왑 (투영용)."""
    rot = p.get("rot_deg")
    if rot:
        rx, ry, rz = rot
        if abs(ry) == 90:   # Z<->X
            lx, lz = lz, lx
        if abs(rx) == 90:   # Z<->Y
            ly, lz = lz, ly
        if abs(rz) == 90:   # X<->Y
            lx, ly = ly, lx
    return x, y, z, lx, ly, lz


def draw_projection(parts, env, name, rev, mat):
    # 3 view: (라벨, 가로축idx, 세로축idx) — 0:X 1:Y 2:Z
    views = [("TOP (X-Y)", 0, 1), ("FRONT (X-Z)", 0, 2), ("SIDE (Y-Z)", 1, 2)]
    # 전체 bbox
    pr = [part_rect(p) for p in parts]
    def axis_range(ai):
        lo = min(c[ai] - c[3+ai]/2 for c in pr); hi = max(c[ai] + c[3+ai]/2 for c in pr)
        return lo, hi
    rng = [axis_range(i) for i in range(3)]
    SCALE = 0.55; GAP = 40; MARGIN = 40; TOP = 56
    svg = []
    x_cursor = MARGIN
    panel_h = 0
    for label, ha, va in views:
        lo_h, hi_h = rng[ha]; lo_v, hi_v = rng[va]
        w = (hi_h - lo_h) * SCALE; h = (hi_v - lo_v) * SCALE
        panel_h = max(panel_h, h)
        ox, oy = x_cursor, TOP
        svg.append(f'<rect x="{ox}" y="{oy}" width="{w:.0f}" height="{h:.0f}" fill="#0c1e35" stroke="#274a79"/>')
        svg.append(f'<text x="{ox}" y="{oy-6}" font-size="12" fill="#9fd3ff" font-weight="bold">{label}</text>')
        for p, c in zip(parts, pr):
            ch, cv, lh, lv = c[ha], c[va], c[3+ha], c[3+va]
            rx = ox + (ch - lh/2 - lo_h) * SCALE
            ry = oy + (hi_v - (cv + lv/2)) * SCALE   # Y 뒤집기
            rw, rh = lh*SCALE, lv*SCALE
            col = ROLE_COLOR.get(p.get("role"), "#cfd6e6")
            svg.append(f'<rect x="{rx:.1f}" y="{ry:.1f}" width="{rw:.1f}" height="{rh:.1f}" '
                       f'fill="{col}" fill-opacity="0.18" stroke="{col}" stroke-width="0.8"/>')
        x_cursor = ox + w + GAP
    total_w = x_cursor + MARGIN
    total_h = TOP + panel_h + 40
    head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w:.0f}" height="{total_h:.0f}" '
            f'viewBox="0 0 {total_w:.0f} {total_h:.0f}"><rect width="100%" height="100%" fill="#f7f9fb"/>'
            f'<rect width="100%" height="100%" fill="#0a1626"/>'
            f'<text x="{MARGIN}" y="24" font-size="13" fill="#9fd3ff" font-weight="bold">'
            f'{name} rev {rev} · {mat} · {len(parts)} parts · 배치 투영도</text>')
    legend = (f'<text x="{MARGIN}" y="{total_h-14:.0f}" font-size="10" fill="#8ba3c7">'
              f'<tspan fill="#9fd3ff">■</tspan>internal '
              f'<tspan fill="#89ffa8">■</tspan>external '
              f'<tspan fill="#ffd39f">■</tspan>structure · 치수선 없는 배치 투영</text>')
    return head + "".join(svg) + legend + "</svg>"


def draw_envelope(env, name, rev, mat):
    X, Y, Z = env[0], env[1], env[2]; S = 0.7; M = 40; G = 50
    parts = []; x = M
    for lbl, wmm, hmm in [("TOP", X, Y), ("FRONT", X, Z), ("SIDE", Y, Z)]:
        w, h = wmm*S, hmm*S
        parts.append(f'<rect x="{x}" y="60" width="{w:.0f}" height="{h:.0f}" fill="none" stroke="#1b3a5b" stroke-width="1.5"/>'
                     f'<text x="{x}" y="52" font-size="12" fill="#1b3a5b">{lbl} {wmm:.0f}×{hmm:.0f}</text>')
        x += w + G
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{x+M:.0f}" height="{60+max(Y,Z)*S+40:.0f}">'
            f'<rect width="100%" height="100%" fill="#f7f9fb"/>'
            f'<text x="{M}" y="28" font-size="13" fill="#1b3a5b">{name} · envelope {X}×{Y}×{Z}</text>'
            + "".join(parts) + "</svg>")


def draw(seed):
    pkg = json.loads((SEEDS / seed / "package.json").read_text(encoding="utf-8"))
    cad = pkg["schema_v6_blueprint"]["cad_brief"]
    env = cad.get("envelope_mm", [100, 100, 100])
    name = cad.get("name", seed); rev = cad.get("rev", ""); mat = cad.get("material", "")
    dp = pkg.get("detail_parts")
    parts = (dp.get("parts") if isinstance(dp, dict) else None) or []
    if parts:
        svg = draw_projection(parts, env, name, rev, mat)
        mode = f"투영도 {len(parts)} parts"
    else:
        svg = draw_envelope(env, name, rev, mat); mode = "envelope"
    out_dir = OUT / seed; out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{seed}_drawing.svg"
    out.write_text(svg, encoding="utf-8")
    print(f"[{seed}] 2D: {out.relative_to(REPO)} ({mode})")
    return 0


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args:
        print("사용: python build_drawing.py <seed>"); return 1
    return draw(args[0])


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
