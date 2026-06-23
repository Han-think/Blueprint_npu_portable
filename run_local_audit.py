"""run_local_audit.py — 로컬에서 300개 batch 결과에 CAD audit 재판정
Usage:
  python run_local_audit.py              # 전체 실행
  python run_local_audit.py --seed cubesat  # 특정 seed만
  python run_local_audit.py --dry-run    # 실행 없이 대상 목록만
"""
import json, os, subprocess, sys, time
from pathlib import Path
from datetime import datetime

REPO = Path(__file__).resolve().parent
CAD_DIR = REPO / "10_execution" / "cad"
OUT = CAD_DIR / "output"
SEEDS_DIR = REPO / "20_dataset" / "seeds_generated"
CURATION_LOG = REPO / "30_model" / "curation" / "curation_log.jsonl"
SEEDS = ["cubesat", "robot_arm", "tiltrotor", "small_launch_vehicle", "long_range_recon_wing", "haptic_glove"]


def read_reports(seed):
    base = OUT / f"{seed}_generated"
    def rj(p):
        try:
            return json.loads((base / p).read_text(encoding="utf-8"))
        except Exception:
            return {}
    return rj("assembly_interference_report.json"), rj("analysis_report.json"), rj("geometry_resolution.json")


from generate_batch import auto_decision, SEED_FOS_THRESHOLDS, fos_grade


def count_parts(run_dir):
    pkg = Path(run_dir) / "package.json"
    if not pkg.exists():
        return 0, 0
    try:
        d = json.loads(pkg.read_text(encoding="utf-8"))
        gp = d.get("generated_parts", d.get("parts", []))
        total = len(gp)
        ok = sum(1 for p in gp if p.get("blueprint") and len(p["blueprint"].get("geometry_ops", [])) >= 1)
        return total, ok
    except Exception:
        return 0, 0


def _folder_to_dt(folder_name):
    try:
        return datetime.strptime(folder_name, "%Y%m%d_%H%M%S")
    except Exception:
        return None


def _started_to_dt(started_str):
    try:
        return datetime.fromisoformat(started_str.replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        return None


def update_curation_log(seed, run_dir, decision, why, fos, score, grade=None):
    rows = []
    if CURATION_LOG.exists():
        rows = [line for line in CURATION_LOG.read_text(encoding="utf-8").splitlines() if line.strip()]

    folder_name = Path(run_dir).name
    folder_dt = _folder_to_dt(folder_name)
    updated = False

    for i, line in enumerate(rows):
        try:
            row = json.loads(line)
            if row.get("seed") != seed:
                continue

            matched = False
            if folder_name in row.get("id", ""):
                matched = True
            elif folder_dt:
                started = (row.get("run_meta") or {}).get("started", "")
                row_dt = _started_to_dt(started)
                if row_dt and abs((folder_dt - row_dt).total_seconds()) < 120:
                    matched = True

            if matched:
                row["decision"] = decision
                row["engineering_scorecard"] = row.get("engineering_scorecard", {})
                row["engineering_scorecard"]["sizing_fos"] = fos
                row["engineering_scorecard"]["score"] = score
                row["engineering_scorecard"]["grade"] = grade
                row["engineering_scorecard"]["auto_reason"] = why
                row["engineering_scorecard"]["audit_ts"] = datetime.now().isoformat()
                rows[i] = json.dumps(row, ensure_ascii=False)
                updated = True
                break
        except Exception:
            continue

    if updated:
        tmp = CURATION_LOG.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8", newline="\n") as f:
            for row in rows:
                f.write(row + "\n")
        tmp.replace(CURATION_LOG)
    return updated


def run_audit(seed, run_dir, dry_run=False, resync=False):
    if dry_run:
        print(f"  [DRY] {seed} / {Path(run_dir).name}")
        return None, None

    if not resync:
        try:
            result = subprocess.run(
                [sys.executable, "run_full_pipeline.py", seed, "--dir", str(run_dir)],
                cwd=str(CAD_DIR), timeout=600, capture_output=True, text=True
            )
            if result.returncode != 0:
                print(f"  FAIL: {result.stderr[:200] if result.stderr else 'unknown error'}")
        except subprocess.TimeoutExpired:
            print(f"  TIMEOUT (600s)")
        except Exception as e:
            print(f"  ERROR: {e}")

    interference, analysis, resolution = read_reports(seed)
    parts_total, parts_ok = count_parts(run_dir)
    decision, why, grade = auto_decision(parts_total, parts_ok, interference, analysis, resolution,
                                         seed_name=seed)

    sizing = analysis.get("sizing", {})
    fos = sizing.get("solver_fos", sizing.get("worst_fos"))
    score = analysis.get("score")

    ok = update_curation_log(seed, run_dir, decision, why, fos, score, grade)
    if resync and not ok:
        print(f"  (no matching log row)")
    return decision, why


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", default="", help="specific seed to audit")
    ap.add_argument("--dry-run", action="store_true", help="list targets without running")
    ap.add_argument("--resync", action="store_true", help="skip CAD pipeline, re-read existing reports and update curation_log")
    args = ap.parse_args()

    seeds = [args.seed] if args.seed else SEEDS
    seeds = [s for s in seeds if (SEEDS_DIR / s).exists()]

    targets = []
    for seed in seeds:
        for d in sorted((SEEDS_DIR / seed).iterdir()):
            if d.is_dir():
                targets.append((seed, str(d)))

    print(f"[audit] {len(targets)} candidates across {len(seeds)} seeds")
    if args.dry_run:
        for seed, d in targets:
            print(f"  {seed} / {Path(d).name}")
        return

    tally = {"keep": 0, "reject": 0, "hold": 0}
    t0 = time.time()

    for i, (seed, run_dir) in enumerate(targets):
        elapsed = time.time() - t0
        rate = (i / elapsed * 3600) if elapsed > 0 and i > 0 else 0
        eta = ((len(targets) - i) / (i / elapsed)) if elapsed > 0 and i > 0 else 0
        eta_m = int(eta // 60)
        eta_s = int(eta % 60)

        print(f"\n[{i+1}/{len(targets)}] {seed} / {Path(run_dir).name}  ({rate:.0f}/hr, ETA {eta_m}m{eta_s}s)")
        decision, why = run_audit(seed, run_dir, resync=args.resync)
        if decision:
            tally[decision] = tally.get(decision, 0) + 1
            symbol = {"keep": "OK", "reject": "XX", "hold": "--"}.get(decision, "??")
            print(f"  {symbol} {decision.upper()}: {why}")

    total = sum(tally.values())
    print(f"\n{'='*60}")
    print(f"  AUDIT COMPLETE: {total} candidates")
    print(f"  Keep: {tally['keep']}  Reject: {tally['reject']}  Hold: {tally['hold']}")
    if total > 0:
        print(f"  Keep rate: {tally['keep']/total*100:.0f}%")
    print(f"  Time: {(time.time()-t0)/60:.1f} min")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
