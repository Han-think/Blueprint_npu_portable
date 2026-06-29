"""audit_hold_rows.py — HOLD 행에 CAD audit 돌려서 FoS 계산 후 KEEP/REJECT 전환.

CAD/build123d/OCCT can hang inside native code. Do not run it in a thread:
run one candidate per subprocess so a timeout kills only that candidate.
"""
import argparse
import os
import json, sys, time, tempfile, shutil, subprocess
import traceback
from pathlib import Path
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parent
CURATION_LOG = REPO / "30_model" / "curation" / "curation_log.jsonl"
CURATION_INDEX = REPO / "30_model" / "curation" / "curation_index.json"

sys.path.insert(0, str(REPO / "10_execution" / "cad"))
sys.path.insert(0, str(REPO))

from generate_batch import auto_decision, SEED_FOS_THRESHOLDS, fos_grade


def _vehicle_envelope_mm(vehicle):
    import re
    nums = re.findall(r"\d+(?:\.\d+)?", str((vehicle or {}).get("envelope", "")))
    return [float(n) for n in nums[:3]] if len(nums) >= 3 else [400.0, 400.0, 400.0]


def package_from_payload(seed, payload):
    """Build the same assembly-shaped package that serve.export_bundle_to_seed_dir writes.

    Earlier versions used the first generated part as schema_v6_blueprint. That made
    CAD/audit judge only one subsystem and could turn assembly candidates into false
    LOW-RES rejects. The audit package must preserve all generated parts as root
    assembly children and retarget each subsystem op to its assembly root.
    """
    vehicle = payload.get("vehicle", {})
    parts = payload.get("parts", [])
    generated_parts = [p for p in parts if p.get("blueprint")]
    children, geometry_ops = [], []
    for i, part in enumerate(generated_parts):
        pid = part.get("id") or f"new-{i + 1:03d}"
        bp = part.get("blueprint") or {}
        cad = bp.get("cad_brief") or {}
        children.append({
            "id": pid,
            "name": part.get("label") or cad.get("name") or pid,
            "qty": 1,
            "material": cad.get("material") or (vehicle or {}).get("material", "PETG"),
            "process": cad.get("process") or (vehicle or {}).get("process", "FDM"),
            "children": [],
        })
        for op in bp.get("geometry_ops") or []:
            op2 = dict(op)
            if "target" in op2:
                op2["_source_target"] = op2.get("target")
            op2["target"] = pid
            geometry_ops.append(op2)
    best = max(generated_parts, key=lambda p: len(((p.get("blueprint") or {}).get("part_tree") or {}).get("children") or []),
               default={})
    best_bp = best.get("blueprint") or {}
    envelope = _vehicle_envelope_mm(vehicle)
    composite_bp = {
        "version": "bp-npu-r6",
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "project": seed,
        "object": (vehicle or {}).get("label", seed),
        "brief": best_bp.get("brief") or {
            "requirements": [],
            "constraints": {
                "material": (vehicle or {}).get("material", "PETG"),
                "process": (vehicle or {}).get("process", "FDM"),
                "envelope_mm": envelope,
                "min_wall_mm": 1.5,
                "overhang_deg": 45,
                "tol_mm": 0.2,
            },
        },
        "cad_brief": {
            "name": (vehicle or {}).get("label", seed),
            "rev": "1.0",
            "material": (vehicle or {}).get("material", "PETG"),
            "envelope_mm": envelope,
            "build_direction": "Z",
        },
        "part_tree": {"id": "asm", "name": (vehicle or {}).get("label", seed), "qty": 1, "children": children},
        "geometry_ops": geometry_ops,
    }
    return {
        "schema": "blueprint_generated_package_v1",
        "seed": seed,
        "run_id": "audit_hold",
        "vehicle": vehicle,
        "run_meta": payload.get("run_meta", {}),
        "schema_v6_blueprint": composite_bp,
        "generated_parts": generated_parts,
        "audit_package_mode": "composite_all_generated_parts_v2",
    }


