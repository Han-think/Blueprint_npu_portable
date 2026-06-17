"""
derive_judgment.py — package.json 에서 공학 판단 인과(causal) row 와 eval 케이스를 derive
============================================================================================

judgment_schema_v2.md 의 인과 사슬을 package 에서 추출한다. 손으로 새로 쓰지 않음.
- integration_decisions + primary_metric + risk → judgment_causal.jsonl
- quality_scenarios → eval/<seed>_eval.jsonl

사용:
    python derive_judgment.py <seed>          # 예: cubesat
    python derive_judgment.py --all-dry-run   # 5 seed derive 가능성만 점검(파일 미생성)
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

SEEDS_DIR = Path(__file__).resolve().parents[1] / "seeds"
EVAL_DIR = Path(__file__).resolve().parents[1] / "eval"
ONTOLOGY_FILE = SEEDS_DIR / "_common" / "classification_ontology.json"

EXPECTED_POLARITY = {"pass": "approve", "fail": "reject", "risk": "caution"}


def infer_core(decision_text: str) -> str | None:
    """integration_decision 동사 → 온톨로지 코어 추론.

    공학적 의미:
    - integrate            → 통합 (INTEGRATE)
    - reduce/combine ... but keep access → 부분 통합 (PARTIAL_INTEGRATE)
    - keep ... removable/replaceable/separate, externalize, separate → 분리 (DECOUPLE)
    - index ... datum/ticks → 기준 보존 (GUARDRAIL)
    - do not integrate / reject → 거부 (REJECT)
    """
    t = decision_text.lower().strip()
    if t.startswith("do not integrate") or t.startswith("reject"):
        return "REJECT"
    if t.startswith("integrate"):
        return "INTEGRATE"
    # combine ... but keep (slide-in/access) = 합치되 접근 보존 → 부분 통합
    if t.startswith("combine") or t.startswith("reduce"):
        return "PARTIAL_INTEGRATE"
    if t.startswith("externalize") or t.startswith("separate"):
        return "DECOUPLE"
    # keep ... (removable/replaceable/separate/service/slide) = 분리 유지
    if t.startswith("keep"):
        return "DECOUPLE"
    # index ... (datum/ticks) = 정렬 기준 가시화 보존
    if t.startswith("index"):
        return "GUARDRAIL"
    return None


def load_cores() -> set[str]:
    onto = json.loads(ONTOLOGY_FILE.read_text(encoding="utf-8"))
    return set(onto.get("cores", {}).keys())


def derive(seed: str, write: bool = True) -> tuple[int, int, list[str]]:
    pkg_path = SEEDS_DIR / seed / "package.json"
    d = json.loads(pkg_path.read_text(encoding="utf-8"))
    target = d["target"]["vehicle_id"]
    metric = d["primary_metric"]
    cores = load_cores()
    warnings: list[str] = []

    # 관련 risk 의 mitigation (진화 후크 재료) — 첫 high/med 우선
    risks = d.get("schema_v6_blueprint", {}).get("risk", [])
    mit_pool = [r.get("mit", "") for r in risks if r.get("mit")]

    causal_rows = []
    for i, dec in enumerate(d.get("integration_decisions", [])):
        core = infer_core(dec["decision"])
        if core is None:
            warnings.append(f"{seed}: core 추론 실패 → 수동 매핑 필요: '{dec['decision']}'")
            core = "UNMAPPED"
        elif core not in cores:
            warnings.append(f"{seed}: 추론 core '{core}' 가 온톨로지에 없음")
        row = {
            "schema": "blueprint_judgment_causal_v2",
            "target": target,
            "objective": {
                "metric": metric.get("name", ""),
                "definition": metric.get("definition", ""),
                "failure_rule": metric.get("failure_rule", ""),
            },
            "constraint": dec.get("guardrail", ""),
            "trade_off": {
                "gain": dec.get("expected_gain", ""),
                "guardrail": dec.get("guardrail", ""),
                "cost_if_violated": metric.get("failure_rule", ""),
            },
            "decision": {"core": core, "rationale": dec["decision"]},
            "verification": [{
                "check": dec.get("guardrail", ""),
                "measurable": bool(dec.get("guardrail")),
                "expected": "pass",
            }],
            "evolution": {
                "leaves_for_next": dec.get("guardrail", "")
                + ((" | mit: " + mit_pool[i]) if i < len(mit_pool) else ""),
            },
        }
        causal_rows.append(row)

    eval_rows = []
    for sc in d.get("quality_scenarios", []):
        exp = sc.get("expected", "")
        eval_rows.append({
            "schema": "blueprint_eval_case_v1",
            "target": target,
            "case": sc.get("case", ""),
            "expected": exp,
            "expected_polarity": EXPECTED_POLARITY.get(exp, "unknown"),
            "reason": sc.get("reason", ""),
        })

    if write:
        out_causal = SEEDS_DIR / seed / "judgment_causal.jsonl"
        out_causal.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in causal_rows) + "\n", encoding="utf-8")
        EVAL_DIR.mkdir(parents=True, exist_ok=True)
        out_eval = EVAL_DIR / f"{seed}_eval.jsonl"
        out_eval.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in eval_rows) + "\n", encoding="utf-8")
    return len(causal_rows), len(eval_rows), warnings


def main(argv: list[str]) -> int:
    if "--all-dry-run" in argv:
        print("5 seed derive 가능성 점검 (파일 미생성):")
        seeds = ["cubesat", "tiltrotor", "robot_arm", "small_launch_vehicle", "long_range_recon_wing", "haptic_glove"]
        total_warn = 0
        for s in seeds:
            nc, ne, w = derive(s, write=False)
            total_warn += len(w)
            print(f"  [{s}] causal={nc} eval={ne} warn={len(w)}")
            for x in w: print(f"      ! {x}")
        print(f"\n총 경고 {total_warn}건")
        return 0 if total_warn == 0 else 2
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args:
        print("사용: python derive_judgment.py <seed> | --all-dry-run")
        return 1
    seed = args[0]
    nc, ne, w = derive(seed, write=True)
    print(f"[{seed}] derive 완료: judgment_causal {nc} rows, eval {ne} cases")
    for x in w: print(f"  ! {x}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
