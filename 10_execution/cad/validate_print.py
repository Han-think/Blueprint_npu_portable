"""
validate_print.py -- pre-print safety gate for exported part STLs
=================================================================

Checks every STL in output/<seed>/print/ before anything is sliced:

  - parses binary STL (struct, no extra deps)
  - watertight/manifold: every edge shared by exactly two triangles
  - positive enclosed volume (signed tetrahedron sum)
  - bed fit against a configurable printer envelope
  - degenerate triangle ratio

Any failed check flags the part "do_not_print". Results land in
output/<seed>/print/print_readiness.json. This is a mesh sanity gate,
not a slicer or certification tool.

Usage:
    python validate_print.py <seed> [--bed 220x220x250] | --all
"""
from __future__ import annotations

import json
import struct
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "10_execution" / "cad" / "output"
SEED_LIST = ["cubesat", "tiltrotor", "robot_arm", "small_launch_vehicle",
             "long_range_recon_wing", "haptic_glove"]
DEFAULT_BED = (220.0, 220.0, 250.0)


def read_binary_stl(path: Path):
    data = path.read_bytes()
    if len(data) < 84:
        raise ValueError("file too small for binary STL")
    (n_tri,) = struct.unpack_from("<I", data, 80)
    expected = 84 + n_tri * 50
    if len(data) < expected:
        raise ValueError(f"truncated STL: {len(data)} bytes, expected {expected}")
    tris = []
    off = 84
    for _ in range(n_tri):
        vals = struct.unpack_from("<12f", data, off)
        tris.append((vals[3:6], vals[6:9], vals[9:12]))
        off += 50
    return tris


def vkey(v):
    return (round(v[0], 4), round(v[1], 4), round(v[2], 4))


def analyze(path: Path, bed):
    tris = read_binary_stl(path)
    edge_count = defaultdict(int)
    vol6 = 0.0
    mins = [float("inf")] * 3
    maxs = [float("-inf")] * 3
    degenerate = 0
    for a, b, c in tris:
        ka, kb, kc = vkey(a), vkey(b), vkey(c)
        if ka == kb or kb == kc or ka == kc:
            degenerate += 1
            continue
        for e in ((ka, kb), (kb, kc), (kc, ka)):
            edge_count[tuple(sorted(e))] += 1
        vol6 += (a[0] * (b[1] * c[2] - c[1] * b[2])
                 - a[1] * (b[0] * c[2] - c[0] * b[2])
                 + a[2] * (b[0] * c[1] - c[0] * b[1]))
        for v in (a, b, c):
            for i in range(3):
                mins[i] = min(mins[i], v[i])
                maxs[i] = max(maxs[i], v[i])
    bad_edges = sum(1 for n in edge_count.values() if n != 2)
    size = [maxs[i] - mins[i] for i in range(3)]
    volume = abs(vol6) / 6.0
    checks = {
        "watertight": bad_edges == 0,
        "positive_volume": volume > 1.0,
        "bed_fit": all(size[i] <= bed[i] + 1e-6 for i in range(3)),
        "low_degenerate": degenerate <= max(2, len(tris) * 0.005),
    }
    return {
        "file": path.name,
        "triangles": len(tris),
        "size_mm": [round(s, 1) for s in size],
        "volume_mm3": round(volume, 0),
        "non_manifold_edges": bad_edges,
        "degenerate_triangles": degenerate,
        "checks": checks,
        "do_not_print": not all(checks.values()),
    }


def validate_seed(seed: str, bed) -> int:
    pdir = OUT / seed / "print"
    if not pdir.is_dir():
        print(f"[{seed}] no print/ folder — run export_print_parts.py first")
        return 1
    results = []
    for stl in sorted(pdir.glob("*.stl")):
        try:
            results.append(analyze(stl, bed))
        except Exception as exc:
            results.append({"file": stl.name, "error": str(exc), "do_not_print": True,
                            "checks": {}})
    blocked = [r for r in results if r.get("do_not_print")]
    report = {
        "schema": "blueprint_print_readiness_v1",
        "seed": seed,
        "bed_mm": list(bed),
        "verdict": "ok_to_print" if not blocked else "blocked",
        "parts": results,
    }
    (pdir / "print_readiness.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[{seed}] {report['verdict']} · {len(results) - len(blocked)}/{len(results)} parts pass")
    for r in blocked:
        why = r.get("error") or ", ".join(k for k, v in r.get("checks", {}).items() if not v)
        print(f"  DO NOT PRINT {r['file']}: {why}")
    return 0 if not blocked else 1


def main(argv):
    args = [a for a in argv[1:] if a]
    bed = DEFAULT_BED
    if "--bed" in args:
        i = args.index("--bed")
        bed = tuple(float(x) for x in args[i + 1].lower().split("x"))
        del args[i:i + 2]
    if not args:
        print("usage: python validate_print.py <seed> [--bed 220x220x250] | --all")
        return 1
    seeds = SEED_LIST if args[0] == "--all" else [args[0]]
    rc = 0
    for seed in seeds:
        rc |= validate_seed(seed, bed)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
