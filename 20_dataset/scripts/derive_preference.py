"""
derive_preference.py — 공학 트레이드오프 선호쌍(DPO) 생성
========================================================

공학적 사고 ⑤ "비교/대안 선택" 을 학습한다. 손작업 0 — 기존 thinking 에서 derive.
같은 seed 안에서 approve(좋은 설계) ↔ reject/fail(나쁜 설계) 을 주제(키워드) 매칭으로 짝짓는다.

출력: 20_dataset/train/blueprint_preference_dpo.jsonl
  {"prompt": 요구/제약, "chosen": 좋은 판단, "rejected": 나쁜 판단, "target", "topic"}

사용: python derive_preference.py [--all 기본]
"""
from __future__ import annotations
import json
import glob
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEEDS = ROOT / "seeds"
ONTO = json.loads((SEEDS / "_common" / "classification_ontology.json").read_text(encoding="utf-8"))["labels"]
STOP = set("the a an of to in for and or with into is be must stay remain can may if after before "
           "from on at by as not no out up its their this that than then keep make takes need".split())


def polarity(cls):
    return ONTO.get(cls, {}).get("polarity", "?")


def toks(*parts):
    words = re.findall(r"[a-z0-9]+", " ".join(parts).lower())
    return {w for w in words if w not in STOP and len(w) > 2}


def jaccard(a, b):
    return len(a & b) / len(a | b) if (a | b) else 0.0


def render(row):
    o, rr = row["output"], row["reasoning"]
    return (f"classification: {rr['classification']}\n"
            f"rule: {rr.get('rule','')}\n"
            f"proposal: {o.get('proposal','')}\n"
            f"retained_access: {', '.join(o.get('retained_access', [])) or 'none'}\n"
            f"verification: {'; '.join(o.get('verification', [])) or 'none'}")


def naive_opposite(row, direction):
    """constraint 를 무시한 naive 반대 판단(나쁜 설계) 텍스트 생성."""
    es = row["input"]["existing_structure"]; co = row["input"]["constraint"]
    if direction == "over_integrate":
        return (f"classification: over_integrate (naive)\n"
                f"rule: fuse everything for fewer parts, ignore the constraint\n"
                f"proposal: fuse {es} into one closed body, ignoring '{co}'\n"
                f"retained_access: none\nverification: none")
    return (f"classification: over_separate (naive)\n"
            f"rule: keep everything separate to avoid any risk\n"
            f"proposal: leave {es} as many separate parts with extra fasteners\n"
            f"retained_access: redundant\nverification: none")


def build():
    pairs = []
    for f in sorted(glob.glob(str(SEEDS / "*" / "thinking.jsonl"))):
        rows = [json.loads(l) for l in open(f, encoding="utf-8") if l.strip()]
        for row in rows:
            pol = polarity(row["reasoning"]["classification"])
            if pol == "approve":
                direction = "over_separate"      # 통합이 옳음 → naive 과분리가 나쁨
            elif pol in ("reject", "caution"):
                direction = "over_integrate"      # 분리/주의가 옳음 → naive 과통합이 나쁨
            else:
                continue                          # neutral 은 트레이드오프 축이 모호 → skip
            prompt = (f"Target: {row['target']}\nMetric: {row['metric']}\n"
                      f"Existing: {row['input']['existing_structure']}\n"
                      f"Problem: {row['input']['problem']}\nConstraint: {row['input']['constraint']}\n"
                      f"Give the design judgment that best balances integration and serviceability.")
            pairs.append({
                "schema": "blueprint_preference_v1",
                "target": row["target"],
                "axis": "integration_vs_serviceability",
                "prompt": prompt,
                "chosen": render(row),                       # 데이터의 올바른 판단
                "rejected": naive_opposite(row, direction),  # constraint 무시한 naive 반대
            })
    out = ROOT / "train" / "blueprint_preference_dpo.jsonl"
    out.write_text("\n".join(json.dumps(p, ensure_ascii=False) for p in pairs) + "\n", encoding="utf-8")
    print(f"preference pairs(DPO): {len(pairs)} → {out.relative_to(ROOT.parent)}")
    byseed = {}
    for p in pairs:
        byseed[p["target"]] = byseed.get(p["target"], 0) + 1
    for k, v in byseed.items():
        print(f"  {k}: {v} pairs")
    return 0


if __name__ == "__main__":
    raise SystemExit(build())
