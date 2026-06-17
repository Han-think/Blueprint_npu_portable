"""Simulate Minimal.html's part->subsystem token matching for every curated seed.

Reads BOM part labels+specs out of Minimal.html and scores them against
packs/<seed>/skeleton.json exactly like matchSubsystemForPart() (>=2 token
overlap on label+spec vs id+discipline+function+evidence_features).

Usage: python check_taxonomy_match.py
"""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HTML = (REPO / "10_execution" / "ui" / "Minimal.html").read_text(encoding="utf-8")

VEHICLES = {
    "long_range_recon_wing": "wing_long_range",
    "tiltrotor": "tiltrotor_vtol",
    "cubesat": "cubesat_3u",
    "small_launch_vehicle": "small_launch_vehicle",
    "robot_arm": "arm_6dof",
    "haptic_glove": "haptic_glove_pair",
}

PART_RE = re.compile(r"label:'([^']+)',\s*preset:\[[^\]]+\],\s*spec:'([^']*)'")


def tokens(s: str) -> set[str]:
    return {w for w in re.split(r"[^a-z0-9]+", s.lower().replace("_", " ")) if len(w) >= 3}


def main() -> int:
    misses = 0
    for seed, vid in VEHICLES.items():
        i = HTML.find(f"id:'{vid}'")
        # 해당 vehicle의 parts:[ ... ] 블록만 정확히 잘라낸다 (이웃 템플릿 침범 방지)
        ps = HTML.find("parts: [", i)
        depth, j = 0, ps + len("parts: ")
        while j < len(HTML):
            if HTML[j] == "[":
                depth += 1
            elif HTML[j] == "]":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        parts = PART_RE.findall(HTML[ps:j + 1])
        sk_path = REPO / "20_dataset" / "packs" / seed / "skeleton.json"
        sk = json.loads(sk_path.read_text(encoding="utf-8"))
        print(f"== {seed} ({len(parts)} BOM parts)")
        for label, spec in parts:
            pt = tokens(f"{label} {spec}")
            best, score = None, 0
            for s in sk["required_subsystems"]:
                st = tokens(f"{s['id']} {s['discipline']} {s['function']} {' '.join(s['evidence_features'])}")
                sc = sum(1 for t in st if t in pt)
                if sc > score:
                    best, score = s["id"], sc
            ok = score >= 2
            if not ok:
                misses += 1
            print(f"  {'OK  ' if ok else 'MISS'} {label:36s} -> {best} ({score})")
    print(f"\ntotal misses: {misses}")
    return 0 if misses == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