def read_cad_reports(seed):
    out = REPO / "10_execution" / "cad" / "output" / f"{seed}_generated"
    def rj(name):
        try:
            return json.loads((out / name).read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {
        "interference": rj("assembly_interference_report.json"),
        "analysis": rj("analysis_report.json"),
        "resolution": rj("geometry_resolution.json"),
    }


def run_pipeline_worker(seed, package_dir, result_path):
    """Subprocess entrypoint. Writes a compact JSON result and exits."""
    try:
        sys.path.insert(0, str(REPO / "10_execution" / "cad"))
        import run_full_pipeline
        run_full_pipeline.run_pipeline(seed, str(package_dir))
        result = {"ok": True, **read_cad_reports(seed)}
    except BaseException as exc:
        result = {
            "ok": False,
            "error": f"{type(exc).__name__}: {str(exc)[:500]}",
            "traceback": traceback.format_exc()[-4000:],
        }
    Path(result_path).write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    return 0 if result.get("ok") else 1


def run_pipeline_on_payload(seed, payload, timeout_s=90):
    tmp = Path(tempfile.mkdtemp(prefix=f"audit_{seed}_"))
    try:
        pkg = package_from_payload(seed, payload)
        pkg_path = tmp / "package.json"
        pkg_path.write_text(json.dumps(pkg, ensure_ascii=False), encoding="utf-8")
        result_path = tmp / "audit_result.json"
        cmd = [sys.executable, str(Path(__file__).resolve()), "--worker", seed, str(tmp), str(result_path)]
        stdout_path = tmp / "worker_stdout.log"
        stderr_path = tmp / "worker_stderr.log"
        with stdout_path.open("w", encoding="utf-8", errors="ignore") as out, \
                stderr_path.open("w", encoding="utf-8", errors="ignore") as err:
            proc = subprocess.Popen(cmd, cwd=str(REPO), stdout=out, stderr=err, text=True)
            deadline = time.time() + timeout_s
            while proc.poll() is None and time.time() < deadline:
                time.sleep(0.5)
            if proc.poll() is None:
                try:
                    proc.kill()
                except Exception:
                    pass
                try:
                    subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                                   capture_output=True, text=True, timeout=10)
                except Exception:
                    pass
                raise TimeoutError(f"CAD worker timeout >{timeout_s}s")
        if result_path.exists():
            result = json.loads(result_path.read_text(encoding="utf-8"))
        else:
            err_text = ""
            for log_path in (stderr_path, stdout_path):
                try:
                    err_text += log_path.read_text(encoding="utf-8", errors="ignore")[-1200:]
                except Exception:
                    pass
            result = {"ok": False, "error": (err_text or "worker produced no result")[:800]}
        if not result.get("ok"):
            detail = result.get("traceback") or result.get("error") or "CAD worker failed"
            raise RuntimeError(detail)
        return result.get("interference", {}), result.get("analysis", {}), result.get("resolution", {})
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def expected_and_ok_parts(payload):
    vehicle_parts = ((payload.get("vehicle") or {}).get("parts") or [])
    generated = payload.get("parts") or []
    expected_total = len(vehicle_parts) or len(generated)
    parts_ok = sum(1 for p in generated if p.get("blueprint") and
                   len((p["blueprint"].get("geometry_ops") or [])) >= 1)
    return expected_total, parts_ok


def cheap_prefilter(payload):
    if not payload or not payload.get("parts"):
        return "no payload parts"
    expected_total, parts_ok = expected_and_ok_parts(payload)
    if expected_total and parts_ok < expected_total:
        return f"incomplete before CAD: {parts_ok}/{expected_total} parts got a blueprint"
    for part in payload.get("parts", []):
        bp = part.get("blueprint") or {}
        if not (bp.get("part_tree") or {}).get("children"):
            return f"missing part_tree children before CAD: {part.get('id') or part.get('label')}"
        if not bp.get("geometry_ops"):
            return f"missing geometry_ops before CAD: {part.get('id') or part.get('label')}"
    return ""


