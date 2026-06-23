"""audit_hold_rows.py — HOLD 행에 CAD audit 돌려서 FoS 계산 후 KEEP/REJECT 전환"""
import json, sys, time, tempfile, shutil
from pathlib import Path
from datetime import datetime

REPO = Path(__file__).resolve().parent
CURATION_LOG = REPO / "30_model" / "curation" / "curation_log.jsonl"

sys.path.insert(0, str(REPO / "10_execution" / "cad"))
sys.path.insert(0, str(REPO))

from generate_batch import auto_decision, SEED_FOS_THRESHOLDS, fos_grade

def run_pipeline_on_payload(seed, payload):
    tmp = Path(tempfile.mkdtemp(prefix=f"audit_{seed}_"))
    try:
        parts = payload.get("parts", [])
        first_bp = parts[0].get("blueprint", {}) if parts else {}
        pkg = {
            "schema": payload.get("schema", "blueprint_npu_assembly_curation_v1"),
            "seed": seed,
            "run_id": "audit_hold",
            "vehicle": payload.get("vehicle", {}),
            "run_meta": payload.get("run_meta", {}),
            "schema_v6_blueprint": first_bp,
            "generated_parts": parts,
        }
        pkg_path = tmp / "package.json"
        pkg_path.write_text(json.dumps(pkg, ensure_ascii=False), encoding="utf-8")
        import run_full_pipeline
        run_full_pipeline.run_pipeline(seed, str(tmp))
        out = REPO / "10_execution" / "cad" / "output" / f"{seed}_generated"
        def rj(name):
            try:
                return json.loads((out / name).read_text(encoding="utf-8"))
            except Exception:
                return {}
        interference = rj("assembly_interference_report.json")
        analysis = rj("analysis_report.json")
        resolution = rj("geometry_resolution.json")
        return interference, analysis, resolution
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def main():
    lines = CURATION_LOG.read_text(encoding="utf-8").splitlines()
    rows = [(i, json.loads(l)) for i, l in enumerate(lines) if l.strip()]
    hold_indices = [(i, r) for i, r in rows if r.get("decision") == "hold"]
    print(f"[audit] {len(hold_indices)} HOLD rows to process")

    gate_current = sum(1 for _, r in rows if r.get("decision") in ("keep", "reject"))
    gate_target = 300
    needed = max(0, gate_target - gate_current)
    print(f"[gate] current {gate_current}/{gate_target}, need {needed} more keep/reject")

    tally = {"keep": 0, "reject": 0, "hold": 0, "error": 0}
    t0 = time.time()
    updated_lines = list(lines)

    for idx, (line_idx, row) in enumerate(hold_indices):
        seed = row.get("seed", "?")
        rid = row.get("id", "?")[:40]
        elapsed = time.time() - t0
        rate = (idx / elapsed) if elapsed > 0 and idx > 0 else 0
        eta = int((len(hold_indices) - idx) / rate) if rate > 0 else 0
        print(f"\n[{idx+1}/{len(hold_indices)}] {seed} / {rid}  (ETA {eta//60}m{eta%60}s)")

        payload = row.get("payload")
        if not payload or not payload.get("parts"):
            print("  SKIP: no payload")
            tally["error"] += 1
            continue

        try:
            interference, analysis, resolution = run_pipeline_on_payload(seed, payload)
        except Exception as e:
            print(f"  ERROR: {e}")
            tally["error"] += 1
            continue

        parts = payload.get("parts", [])
        parts_total = len(parts)
        parts_ok = sum(1 for p in parts if p.get("blueprint") and
                       len((p["blueprint"].get("geometry_ops") or [])) >= 1)

        decision, why, grade = auto_decision(parts_total, parts_ok, interference, analysis,
                                              resolution, seed_name=seed)
        sizing = analysis.get("sizing", {})
        fos = sizing.get("solver_fos", sizing.get("worst_fos"))
        score = analysis.get("score")

        row["decision"] = decision
        sc = row.get("engineering_scorecard", {})
        sc["sizing_fos"] = fos
        sc["score"] = score
        sc["grade"] = grade
        sc["auto_reason"] = why
        sc["audit_ts"] = datetime.now().isoformat()
        row["engineering_scorecard"] = sc

        updated_lines[line_idx] = json.dumps(row, ensure_ascii=False)
        tally[decision] = tally.get(decision, 0) + 1

        symbol = {"keep": "OK", "reject": "XX", "hold": "--"}.get(decision, "??")
        print(f"  {symbol} {decision.upper()}: {why}")

        if tally["keep"] + tally["reject"] >= needed and needed > 0:
            print(f"\n  >>> Gate target reached! ({tally['keep']} keep + {tally['reject']} reject >= {needed} needed)")

    tmp = CURATION_LOG.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
        for line in updated_lines:
            f.write(line + "\n")
    tmp.replace(CURATION_LOG)

    total = sum(v for k, v in tally.items() if k != "error")
    print(f"\n{'='*60}")
    print(f"  AUDIT COMPLETE: {total} processed, {tally['error']} errors")
    print(f"  Keep: {tally['keep']}  Reject: {tally['reject']}  Hold: {tally['hold']}")
    print(f"  Gate: {gate_current + tally['keep'] + tally['reject']}/300")
    print(f"  Time: {(time.time()-t0)/60:.1f} min")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
