"""
build_sft.py — seed 데이터 → instruct(SFT) 학습셋 변환 + train/eval split
=========================================================================

두 소스를 instruct messages 로 변환한다 (DESIGN_MODEL_BUILDING_REALITY_AND_TREE.md 포맷):
  1. thinking.jsonl (125) — 기본 판단 (input → classification/proposal/verification)
  2. judgment_causal.jsonl (24) — 인과 판단 (objective/trade_off/decision/verification)

출력:
  20_dataset/train/blueprint_judgment_sft_train.jsonl
  20_dataset/eval/blueprint_judgment_sft_eval.jsonl   (held-out)

비파괴: 원본 seed 파일 미변경. classification 은 온톨로지 core 를 함께 부착.
"""
from __future__ import annotations
import json
import glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEEDS = ROOT / "seeds"
TRAIN = ROOT / "train"
EVAL = ROOT / "eval"
ONTO = json.loads((SEEDS / "_common" / "classification_ontology.json").read_text(encoding="utf-8"))["labels"]

SYSTEM = ("You are a Blueprint design-judgment assistant. "
          "Read existing structure, problem, and constraint. "
          "Preserve service access and datum visibility. "
          "Output schema-aware judgment: classification(core), rule, proposal, retained_access, verification. "
          "Keep advanced/aerospace topics at educational mockup level.")

EVAL_EVERY = 5   # seed당 5번째 row 를 held-out (80/20)


def core_of(label: str) -> str:
    return ONTO.get(label, {}).get("core", "UNMAPPED")


def from_thinking(row: dict) -> dict:
    inp, rea, out = row["input"], row["reasoning"], row["output"]
    user = (f"Target: {row['target']}\nMetric: {row['metric']}\n"
            f"Existing structure: {inp['existing_structure']}\n"
            f"Problem: {inp['problem']}\nConstraint: {inp['constraint']}")
    cls = rea["classification"]
    assistant = json.dumps({
        "classification": cls, "core": core_of(cls),
        "rule": rea.get("rule", ""),
        "proposal": out.get("proposal", ""),
        "retained_access": out.get("retained_access", []),
        "verification": out.get("verification", []),
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant},
    ]}


def from_causal(row: dict) -> dict:
    obj, tr, dec = row["objective"], row["trade_off"], row["decision"]
    user = (f"Target: {row['target']}\nObjective: {obj['metric']} — {obj.get('definition','')}\n"
            f"Failure rule: {obj.get('failure_rule','')}\nConstraint: {row.get('constraint','')}")
    assistant = json.dumps({
        "decision_core": dec.get("core", ""), "rationale": dec.get("rationale", ""),
        "trade_off": {"gain": tr.get("gain", ""), "guardrail": tr.get("guardrail", ""),
                      "cost_if_violated": tr.get("cost_if_violated", "")},
        "verification": row.get("verification", []),
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant},
    ]}


PARTSPEC_SYSTEM = ("You are a Blueprint part-design assistant. "
                   "Given a part and its assembly context, output a concrete, printable part spec: "
                   "envelope_mm, material, process, interfaces (mate, fastener std/qty, clearance, face), "
                   "print orientation, tolerances. Concrete dimensions, not vague description.")


def from_partspec(row: dict) -> dict:
    ifaces = row.get("interfaces", [])
    iface_txt = "; ".join(
        f"{i['to']} ({i['mate']}"
        + (f", {i['fastener']['std']}×{i['fastener']['qty']}" if i.get("fastener") else "")
        + (f", clr {i['clearance_mm']}mm" if i.get("clearance_mm") is not None else "")
        + ")" for i in ifaces) or "none"
    user = (f"Target: {row['target']}\nPart: {row['part_id']} — {row['name']}\n"
            f"Material: {row.get('material','')} / {row.get('process','')}\n"
            f"Interfaces with: {iface_txt}\n"
            f"Service access to preserve: {', '.join(row.get('service_access_preserved', [])) or 'n/a'}\n"
            f"Output the concrete part spec.")
    assistant = json.dumps({
        "envelope_mm": row.get("envelope_mm"),
        "material": row.get("material"), "process": row.get("process"), "qty": row.get("qty"),
        "interfaces": row.get("interfaces"),
        "print": row.get("print"), "tolerances_mm": row.get("tolerances_mm"),
        "verify": row.get("verify", []),
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": PARTSPEC_SYSTEM},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant},
    ]}


def main() -> int:
    train, evald = [], []
    n_think = n_causal = 0
    for f in sorted(glob.glob(str(SEEDS / "*" / "thinking.jsonl"))):
        for i, l in enumerate(open(f, encoding="utf-8")):
            if not l.strip():
                continue
            ex = from_thinking(json.loads(l))
            (evald if i % EVAL_EVERY == EVAL_EVERY - 1 else train).append(ex)
            n_think += 1
    for f in sorted(glob.glob(str(SEEDS / "*" / "judgment_causal.jsonl"))):
        for l in open(f, encoding="utf-8"):
            if l.strip():
                train.append(from_causal(json.loads(l)))
                n_causal += 1

    # ── part_spec → 구체 도안 instruct (별도 셋) ──
    ps_train, ps_eval = [], []
    n_ps = 0
    for f in sorted(glob.glob(str(SEEDS / "*" / "part_spec.jsonl"))):
        for i, l in enumerate(open(f, encoding="utf-8")):
            if not l.strip():
                continue
            ex = from_partspec(json.loads(l))
            (ps_eval if i % EVAL_EVERY == EVAL_EVERY - 1 else ps_train).append(ex)
            n_ps += 1

    TRAIN.mkdir(parents=True, exist_ok=True)
    EVAL.mkdir(parents=True, exist_ok=True)
    out_tr = TRAIN / "blueprint_judgment_sft_train.jsonl"
    out_ev = EVAL / "blueprint_judgment_sft_eval.jsonl"
    out_tr.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in train) + "\n", encoding="utf-8")
    out_ev.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in evald) + "\n", encoding="utf-8")
    ps_tr = TRAIN / "blueprint_partspec_sft_train.jsonl"
    ps_ev = EVAL / "blueprint_partspec_sft_eval.jsonl"
    ps_tr.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in ps_train) + "\n", encoding="utf-8")
    ps_ev.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in ps_eval) + "\n", encoding="utf-8")

    print(f"SFT 변환 완료 (instruct messages)")
    print(f"  judgment: thinking {n_think} + causal {n_causal} → train {len(train)} / eval {len(evald)}")
    print(f"  part_spec(구체도안): {n_ps} → train {len(ps_train)} / eval {len(ps_eval)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