def write_lines_atomic(path, lines):
    tmp = path.with_name(f"{path.stem}.{os.getpid()}.tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
        for line in lines:
            f.write(line + "\n")
    last_exc = None
    for _ in range(20):
        try:
            tmp.replace(path)
            return
        except PermissionError as exc:
            last_exc = exc
            time.sleep(0.25)
    try:
        tmp.unlink(missing_ok=True)
    except Exception:
        pass
    raise last_exc


def rebuild_curation_index(rows):
    kept = sum(1 for r in rows if r.get("decision") == "keep")
    rejected = sum(1 for r in rows if r.get("decision") == "reject")
    by_seed = {}
    last_ts = ""
    for r in rows:
        seed = r.get("seed", "unknown")
        by_seed[seed] = by_seed.get(seed, 0) + 1
        last_ts = r.get("ts") or last_ts
    index = {
        "schema": "blueprint_curation_index_v1",
        "total": len(rows),
        "kept": kept,
        "rejected": rejected,
        "by_seed": by_seed,
        "last_ts": last_ts,
        "rebuilt_at": datetime.now().isoformat(),
    }
    CURATION_INDEX.parent.mkdir(parents=True, exist_ok=True)
    CURATION_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeout", type=int, default=90, help="seconds per CAD candidate subprocess")
    ap.add_argument("--limit", type=int, default=0, help="process only first N HOLD rows")
    ap.add_argument("--no-prefilter", action="store_true", help="run CAD even for obvious incomplete rows")
    ap.add_argument("--prefilter-only", action="store_true",
                    help="only reject obvious incomplete/low-resolution rows; leave CAD candidates as HOLD")
    ap.add_argument("--retry-cad-errors", action="store_true",
                    help="retry rows already marked with cad_error/cad_timeout")
    ap.add_argument("--reconsider-low-res", action="store_true",
                    help="re-audit existing LOW-RES reject rows using the composite assembly package")
    ap.add_argument("--worker", nargs=3, metavar=("SEED", "PACKAGE_DIR", "RESULT_JSON"),
                    help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    if args.worker:
        seed, package_dir, result_path = args.worker
        return run_pipeline_worker(seed, Path(package_dir), Path(result_path))

    lines = CURATION_LOG.read_text(encoding="utf-8").splitlines()
    rows = [(i, json.loads(l)) for i, l in enumerate(lines) if l.strip()]
    hold_indices = []
    for i, r in rows:
        decision = r.get("decision")
        sc = r.get("engineering_scorecard") or {}
        if args.reconsider_low_res and decision == "reject":
            if sc.get("decision_changed_by") == "audit_hold_rows_composite_reaudit_v2":
                continue
            if sc.get("audit_stage") == "final_low_res_after_composite_reaudit":
                continue
            if str(sc.get("auto_reason") or "").startswith("LOW-RES"):
                hold_indices.append((i, r))
            continue
        if decision != "hold":
            continue
        stage = sc.get("audit_stage")
        if stage in ("cad_error", "cad_timeout") and not args.retry_cad_errors:
            continue
        hold_indices.append((i, r))
    if args.limit > 0:
        hold_indices = hold_indices[:args.limit]
    print(f"[audit] {len(hold_indices)} HOLD rows to process")

    gate_current = sum(1 for _, r in rows if r.get("decision") in ("keep", "reject"))
    gate_target = 300
    needed = max(0, gate_target - gate_current)
    print(f"[gate] current {gate_current}/{gate_target}, need {needed} more keep/reject")

    tally = {"keep": 0, "reject": 0, "hold": 0, "error": 0}
    t0 = time.time()
    updated_lines = list(lines)

    for idx, (line_idx, row) in enumerate(hold_indices):
        original_decision = row.get("decision")
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
        if not args.no_prefilter:
            prefilter_reason = cheap_prefilter(payload)
            if prefilter_reason:
                row["decision"] = "reject"
                sc = row.get("engineering_scorecard", {})
                sc["auto_reason"] = prefilter_reason
                sc["audit_ts"] = datetime.now().isoformat()
                sc["audit_stage"] = "cheap_prefilter"
                row["engineering_scorecard"] = sc
                updated_lines[line_idx] = json.dumps(row, ensure_ascii=False)
                tally["reject"] += 1
                print(f"  XX REJECT: {prefilter_reason}")
                write_lines_atomic(CURATION_LOG, updated_lines)
                continue
            if args.prefilter_only:
                print("  -- HOLD: prefilter passed, CAD audit deferred")
                tally["hold"] += 1
                continue

        try:
            interference, analysis, resolution = run_pipeline_on_payload(seed, payload, timeout_s=args.timeout)
        except TimeoutError as e:
            print(f"  HOLD: {e}")
            row["decision"] = "hold"
            sc = row.get("engineering_scorecard", {})
            sc["audit_error"] = str(e)
            sc["audit_stage"] = "cad_timeout"
            sc["audit_ts"] = datetime.now().isoformat()
            row["engineering_scorecard"] = sc
            updated_lines[line_idx] = json.dumps(row, ensure_ascii=False)
            tally["hold"] += 1
            write_lines_atomic(CURATION_LOG, updated_lines)
            continue
        except (Exception, SystemExit) as e:
            print(f"  HOLD: CAD error: {e}")
            row["decision"] = "hold"
            sc = row.get("engineering_scorecard", {})
            sc["audit_error"] = str(e)[:500]
            sc["audit_stage"] = "cad_error"
            sc["audit_ts"] = datetime.now().isoformat()
            row["engineering_scorecard"] = sc
            updated_lines[line_idx] = json.dumps(row, ensure_ascii=False)
            tally["hold"] += 1
            write_lines_atomic(CURATION_LOG, updated_lines)
            continue

        parts_total, parts_ok = expected_and_ok_parts(payload)

        decision, why, grade = auto_decision(parts_total, parts_ok, interference, analysis,
                                              resolution, seed_name=seed)
        sizing = analysis.get("sizing", {})
        fos = sizing.get("solver_fos", sizing.get("worst_fos"))
        score = analysis.get("score")

        row["decision"] = decision
        sc = row.get("engineering_scorecard", {})
        if original_decision != decision:
            sc["previous_decision"] = original_decision
            sc["decision_changed_by"] = "audit_hold_rows_composite_reaudit_v2"
        elif args.reconsider_low_res and original_decision == "reject" and decision == "reject":
            sc["decision_changed_by"] = "audit_hold_rows_composite_reaudit_v2"
            sc["audit_stage"] = "final_low_res_after_composite_reaudit"
        sc["sizing_fos"] = fos
        sc["score"] = score
        sc["grade"] = grade
        sc["auto_reason"] = why
        sc.pop("audit_error", None)
        if decision == "keep":
            sc["audit_stage"] = "cad_audit_keep"
        elif decision == "hold" and str(why).startswith("mid:"):
            sc["audit_stage"] = "analysis_mid_watch"
        elif decision == "reject":
            sc["audit_stage"] = sc.get("audit_stage") or "cad_audit_reject"
        sc["audit_ts"] = datetime.now().isoformat()
        sc["audit_package_mode"] = "composite_all_generated_parts_v2"
        row["engineering_scorecard"] = sc

        updated_lines[line_idx] = json.dumps(row, ensure_ascii=False)
        tally[decision] = tally.get(decision, 0) + 1

        symbol = {"keep": "OK", "reject": "XX", "hold": "--"}.get(decision, "??")
        print(f"  {symbol} {decision.upper()}: {why}")
        write_lines_atomic(CURATION_LOG, updated_lines)

        if tally["keep"] + tally["reject"] >= needed and needed > 0:
            print(f"\n  >>> Gate target reached! ({tally['keep']} keep + {tally['reject']} reject >= {needed} needed)")

        if (idx + 1) % 50 == 0:
            print(f"  [checkpoint saved at {idx+1}/{len(hold_indices)}]")

    write_lines_atomic(CURATION_LOG, updated_lines)
    rebuilt_rows = [json.loads(l) for l in updated_lines if l.strip()]
    rebuild_curation_index(rebuilt_rows)

    total = sum(v for k, v in tally.items() if k != "error")
    print(f"\n{'='*60}")
    print(f"  AUDIT COMPLETE: {total} processed, {tally['error']} errors")
    print(f"  Keep: {tally['keep']}  Reject: {tally['reject']}  Hold: {tally['hold']}")
    print(f"  Gate: {gate_current + tally['keep'] + tally['reject']}/300")
    print(f"  Time: {(time.time()-t0)/60:.1f} min")
    print(f"{'='*60}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
