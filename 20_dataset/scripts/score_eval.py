"""
score_eval.py — 평가 케이스 채점기 (진화 루프의 채점 장치)
==========================================================

eval/<seed>_eval.jsonl 의 정답(expected_polarity)과 모델 예측을 대조해 accuracy 를 낸다.

사용:
    python score_eval.py <seed>                      # self-score (정답=예측, sanity 100%)
    python score_eval.py <seed> <predictions.jsonl>  # 모델 예측 채점

predictions.jsonl row (모델 출력 자리 — 인터페이스):
    {"case": "<eval 의 case 와 동일>", "predicted_polarity": "approve|reject|caution"}
    (또는 "expected"/"predicted" 키로 pass|fail|risk 를 줘도 polarity 로 환산)

모델 연결(ollama 등)은 사용자 판단. 이 스크립트는 채점 인터페이스만 제공한다.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parents[1] / "eval"
POL = {"pass": "approve", "fail": "reject", "risk": "caution"}


def to_polarity(row: dict) -> str:
    if "predicted_polarity" in row:
        return row["predicted_polarity"]
    if "polarity" in row:
        return row["polarity"]
    v = row.get("predicted") or row.get("expected") or ""
    return POL.get(v, v)


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args:
        print("사용: python score_eval.py <seed> [predictions.jsonl]")
        return 1
    seed = args[0]
    eval_path = EVAL_DIR / f"{seed}_eval.jsonl"
    if not eval_path.exists():
        print(f"eval 없음: {eval_path} — 먼저 derive_judgment.py 실행")
        return 1

    gold = {}
    for l in eval_path.read_text(encoding="utf-8").splitlines():
        if not l.strip():
            continue
        r = json.loads(l)
        gold[r["case"]] = r["expected_polarity"]

    # 예측 로드 (없으면 self-score)
    if len(args) >= 2:
        pred = {}
        for l in Path(args[1]).read_text(encoding="utf-8").splitlines():
            if not l.strip():
                continue
            r = json.loads(l)
            pred[r["case"]] = to_polarity(r)
        mode = f"예측파일: {args[1]}"
    else:
        pred = dict(gold)  # self-score sanity
        mode = "self-score (sanity)"

    total = len(gold)
    correct = 0
    misses = []
    for case, g in gold.items():
        p = pred.get(case)
        if p == g:
            correct += 1
        else:
            misses.append((case, g, p))

    acc = correct / total * 100 if total else 0
    print(f"[{seed}] 채점 — {mode}")
    print(f"  정확도: {correct}/{total} = {acc:.0f}%")
    if misses:
        print(f"  오답 {len(misses)}건:")
        for case, g, p in misses:
            print(f"    - '{case[:50]}' 정답={g} 예측={p}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
