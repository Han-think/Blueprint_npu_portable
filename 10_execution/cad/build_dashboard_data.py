"""
build_dashboard_data.py — 5 seed 산출물을 대시보드용 JSON 으로 집계
=================================================================
출력: 10_execution/ui/dashboard.json  (대시보드가 fetch)
"""
from __future__ import annotations
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SEEDS = REPO / "20_dataset" / "seeds"
OUT = REPO / "10_execution" / "ui" / "dashboard.json"
SEED_LIST = ["cubesat", "tiltrotor", "robot_arm", "small_launch_vehicle", "long_range_recon_wing", "haptic_glove"]


def pct(old, new):
    return round((old - new) / old * 100) if old else 0


def collect():
    mrl_summary = _json(REPO / "10_execution" / "cad" / "output" / "mrl05_summary.json", {})
    mrl_by_seed = {r.get("seed"): r for r in mrl_summary.get("reports", [])}
    interference_summary = _json(REPO / "10_execution" / "cad" / "output" / "interference_summary.json", {})
    interference_by_seed = {r.get("seed"): r for r in interference_summary.get("reports", [])}
    cards = []
    for s in SEED_LIST:
        pkg = json.loads((SEEDS / s / "package.json").read_text(encoding="utf-8"))
        bp = pkg["schema_v6_blueprint"]
        delta = pkg.get("assembly_delta", {})
        asm_p = SEEDS / s / "assembly.json"
        asm = json.loads(asm_p.read_text(encoding="utf-8")) if asm_p.exists() else {}
        jc = SEEDS / s / "judgment_causal.jsonl"
        n_causal = len([l for l in jc.read_text(encoding="utf-8").splitlines() if l.strip()]) if jc.exists() else 0
        n_think = len([l for l in (SEEDS / s / "thinking.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()])
        ne = len(pkg.get("existing_bom", [])); nr = len(pkg.get("redesigned_bom", []))
        bs = delta.get("baseline_steps", 0); rs = delta.get("redesigned_steps", 0)
        mrl = mrl_by_seed.get(s) or _json(REPO / "10_execution" / "cad" / "output" / s / f"{s}_mrl05.json", {})
        placement = interference_by_seed.get(s) or _json(REPO / "10_execution" / "cad" / "output" / s / "assembly_interference_report.json", {})
        cards.append({
            "seed": s,
            "label": pkg["target"].get("label", s),
            "target": pkg["target"]["vehicle_id"],
            "parts": {"from": ne, "to": nr, "cut": pct(ne, nr)},
            "steps": {"from": bs, "to": rs, "cut": pct(bs, rs)},
            "service_access": len(delta.get("retained_service_access_points", [])),
            "hardware_bom": asm.get("hardware_bom", []),
            "fasteners": len(asm.get("fasteners", [])),
            "joints": len(asm.get("joints", [])),
            "mass_g": bp.get("cad_brief", {}).get("mass_est_g", 0),
            "mrl05": {
                "score": mrl.get("score", 0),
                "status": mrl.get("status", "unknown"),
                "issues": mrl.get("issues", []),
                "loop_feedback": mrl.get("loop_feedback", ""),
                "report": mrl.get("report", f"/output/{s}/{s}_mrl05.json"),
            },
            "placement_audit": {
                "score": placement.get("score", 0),
                "status": placement.get("status", "unknown"),
                "counts": placement.get("counts", {}),
                "findings": placement.get("findings", []),
                "loop_feedback": placement.get("loop_feedback", ""),
                "report": placement.get("report", f"/output/{s}/assembly_interference_report.json"),
            },
            "thinking": n_think, "causal": n_causal,
            "stl": f"/output/{s}/{s}.stl",
            "svg": f"/output/{s}/{s}_drawing.svg",
        })
    pipeline = {
        "thinking_total": sum(c["thinking"] for c in cards),
        "causal_total": sum(c["causal"] for c in cards),
        "sft_train": _count(REPO / "20_dataset" / "train" / "blueprint_judgment_sft_train.jsonl"),
        "sft_eval": _count(REPO / "20_dataset" / "eval" / "blueprint_judgment_sft_eval.jsonl"),
        "part_spec": sum(_count(REPO / "20_dataset" / "seeds" / c["seed"] / "part_spec.jsonl") for c in cards),
        "preference": _count(REPO / "20_dataset" / "train" / "blueprint_preference_dpo.jsonl"),
        "eval_cases": sum(_count(p) for p in (REPO / "20_dataset" / "eval").glob("*_eval.jsonl")),
        "seeds": len(cards),
        "mrl05_average": mrl_summary.get("average_score", round(sum(c["mrl05"]["score"] for c in cards) / max(1, len(cards)))),
        "mrl05_ready": mrl_summary.get("ready", sum(1 for c in cards if c["mrl05"]["status"] == "ready")),
        "mrl05_watch": mrl_summary.get("watch", sum(1 for c in cards if c["mrl05"]["status"] == "watch")),
        "mrl05_weak": mrl_summary.get("weak", sum(1 for c in cards if c["mrl05"]["status"] == "weak")),
        "placement_average": interference_summary.get("average_score", round(sum(c["placement_audit"]["score"] for c in cards) / max(1, len(cards)))),
        "placement_pass": interference_summary.get("pass", sum(1 for c in cards if c["placement_audit"]["status"] == "pass")),
        "placement_watch": interference_summary.get("watch", sum(1 for c in cards if c["placement_audit"]["status"] == "watch")),
        "placement_block": interference_summary.get("block", sum(1 for c in cards if c["placement_audit"]["status"] == "block")),
    }
    return {"generated": "blueprint_dashboard_v1", "axes": ["00_contract", "10_execution", "20_dataset", "30_model"],
            "mrl05": mrl_summary,
            "interference": interference_summary,
            "pipeline": pipeline, "cards": cards}


def _count(p: Path):
    return len([l for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]) if p.exists() else 0


def _json(p: Path, default):
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))


def main():
    data = collect()
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"dashboard.json 생성: {OUT.relative_to(REPO)}")
    print(f"  seed {len(data['cards'])} · thinking {data['pipeline']['thinking_total']} · "
          f"SFT train {data['pipeline']['sft_train']}/eval {data['pipeline']['sft_eval']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
