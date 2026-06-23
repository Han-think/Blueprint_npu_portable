"""
generate_reverse.py -- 역설계 분석 학습 데이터 생성
====================================================

기존 keep 블루프린트를 입력으로, 7가지 역설계 분석 태스크의
학습 데이터를 LLM으로 생성한다. 순방향(생성) + 역방향(분석)
데이터가 합쳐져야 진짜 설계 전문 모델이 된다.

분석 태스크:
  1. structural  — 구조 취약점 + 보강 제안 (FEA 관점)
  2. thermal     — 열경로 병목 + 냉각 개선 (CFD 관점)
  3. dfa         — 조립 효율 + 서비스성 개선 (DFA/DFM)
  4. fmea        — 고장 모드 + 심각도 + 대책 (FMEA)
  5. cost        — 원가 절감 + 대안 재료/공정
  6. weight      — 경량화 기회 + 토폴로지 힌트
  7. tolerance   — 공차 체인 + 누적 위험 + fit 개선

Usage:
  python generate_reverse.py --tasks all --max 50     # 50개 역분석 생성
  python generate_reverse.py --tasks structural,thermal --seed cubesat
  python generate_reverse.py --dry-run                # 대상 목록만
  python generate_reverse.py --stats                  # 현재 역분석 데이터 통계

Env: BP_LM_URL, BP_LM_MODEL (generate_batch.py와 동일)
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO = Path(__file__).resolve().parent
CURATION_LOG = REPO / "30_model" / "curation" / "curation_log.jsonl"
REVERSE_LOG = REPO / "30_model" / "curation" / "reverse_log.jsonl"

LM_URL = os.environ.get("BP_LM_URL", "http://127.0.0.1:1234/v1").rstrip("/")
LM_MODEL = os.environ.get("BP_LM_MODEL", "")
LM_API_KEY = os.environ.get("BP_LM_API_KEY", "")

TASK_LIST = ["structural", "thermal", "dfa", "fmea", "cost", "weight", "tolerance"]

# ── 역설계 분석 태스크 정의 ─────────────────────────────────────────────────

REVERSE_TASKS = {
    "structural": {
        "name": "Structural Weakness Analysis",
        "system": (
            "You are Blueprint XPU Reverse Engineering Analyst — structural domain. "
            "Given a subsystem blueprint JSON, perform FEA-grade structural review. "
            "Output ONLY raw JSON, no prose.\n\n"
            "Output schema:\n"
            '{"analysis_type":"structural", "seed":"<seed>", "part_label":"<label>",\n'
            ' "load_paths": [{path, critical_section, stress_type, margin_pct}],\n'
            ' "weak_points": [{location_mm:[x,y,z], failure_mode, severity:low|med|high, '
            'fos_local:number}],\n'
            ' "reinforcement_suggestions": [{target, action:add_rib|thicken_wall|add_gusset|change_material|add_fillet, '
            'delta_mass_g, fos_improvement_pct, priority:1-5}],\n'
            ' "mesh_hints": {element_type:tet4|hex8|shell4, min_size_mm, refinement_zones:[{at,reason}]}}'
        ),
    },
    "thermal": {
        "name": "Thermal Path Analysis",
        "system": (
            "You are Blueprint XPU Reverse Engineering Analyst — thermal/CFD domain. "
            "Given a subsystem blueprint JSON, identify thermal bottlenecks and suggest improvements. "
            "Output ONLY raw JSON, no prose.\n\n"
            "Output schema:\n"
            '{"analysis_type":"thermal", "seed":"<seed>", "part_label":"<label>",\n'
            ' "heat_sources": [{location_mm, W_dissipated, component}],\n'
            ' "heat_sinks": [{location_mm, mechanism:conduction|convection|radiation, capacity_W}],\n'
            ' "thermal_bottlenecks": [{from_component, to_component, resistance_C_per_W, '
            'limiting_feature, severity:low|med|high}],\n'
            ' "improvements": [{action:add_thermal_strap|add_vent|increase_contact_area|change_material|add_heat_pipe, '
            'target, delta_temp_C, priority:1-5}],\n'
            ' "cfd_setup": {domain_mm:[x,y,z], inlet_faces:[], outlet_faces:[], '
            'wall_bc:[{face,type:adiabatic|fixed_T|heat_flux,value}]}}'
        ),
    },
    "dfa": {
        "name": "Design for Assembly / Disassembly Review",
        "system": (
            "You are Blueprint XPU Reverse Engineering Analyst — DFA/DFM domain. "
            "Given a subsystem blueprint JSON, analyze assembly efficiency and serviceability. "
            "Output ONLY raw JSON, no prose.\n\n"
            "Output schema:\n"
            '{"analysis_type":"dfa", "seed":"<seed>", "part_label":"<label>",\n'
            ' "assembly_score": {total_steps, total_time_min, unique_tools, '
            'boothroyd_efficiency_pct},\n'
            ' "problem_steps": [{step, issue:blind_fastener|tight_clearance|special_tool|'
            'sequence_dependency|no_datum, severity:low|med|high, suggestion}],\n'
            ' "service_access": [{component, current_method, time_min, improved_method, '
            'time_saved_min}],\n'
            ' "part_consolidation": [{merge_candidates:[], current_count, proposed_count, '
            'method:snap_fit|living_hinge|overmold|print_in_place, risk}],\n'
            ' "disassembly_sequence": [{step, action, target, tool, '
            'reusable:true|false, notes}]}'
        ),
    },
    "fmea": {
        "name": "Failure Mode & Effects Analysis",
        "system": (
            "You are Blueprint XPU Reverse Engineering Analyst — reliability/FMEA domain. "
            "Given a subsystem blueprint JSON, perform systematic FMEA. "
            "Output ONLY raw JSON, no prose.\n\n"
            "Output schema:\n"
            '{"analysis_type":"fmea", "seed":"<seed>", "part_label":"<label>",\n'
            ' "failure_modes": [{\n'
            '   "id":"FM01", "component":"<child_feature>",\n'
            '   "mode":"fatigue_crack|corrosion|wear|overload|thermal_distortion|loosening|seal_leak|harness_chafe",\n'
            '   "effect":"loss_of_function|degraded_performance|safety_hazard|cascading_failure",\n'
            '   "cause":"cyclic_load|environment|assembly_error|material_defect|design_flaw",\n'
            '   "severity":1-10, "occurrence":1-10, "detection":1-10, "rpn":number,\n'
            '   "current_control":"<existing mitigation from blueprint>",\n'
            '   "recommended_action":"<specific design change>",\n'
            '   "target_rpn":number\n'
            ' }],\n'
            ' "critical_items": [{fm_id, justification}],\n'
            ' "inspection_plan": [{component, method:visual|NDT|dimensional|functional, '
            'interval, acceptance_criteria}]}'
        ),
    },
    "cost": {
        "name": "Cost Optimization Analysis",
        "system": (
            "You are Blueprint XPU Reverse Engineering Analyst — cost/value engineering domain. "
            "Given a subsystem blueprint JSON, identify cost reduction opportunities. "
            "Output ONLY raw JSON, no prose.\n\n"
            "Output schema:\n"
            '{"analysis_type":"cost", "seed":"<seed>", "part_label":"<label>",\n'
            ' "current_estimate": {material_usd, process_usd, assembly_usd, total_usd, '
            'batch_size_assumed},\n'
            ' "cost_drivers": [{item, pct_of_total, reason:material_grade|tight_tolerance|'
            'complex_geometry|special_process|low_volume}],\n'
            ' "reductions": [{target, change:material_substitution|loosen_tolerance|'
            'simplify_geometry|change_process|redesign_for_volume, '
            'savings_pct, risk:low|med|high, min_order_qty}],\n'
            ' "make_vs_buy": [{component, recommendation:make|buy|hybrid, rationale, '
            'estimated_delta_usd}],\n'
            ' "value_engineering": [{function, current_cost_usd, '
            'alternative_approach, new_cost_usd}]}'
        ),
    },
    "weight": {
        "name": "Weight Optimization Analysis",
        "system": (
            "You are Blueprint XPU Reverse Engineering Analyst — lightweight design domain. "
            "Given a subsystem blueprint JSON, identify mass reduction opportunities. "
            "Output ONLY raw JSON, no prose.\n\n"
            "Output schema:\n"
            '{"analysis_type":"weight", "seed":"<seed>", "part_label":"<label>",\n'
            ' "current_mass_g": number,\n'
            ' "mass_breakdown": [{feature, mass_g, pct_of_total, '
            'structural_role:primary_load|secondary|non_structural}],\n'
            ' "lightweighting": [{\n'
            '   "target":"<feature>", "method":"topology_opt|lattice_infill|'
            'pocket_milling|rib_pattern|material_swap|wall_thinning|hollow_section",\n'
            '   "current_g":number, "proposed_g":number, "savings_g":number,\n'
            '   "fos_impact":"none|minor_reduction|needs_verification",\n'
            '   "manufacturability":"easy|moderate|requires_AM",\n'
            '   "priority":1-5\n'
            ' }],\n'
            ' "topology_zones": [{region_mm:[x0,y0,z0,x1,y1,z1], '
            'keep_constraint:load_path|interface|datum, design_space_pct}],\n'
            ' "target_mass_g": number, "achievable_reduction_pct": number}'
        ),
    },
    "tolerance": {
        "name": "Tolerance Chain Analysis",
        "system": (
            "You are Blueprint XPU Reverse Engineering Analyst — dimensional/GD&T domain. "
            "Given a subsystem blueprint JSON, analyze tolerance chains and fit risks. "
            "Output ONLY raw JSON, no prose.\n\n"
            "Output schema:\n"
            '{"analysis_type":"tolerance", "seed":"<seed>", "part_label":"<label>",\n'
            ' "datum_scheme": {primary, secondary, tertiary, reasoning},\n'
            ' "tolerance_chains": [{\n'
            '   "chain_id":"TC01", "from_datum":"<datum>", "to_feature":"<mating face>",\n'
            '   "links": [{feature, nominal_mm, tolerance_mm, contributor_type:'
            'dimension|form|position|runout}],\n'
            '   "stack_up_mm": number, "worst_case_mm": number, "rss_mm": number,\n'
            '   "fit_class":"<current>", "gap_or_interference_mm": number,\n'
            '   "risk": "ok|tight|interference_risk|excessive_gap"\n'
            ' }],\n'
            ' "improvements": [{chain_id, action:tighten|loosen|add_datum|'
            'change_fit_class|add_shim|redesign_interface, '
            'target_feature, rationale, cost_impact:lower|same|higher}],\n'
            ' "gdt_callouts": [{feature, symbol:position|flatness|perpendicularity|'
            'runout|concentricity, value_mm, datum_ref}]}'
        ),
    },
}


# ── LM 호출 ────────────────────────────────────────────────────────────────
def lm_call(system, user, temperature=0.4):
    import urllib.request
    body = {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
        "max_tokens": 3000,
        "stream": False,
    }
    if LM_MODEL:
        body["model"] = LM_MODEL
    headers = {"Content-Type": "application/json"}
    if LM_API_KEY:
        headers["Authorization"] = f"Bearer {LM_API_KEY}"
    req = urllib.request.Request(f"{LM_URL}/chat/completions",
                                data=json.dumps(body).encode(), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        return None


def extract_json(text):
    if not text:
        return None
    t = text.strip()
    if t.startswith("{"):
        try:
            return json.loads(t)
        except Exception:
            pass
    import re
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except Exception:
            pass
    s, e = text.find("{"), text.rfind("}")
    if s != -1 and e > s:
        try:
            return json.loads(text[s:e + 1])
        except Exception:
            pass
    return None


# ── keep 블루프린트 로드 ───────────────────────────────────────────────────
def load_keep_rows(seed_filter=""):
    if not CURATION_LOG.exists():
        return []
    rows = []
    for line in CURATION_LOG.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
            if str(r.get("decision", "")).lower() != "keep":
                continue
            if seed_filter and r.get("seed") != seed_filter:
                continue
            rows.append(r)
        except Exception:
            pass
    return rows


def load_existing_ids():
    ids = set()
    if REVERSE_LOG.exists():
        for line in REVERSE_LOG.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
                ids.add(r.get("id", ""))
            except Exception:
                pass
    return ids


def _compact_cad_brief(cb):
    """Extract only key fields from cad_brief to save tokens."""
    if not cb:
        return {}
    return {k: cb[k] for k in ("material", "process", "tolerance_mm", "finish",
                                "assembly_sequence", "fit_class") if k in cb}


def _compact_verify(v):
    """Keep first 2 verify items, strip verbose fields."""
    if not v:
        return []
    items = v[:2] if isinstance(v, list) else [v]
    out = []
    for item in items:
        if isinstance(item, dict):
            out.append({k: item[k] for k in ("check", "result", "value", "limit",
                                               "boundary_conditions") if k in item})
        else:
            out.append(item)
    return out


def blueprint_summary(row):
    """Extract a compact blueprint representation for the LLM input.
    Keeps total prompt under ~6000 tokens so LLM has room to respond."""
    payload = row.get("payload") or {}
    parts = payload.get("parts") or []
    vehicle = payload.get("vehicle") or {}

    summary_parts = []
    for p in parts[:13]:
        bp = p.get("blueprint") or {}
        children = (bp.get("part_tree") or {}).get("children") or []
        summary_parts.append({
            "label": p.get("label", ""),
            "child_count": len(children),
            "geometry_ops_count": len(bp.get("geometry_ops") or []),
            "cad_brief": _compact_cad_brief(bp.get("cad_brief", {})),
            "verify": _compact_verify(bp.get("verify", [])),
            "risk": (bp.get("risk") or [])[:2],
        })

    return {
        "vehicle": {"label": vehicle.get("label"), "desc": vehicle.get("desc"),
                     "material": vehicle.get("material"), "envelope": vehicle.get("envelope")},
        "seed": row.get("seed"),
        "engineering_scorecard": row.get("engineering_scorecard", {}),
        "parts": summary_parts,
    }


# ── 역분석 1건 생성 ───────────────────────────────────────────────────────
def generate_reverse_analysis(row, task_key, log):
    task = REVERSE_TASKS[task_key]
    summary = blueprint_summary(row)
    seed = row.get("seed", "unknown")

    user_prompt = (
        f"Analyze this {seed} subsystem assembly blueprint.\n"
        f"Task: {task['name']}\n\n"
        f"Blueprint data:\n{json.dumps(summary, ensure_ascii=False)}"
    )

    raw = lm_call(task["system"], user_prompt, temperature=0.35)
    analysis = extract_json(raw)
    if not analysis:
        log(f"    failed to parse {task_key} response")
        return None

    row_id = f"rev-{task_key}-{seed}-{int(time.time()*1000)}-{random.randint(100,999)}"
    rev_row = {
        "id": row_id,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "kind": "reverse_analysis",
        "task": task_key,
        "task_name": task["name"],
        "seed": seed,
        "source_id": row.get("id", ""),
        "source_grade": (row.get("engineering_scorecard") or {}).get("grade"),
        "decision": "keep",
        "messages": [
            {"role": "system", "content": f"You are Blueprint XPU reverse engineering analyst. "
             f"Given a blueprint, perform {task['name']} and output structured JSON analysis."},
            {"role": "user", "content": f"Analyze this {seed} blueprint for {task['name']}.\n"
             f"Blueprint: {json.dumps(summary, ensure_ascii=False)}"},
            {"role": "assistant", "content": json.dumps(analysis, ensure_ascii=False)},
        ],
        "analysis": analysis,
    }
    return rev_row


_write_lock = threading.Lock()


def persist_reverse_row(rev_row):
    REVERSE_LOG.parent.mkdir(parents=True, exist_ok=True)
    with _write_lock:
        with REVERSE_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rev_row, ensure_ascii=False) + "\n")


# ── 통계 ──────────────────────────────────────────────────────────────────
def show_stats():
    if not REVERSE_LOG.exists():
        print("[reverse] no reverse_log.jsonl yet")
        return 0
    rows = []
    for line in REVERSE_LOG.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                rows.append(json.loads(line))
            except Exception:
                pass

    by_task = {}
    by_seed = {}
    for r in rows:
        t = r.get("task", "?")
        s = r.get("seed", "?")
        by_task[t] = by_task.get(t, 0) + 1
        by_seed[s] = by_seed.get(s, 0) + 1

    print(f"\n[reverse] total: {len(rows)} reverse analysis rows")
    print(f"\nby task:")
    for t in TASK_LIST:
        print(f"  {t:<15} {by_task.get(t, 0):>4}")
    print(f"\nby seed:")
    for s in sorted(by_seed):
        print(f"  {s:<25} {by_seed[s]:>4}")
    return 0


# ── main ──────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", default="all",
                    help="all | comma list (structural,thermal,dfa,fmea,cost,weight,tolerance)")
    ap.add_argument("--seed", default="", help="filter to specific seed")
    ap.add_argument("--max", type=int, default=50, help="max analyses to generate")
    ap.add_argument("--workers", type=int, default=int(os.environ.get("BP_WORKERS", "6")),
                    help="parallel workers (default: BP_WORKERS or 6)")
    ap.add_argument("--dry-run", action="store_true", help="list targets without generating")
    ap.add_argument("--stats", action="store_true", help="show current reverse_log stats")
    a = ap.parse_args()

    if a.stats:
        return show_stats()

    tasks = TASK_LIST if a.tasks == "all" else [t.strip() for t in a.tasks.split(",")]
    tasks = [t for t in tasks if t in REVERSE_TASKS]
    if not tasks:
        print("no valid tasks"); return 1

    keeps = load_keep_rows(a.seed)
    if not keeps:
        print(f"[reverse] no keep rows found{' for seed ' + a.seed if a.seed else ''}")
        return 1

    existing_ids = load_existing_ids()

    # build work queue: round-robin task x random keep rows
    queue = []
    random.shuffle(keeps)
    idx = 0
    for _ in range(a.max):
        task = tasks[idx % len(tasks)]
        row = keeps[idx % len(keeps)]
        queue.append((task, row))
        idx += 1

    print(f"[reverse] {len(queue)} analyses planned | tasks: {tasks} | source rows: {len(keeps)}")
    if a.dry_run:
        for i, (task, row) in enumerate(queue[:20]):
            print(f"  [{i+1}] {task} <- {row.get('seed')}/{row.get('id','')[:30]}")
        if len(queue) > 20:
            print(f"  ... and {len(queue)-20} more")
        return 0

    tally = {t: 0 for t in tasks}
    _tally_lock = threading.Lock()
    done_count = [0]
    t0 = time.time()
    workers = min(a.workers, len(queue))
    print(f"[reverse] workers: {workers}")

    def _run_one(idx, task, row):
        try:
            rev = generate_reverse_analysis(row, task, lambda m: print(m, flush=True))
            if rev:
                persist_reverse_row(rev)
                with _tally_lock:
                    tally[task] += 1
                    done_count[0] += 1
                    n = done_count[0]
                elapsed = time.time() - t0
                rate = n / elapsed if elapsed > 0 else 0
                eta_s = int((len(queue) - n) / rate) if rate > 0 else 0
                print(f"  [{n}/{len(queue)}] OK: {task} <- {row.get('seed','')[:10]}  "
                      f"({rate*60:.0f}/hr, ETA {eta_s//60}m{eta_s%60}s)")
            else:
                with _tally_lock:
                    done_count[0] += 1
                print(f"  [{done_count[0]}/{len(queue)}] SKIP: {task}")
        except Exception as e:
            with _tally_lock:
                done_count[0] += 1
            print(f"  [{done_count[0]}/{len(queue)}] ERROR: {task} - {e}")

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(_run_one, i, task, row) for i, (task, row) in enumerate(queue)]
        for f in as_completed(futures):
            pass

    total = sum(tally.values())
    print(f"\n{'='*50}")
    print(f"  REVERSE ANALYSIS COMPLETE: {total}/{len(queue)}")
    for t, c in tally.items():
        print(f"    {t}: {c}")
    print(f"  Time: {(time.time()-t0)/60:.1f} min")
    print(f"{'='*50}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
