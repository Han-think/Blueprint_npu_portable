"""
train_lora.py -- QLoRA fine-tune the STUDENT model from curated corpus
======================================================================

Trains a small 7B student (default qwen2.5:7b-instruct) on the disk-persisted
curation corpus (30_model/curation/curation_log.jsonl). keep rows = positive
targets, reject rows = patterns to avoid. The 20B model stays the TEACHER
(generation + judging); the student gets cheaper/faster on THIS domain.

DATA-GATED: refuses to train until the corpus has enough rows.
  - trial threshold  : 300 rows  (smoke-test a LoRA)
  - full  threshold  : 1000 rows (real run)
Run with --force to override (not recommended below trial).

Corpus row format (already produced by serve.py /persist-curation):
  {"messages":[{role:system},{role:user},{role:assistant}], "decision":"keep|reject", ...}

Usage:
  python train_lora.py                 # dry-run gate check (safe, no training)
  python train_lora.py --train         # train if >= trial threshold
  python train_lora.py --train --force # train regardless (debug)

Requires (only when actually training): transformers, peft, datasets,
bitsandbytes, accelerate. The gate check needs none of them.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CORPUS = REPO / "30_model" / "curation" / "curation_log.jsonl"
REVERSE_LOG = REPO / "30_model" / "curation" / "reverse_log.jsonl"
OUT_DIR = REPO / "30_model" / "lora_out"

TRIAL_THRESHOLD = 300
FULL_THRESHOLD = 1000
DEFAULT_BASE = "Qwen/Qwen2.5-7B-Instruct"   # 학생 모델 (HF id). Ollama qwen2.5:7b 와 동계열.


def load_rows():
    if not CORPUS.exists():
        return []
    rows = []
    for line in CORPUS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows


def load_reverse_rows():
    if not REVERSE_LOG.exists():
        return []
    rows = []
    for line in REVERSE_LOG.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
    return rows


SFT_SYSTEM = ("You are Blueprint XPU. Given a design brief and subsystem context, output a "
              "schema_v6 engineering blueprint as raw JSON: part_tree, coordinate-bearing "
              "geometry_ops, cad_brief, verify, risk. No prose.")


def row_seed(row):
    return (row.get("seed") or (row.get("input_context") or {}).get("seed")
            or row.get("vehicle_id") or "unknown")


def record_to_messages(row):
    """serve.py /persist-curation 이 쓰는 큐레이션 레코드 → (system,user,assistant).
    레코드엔 보통 messages가 없고 payload(번들/블루프린트)만 있다. 관대하게 유도한다.
    포맷이 바뀌면 `--inspect` 로 첫 행을 보고 이 함수만 고치면 된다."""
    if isinstance(row.get("messages"), list) and row["messages"]:
        return row["messages"]
    payload = row.get("payload") or {}
    design = (payload.get("schema_v6_blueprint")
              or ({"parts": [p.get("blueprint") for p in payload["parts"] if p.get("blueprint")]}
                  if isinstance(payload.get("parts"), list) else None)
              or (payload if payload else None))
    if not design:
        return []
    vehicle = payload.get("vehicle") or {}
    brief = (vehicle.get("desc") or vehicle.get("label") or row.get("title")
             or f"Design the {row_seed(row)} assembly.")
    user = f"Design brief: {brief}\nSeed: {row_seed(row)}\nOutput the schema_v6 blueprint JSON."
    return [
        {"role": "system", "content": SFT_SYSTEM},
        {"role": "user", "content": user},
        {"role": "assistant", "content": json.dumps(design, ensure_ascii=False)},
    ]


def corpus_summary(rows, reverse_rows=None):
    keep = sum(1 for r in rows if str(r.get("decision")).lower() == "keep")
    reject = sum(1 for r in rows if str(r.get("decision")).lower() == "reject")
    hold = sum(1 for r in rows if str(r.get("decision")).lower() == "hold")
    grades = {"A": 0, "B": 0, "C": 0}
    by_seed = {}
    for r in rows:
        s = row_seed(r)
        by_seed[s] = by_seed.get(s, 0) + 1
        g = (r.get("engineering_scorecard") or {}).get("grade")
        if g in grades:
            grades[g] += 1
    rev_count = len(reverse_rows) if reverse_rows else 0
    rev_tasks = {}
    if reverse_rows:
        for r in reverse_rows:
            t = r.get("task", "?")
            rev_tasks[t] = rev_tasks.get(t, 0) + 1
    return {"total": len(rows), "keep": keep, "reject": reject, "hold": hold,
            "grades": grades, "by_seed": by_seed,
            "reverse": rev_count, "reverse_tasks": rev_tasks}


GRADE_REPEAT = {"A": 3, "B": 2, "C": 1}


def to_chat_example(row):
    """keep = 정답 메시지 (grade별 반복 가중치). reject = 회피 학습."""
    msgs = record_to_messages(row)
    decision = str(row.get("decision")).lower()
    grade = (row.get("engineering_scorecard") or {}).get("grade")
    if decision == "reject":
        msgs = [{"role": "system",
                 "content": (msgs[0]["content"] if msgs and msgs[0]["role"] == "system" else "")
                 + "\n[CURATION] The following assistant output was REJECTED by engineering review - avoid this pattern."}] + \
               [m for m in msgs if m["role"] != "system"]
    repeat = GRADE_REPEAT.get(grade, 1) if decision == "keep" else 1
    return {"messages": msgs, "grade": grade, "repeat": repeat}


VAL_PER_SEED = 2


def split_train_val(rows):
    """Seed-stratified split: last VAL_PER_SEED keep rows per seed → val, rest → train."""
    by_seed = {}
    for r in rows:
        s = row_seed(r)
        by_seed.setdefault(s, []).append(r)
    train, val = [], []
    for s, seed_rows in by_seed.items():
        keeps = [r for r in seed_rows if str(r.get("decision")).lower() == "keep"]
        others = [r for r in seed_rows if str(r.get("decision")).lower() != "keep"]
        if len(keeps) > VAL_PER_SEED:
            val.extend(keeps[-VAL_PER_SEED:])
            train.extend(keeps[:-VAL_PER_SEED])
        else:
            train.extend(keeps)
        train.extend(others)
    return train, val


def gate_check(rows, force):
    rev_rows = load_reverse_rows()
    s = corpus_summary(rows, rev_rows)
    g = s["grades"]
    _, val = split_train_val(rows)
    print(f"[corpus] total {s['total']} | keep {s['keep']} (A:{g['A']} B:{g['B']} C:{g['C']}) "
          f"| reject {s['reject']} | hold {s['hold']} | val holdout {len(val)}")
    if s["reverse"]:
        print(f"[corpus] reverse: {s['reverse']} analyses {s['reverse_tasks']}")
    print(f"[corpus] by_seed {s['by_seed']}")
    trainable = s["keep"] + s["reject"]
    if trainable >= FULL_THRESHOLD:
        print(f"[gate] {trainable} trainable rows >= full threshold ({FULL_THRESHOLD}) - ready for a real run.")
        return True
    if trainable >= TRIAL_THRESHOLD:
        print(f"[gate] {trainable} trainable rows >= trial threshold ({TRIAL_THRESHOLD}) - OK for a smoke-test LoRA.")
        return True
    if force:
        print(f"[gate] below trial ({trainable}/{TRIAL_THRESHOLD}) but --force given.")
        return True
    print(f"[gate] NOT ENOUGH DATA: {trainable}/{TRIAL_THRESHOLD} (trial). "
          f"Need {TRIAL_THRESHOLD - trainable} more keep/reject rows.")
    return False


def train(rows, base_model):
    try:
        from datasets import Dataset
        from transformers import (AutoModelForCausalLM, AutoTokenizer,
                                   BitsAndBytesConfig, TrainingArguments)
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        from trl import SFTTrainer
        import torch
    except ImportError as e:
        print(f"[deps] install training deps first: pip install transformers peft datasets "
              f"bitsandbytes accelerate trl  ({e})")
        return 1

    train_rows, val_rows = split_train_val(rows)
    trainable = [r for r in train_rows if str(r.get("decision")).lower() in ("keep", "reject")
                 and record_to_messages(r)]
    val_eligible = [r for r in val_rows if record_to_messages(r)]
    if not trainable:
        print("[data] no trainable examples could be built from the corpus (check --inspect).")
        return 1
    examples = []
    for r in trainable:
        ex = to_chat_example(r)
        for _ in range(ex.pop("repeat", 1)):
            examples.append({"messages": ex["messages"]})
    # reverse analysis examples (역설계 분석 데이터)
    rev_rows = load_reverse_rows()
    rev_count = 0
    for r in rev_rows:
        msgs = r.get("messages")
        if msgs and len(msgs) >= 3:
            examples.append({"messages": msgs})
            rev_count += 1
    val_examples = [{"messages": to_chat_example(r)["messages"]} for r in val_eligible]
    print(f"[data] {len(trainable)} forward + {rev_count} reverse -> {len(examples)} training examples "
          f"(grade-A x3, B x2, C x1) + {len(val_examples)} val")
    ds = Dataset.from_list(examples)
    ds_val = Dataset.from_list(val_examples) if val_examples else None

    tok = AutoTokenizer.from_pretrained(base_model)
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                             bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True)
    model = AutoModelForCausalLM.from_pretrained(base_model, quantization_config=bnb, device_map="auto")
    model = prepare_model_for_kbit_training(model)
    lora = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, bias="none",
                      task_type="CAUSAL_LM",
                      target_modules=["q_proj", "k_proj", "v_proj", "o_proj"])
    model = get_peft_model(model, lora)

    def fmt(ex):
        return {"text": tok.apply_chat_template(ex["messages"], tokenize=False, add_generation_prompt=False)}
    ds = ds.map(fmt)
    if ds_val:
        ds_val = ds_val.map(fmt)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    eval_strategy = "steps" if ds_val else "no"
    args = TrainingArguments(output_dir=str(OUT_DIR), num_train_epochs=2,
                             per_device_train_batch_size=1, gradient_accumulation_steps=8,
                             learning_rate=2e-4, fp16=True, logging_steps=10, save_steps=200,
                             eval_strategy=eval_strategy, eval_steps=50,
                             report_to=[])
    trainer = SFTTrainer(model=model, args=args, train_dataset=ds,
                         eval_dataset=ds_val,
                         dataset_text_field="text",
                         max_seq_length=4096, tokenizer=tok)
    trainer.train()
    trainer.save_model(str(OUT_DIR / "adapter"))
    print(f"[done] LoRA adapter → {OUT_DIR / 'adapter'}  (merge/convert to GGUF for Ollama/LM Studio)")
    return 0


def check_artifacts(rows):
    """Detect teacher-model repetitive patterns in keep rows."""
    keeps = [r for r in rows if str(r.get("decision")).lower() == "keep"]
    if not keeps:
        print("[artifacts] no keep rows"); return

    by_seed = {}
    for r in keeps:
        s = row_seed(r)
        by_seed.setdefault(s, []).append(r)

    print(f"[artifacts] analyzing {len(keeps)} keep rows across {len(by_seed)} seeds\n")
    for seed, seed_rows in sorted(by_seed.items()):
        msgs_list = [record_to_messages(r) for r in seed_rows]
        msgs_list = [m for m in msgs_list if m]

        # 1) user prompt uniqueness
        user_texts = [m[1]["content"][:200] if len(m) > 1 else "" for m in msgs_list]
        unique_prompts = len(set(user_texts))

        # 2) assistant response opening (first 100 chars)
        openings = [m[2]["content"][:100] if len(m) > 2 else "" for m in msgs_list]
        from collections import Counter
        top_openings = Counter(openings).most_common(3)

        # 3) geometry_ops count distribution
        op_counts = []
        for r in seed_rows:
            payload = r.get("payload") or {}
            parts = payload.get("parts") or []
            for p in parts:
                bp = p.get("blueprint") or {}
                n = len(bp.get("geometry_ops") or [])
                if n > 0:
                    op_counts.append(n)
        avg_ops = sum(op_counts) / len(op_counts) if op_counts else 0
        ops_unique = len(set(op_counts))

        print(f"  {seed} ({len(seed_rows)} rows):")
        print(f"    unique user prompts: {unique_prompts}/{len(seed_rows)}"
              f"{'  << LOW' if unique_prompts <= 2 else ''}")
        print(f"    top assistant openings:")
        for opening, cnt in top_openings:
            pct = cnt / len(msgs_list) * 100
            print(f"      {pct:4.0f}% ({cnt}x): {opening[:60]}...")
        print(f"    geometry_ops/part: avg {avg_ops:.1f}, {ops_unique} distinct counts")
        print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", action="store_true", help="actually train (else gate-check only)")
    ap.add_argument("--force", action="store_true", help="train below trial threshold")
    ap.add_argument("--base", default=DEFAULT_BASE, help="student base model (HF id)")
    ap.add_argument("--inspect", action="store_true", help="dump first corpus row + a built example, then exit")
    ap.add_argument("--check-artifacts", action="store_true", help="detect teacher-model repetitive patterns")
    a = ap.parse_args()

    rows = load_rows()
    if a.check_artifacts:
        check_artifacts(rows)
        return 0
    if a.inspect:
        if not rows:
            print(f"corpus empty: {CORPUS} (0 rows). Curate keep/reject in the UI to accrue rows.")
            return 0
        print(f"{len(rows)} rows. First row keys: {sorted(rows[0].keys())}")
        ex = to_chat_example(rows[0])
        print("built example:\n" + json.dumps(ex, ensure_ascii=False, indent=2)[:1500])
        return 0
    ok = gate_check(rows, a.force)
    if not a.train:
        print("[mode] gate-check only (use --train to fine-tune). Teacher (gpt-oss-20B) stays unchanged.")
        return 0
    if not ok:
        return 1
    return train(rows, a.base)


if __name__ == "__main__":
    raise SystemExit(main())
