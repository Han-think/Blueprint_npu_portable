"""
check_integrity.py — 데이터 종류 간 교차 일관성 + stale 종합 점검
==============================================================

데이터 5종(thinking·judgment_causal·part_spec·eval·preference)이 서로 모순되지 않는지,
산출물이 소스보다 오래되지(stale) 않았는지 검사한다. 진화(안전한 변화)의 무결성 보증.

사용: python check_integrity.py      (PASS/FAIL 종료코드)
"""
from __future__ import annotations
import json
import glob
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEEDS = ROOT / "seeds"
SEED_LIST = ["cubesat", "tiltrotor", "robot_arm", "small_launch_vehicle", "long_range_recon_wing", "haptic_glove"]
ONTO = json.loads((SEEDS / "_common" / "classification_ontology.json").read_text(encoding="utf-8"))
LABELS, CORES = ONTO["labels"], set(ONTO["cores"].keys())


def rows(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()] if Path(p).exists() else []


def check():
    errs, warns = [], []

    for s in SEED_LIST:
        base = SEEDS / s
        pkg = json.loads((base / "package.json").read_text(encoding="utf-8"))
        bp = pkg["schema_v6_blueprint"]
        box = {o.get("target"): o["args"].get("size_mm") for o in bp["geometry_ops"] if o["op"] == "box"}
        asm = json.loads((base / "assembly.json").read_text(encoding="utf-8")) if (base / "assembly.json").exists() else {"joints": [], "fasteners": []}

        # 1) part_spec envelope ↔ geometry_ops box
        for r in rows(base / "part_spec.jsonl"):
            src = box.get(r["part_id"])
            if src and r.get("envelope_mm") and src != r["envelope_mm"]:
                errs.append(f"{s}/part_spec {r['part_id']}: envelope {r['envelope_mm']} != geometry box {src}")
            # 3) part_spec.interfaces ↔ assembly 파트쌍
            for itf in r.get("interfaces", []):
                pair = {r["part_id"], itf["to"]}
                if not any({j["partA"], j["partB"]} == pair for j in asm["joints"]):
                    warns.append(f"{s}/part_spec {r['part_id']}→{itf['to']}: assembly joints 에 없음")

        # 2) judgment_causal.core ↔ ontology cores
        for r in rows(base / "judgment_causal.jsonl"):
            c = r.get("decision", {}).get("core")
            if c and c not in CORES:
                errs.append(f"{s}/judgment_causal: core '{c}' 미등록")

        # 4) thinking.classification ↔ ontology
        for i, r in enumerate(rows(base / "thinking.jsonl")):
            cls = r["reasoning"]["classification"]
            if cls not in LABELS:
                errs.append(f"{s}/thinking L{i+1}: classification '{cls}' 미등록")

        # 6) stale: 소스 mtime > 산출물 mtime
        srcs = [base / "package.json", base / "thinking.jsonl"]
        if (base / "assembly.json").exists():
            srcs.append(base / "assembly.json")
        src_m = max(os.path.getmtime(p) for p in srcs)
        for d in ["judgment_causal.jsonl", "part_spec.jsonl"]:
            p = base / d
            if p.exists() and os.path.getmtime(p) < src_m:
                warns.append(f"{s}/{d}: stale (소스보다 오래됨 → rebuild 필요)")

    # 5) eval / preference ↔ ontology
    for r in rows(ROOT / "train" / "blueprint_preference_dpo.jsonl"):
        m = re.search(r"classification: (\w+)", r["chosen"])
        if m and m.group(1) not in LABELS and m.group(1) not in ("over_integrate", "over_separate"):
            errs.append(f"preference: chosen classification '{m.group(1)}' 미등록")
    for f in glob.glob(str(ROOT / "eval" / "*_eval.jsonl")):
        for r in rows(f):
            if "expected_polarity" in r and r["expected_polarity"] not in ("approve", "reject", "caution", "neutral", "unknown"):
                errs.append(f"{Path(f).name}: expected_polarity '{r['expected_polarity']}' 비정상")

    print("=== Blueprint 데이터 무결성 점검 ===")
    print(f"교차 일관성 오류: {len(errs)}")
    for e in errs[:20]:
        print(f"  ✗ {e}")
    print(f"경고(stale/느슨한 정합): {len(warns)}")
    for w in warns[:20]:
        print(f"  ! {w}")
    if errs:
        print("\n[FAIL] 무결성 오류 존재")
        return 1
    print(f"\n[OK] 교차 일관성 통과" + (f" (경고 {len(warns)}건 — rebuild_all.py 권장)" if warns else " · stale 0"))
    return 0


if __name__ == "__main__":
    sys.exit(check())
