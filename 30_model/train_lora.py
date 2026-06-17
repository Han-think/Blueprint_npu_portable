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


def corpus_summary(rows):
    keep = sum(1 for r in rows if str(r.get("decision")).lower() == "keep")
    reject = sum(1 for r in rows if str(r.get("decision")).lower() == "reject")
    by_seed = {}
    for r in rows:
        s = row_seed(r)
        by_seed[s] = by_seed.get(s, 0) + 1
    return {"total": len(rows), "keep": keep, "reject": reject, "by_seed": by_seed}


def to_chat_example(row):
    """keep = 정답 메시지. reject = '회피' 신호로 시스템에 부정 라벨. messages 없으면 레코드에서 유도."""
    msgs = record_to_messages(row)
    decision = str(row.get("decision")).lower()
    if decision == "reject":
        # reject는 회피 학습: system 에 '이 패턴은 reject됨' 표식 추가
        msgs = [{"role": "system",
                 "content": (msgs[0]["content"] if msgs and msgs[0]["role"] == "system" else "")
                 + "\n[CURATION] The following assistant output was REJECTED by engineering review — avoid this pattern."}] + \
               [m for m in msgs if m["role"] != "system"]
    return {"messages": msgs}


def gate_check(rows, force):
    s = corpus_summary(rows)
    print(f"[corpus] total {s['total']} | keep {s['keep']} | reject {s['reject']} | by_seed {s['by_seed']}")
    if s["total"] >= FULL_THRESHOLD:
        print(f"[gate] >= full threshold ({FULL_THRESHOLD}) — ready for a real run.")
        return True
    if s["total"] >= TRIAL_THRESHOLD:
        print(f"[gate] >= trial threshold ({TRIAL_THRESHOLD}) — OK for a smoke-test LoRA.")
        return True
    if force:
        print(f"[gate] below trial ({s['total']}/{TRIAL_THRESHOLD}) but --force given.")
        return True
    print(f"[gate] NOT ENOUGH DATA: {s['total']}/{TRIAL_THRESHOLD} (trial). Keep curating (good/bad). No training.")
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

    examples = [to_chat_example(r) for r in rows if record_to_messages(r)]
    if not examples:
        print("[data] no trainable examples could be built from the corpus (check --inspect).")
        return 1
    ds = Dataset.from_list(examples)

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

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    args = TrainingArguments(output_dir=str(OUT_DIR), num_train_epochs=2,
                             per_device_train_batch_size=1, gradient_accumulation_steps=8,
                             learning_rate=2e-4, fp16=True, logging_steps=10, save_steps=200,
                             report_to=[])
    trainer = SFTTrainer(model=model, args=args, train_dataset=ds, dataset_text_field="text",
                         max_seq_length=4096, tokenizer=tok)
    trainer.train()
    trainer.save_model(str(OUT_DIR / "adapter"))
    print(f"[done] LoRA adapter → {OUT_DIR / 'adapter'}  (merge/convert to GGUF for Ollama/LM Studio)")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", action="store_true", help="actually train (else gate-check only)")
    ap.add_argument("--force", action="store_true", help="train below trial threshold")
    ap.add_argument("--base", default=DEFAULT_BASE, help="student base model (HF id)")
    ap.add_argument("--inspect", action="store_true", help="dump first corpus row + a built example, then exit")
    a = ap.parse_args()

    rows = load_rows()
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
