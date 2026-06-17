"""
generate_batch.py -- headless mass generation runner (pod-ready, no browser)
============================================================================

Drives the SAME multi-pass design generation as the Minimal.html workbench, but
unattended from the CLI so a GPU pod can produce a large curated corpus.

Design principle (see plan PHASE B): REUSE downstream, PORT only generation.
- Generation passes (P0 -> S1 -> S2 -> S3 -> S4) + micro-pack injection + the
  granularity/geometry/interface rules are ported verbatim from Minimal.html.
- Bundle -> disk -> CAD audit -> corpus reuses serve.py functions + the STEP 1-4
  Python audit outputs (geometry_resolution / interference / beam-FE sizing) as
  the AUTO-CURATION gate. No JS scorecard is re-implemented.

Honest limits: cosmetic prompt context present in the UI (preset SVG hints,
category prose, dataset-contract dump) is omitted; the quality-driving rule
block + micro-pack + subsystem plan are preserved. Verify parity with
`--parity` against a UI-generated candidate before trusting at scale.

Usage:
  python generate_batch.py --seeds cubesat --n 1            # smoke (1 candidate)
  python generate_batch.py --seeds all --per-seed 5         # 5 per seed, round-robin
  python generate_batch.py --seeds cubesat,robot_arm --n 10 # 10 total across listed
  python generate_batch.py --inspect-vehicle cubesat        # print the BOM, exit
Env:
  BP_LM_URL   default http://127.0.0.1:1234/v1   (LM Studio OpenAI endpoint)
  BP_LM_MODEL default '' -> let the server pick the loaded model
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as _dt
import json
import os
import random
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent
SERVER_DIR = REPO / "10_execution" / "server"
CAD_DIR = REPO / "10_execution" / "cad"
PACKS = REPO / "20_dataset" / "packs"
OUT = CAD_DIR / "output"
VEHICLES_FILE = REPO / "20_dataset" / "seed_vehicles.json"
CKPT_FILE = REPO / "30_model" / "curation" / "batch_checkpoint.json"

LM_URL = os.environ.get("BP_LM_URL", "http://127.0.0.1:1234/v1").rstrip("/")
LM_MODEL = os.environ.get("BP_LM_MODEL", "")
LM_API_KEY = os.environ.get("BP_LM_API_KEY", "")
NUM_PREDICT = 8000
# 한 후보의 서브시스템을 동시에 생성하는 워커 수. vLLM처럼 배치 처리하는 서버에서 1>이면
# 동시 요청 → 배치 → 큰 속도이득. Ollama(직렬 서버)면 1로 두는 게 무난(이득 없음).
WORKERS = int(os.environ.get("BP_WORKERS", "1"))

sys.path.insert(0, str(SERVER_DIR))
import serve  # noqa: E402  (export_bundle_to_seed_dir, persist_curation_row, VEHICLE_TO_SEED)

SEED_LIST = ["cubesat", "robot_arm", "tiltrotor", "small_launch_vehicle",
             "long_range_recon_wing", "haptic_glove"]

# ── 프롬프트 (Minimal.html에서 verbatim 포팅) ────────────────────────────────
P0_PLAN_SYS = (
    "You are Blueprint XPU, an assembly-subsystem planning assistant. Output ONLY raw JSON, "
    "no prose, no markdown fences, no explanation.\n\n"
    "Stage P0: before CAD generation, make a compact engineering plan for one subsystem inside a full assembly.\n"
    "Rules:\n"
    '- schema must be exactly "blueprint_npu_subsystem_plan_v1"\n'
    "- Plan the subsystem as part of the vehicle, not as an isolated single part.\n"
    "- Include 5 to 9 internal_features that later must appear in part_tree and geometry_ops.\n"
    "- Include at least 3 adjacent_interfaces to neighboring modules, service paths, or mounting datums; each must "
    "name a connection_type (bolted/snap_fit/press_fit/revolute_bearing/band_clamp/connector_mate/harness_passthrough/...), "
    "its dof, a clearance_mm, and an assembly_order_hint.\n"
    "- Prefer reciprocal interface naming: if this subsystem mates to a neighbor, name the exact neighbor label and the "
    "feature that the neighbor should declare back.\n"
    "- Include physics_paths that explain load, flow, thermal, motion, pressure, electrical/data, or human/service access paths.\n"
    "- Include manufacturing_strategy with process, datum, tolerance, support/orientation, and inspection implications.\n"
    "- Coordinate hints must be plausible local regions or [x_mm, y_mm, z_mm] arrays.\n"
    "- Keep strings concise. Use real feature names, not generic placeholders."
)

S1_SYS = (
    "You are Blueprint XPU, a mechanical CAD design assistant. Your output is ONLY raw JSON - no prose, no markdown "
    "fences, no explanation. Just a single JSON object.\n\n"
    'Stage 1: analyze the design brief, then output the "brief" and "part_tree" sections of a blueprint.\n'
    "Rules:\n"
    '- version must be exactly the string "bp-npu-r6"\n'
    "- ts must be a valid ISO 8601 datetime string\n"
    "- brief.constraints.process must be exactly one of: FDM, SLA, LPBF, DED, BinderJet\n"
    "- part_tree must have: id (string), name (string), qty (integer >= 1), children (array)\n"
    "- For assembly-subsystem design, decompose the subsystem into 5-9 meaningful internal child features when possible.\n"
    "- Every P0 internal_feature_target from the supplied subsystem plan must appear as a named part_tree child or synonym.\n"
    "- Include children for service access, inspection window/callout, primary datum, fastener/insert/washer feature, "
    "and harness/connector path when relevant.\n"
    "- Child features should be physical/functional features, not vague labels.\n"
    "- Avoid one-piece or shallow part_tree outputs; sparse part_tree will be rejected as training-poor."
)

S2_SYS = (
    "You are Blueprint XPU. Output ONLY raw JSON - no prose, no markdown, no explanation.\n\n"
    'Stage 2: given design context, output "geometry_ops" and "cad_brief".\n'
    "Rules:\n"
    "- geometry_ops[].op must be exactly one of: cylinder box sphere shell extrude revolve sweep loft fillet chamfer "
    "drill boss pocket pattern_polar pattern_linear channel engrave mirror union subtract intersect\n"
    "- geometry_ops must contain 12 to 24 operations for generated assembly subsystem parts\n"
    "- include at least: 1 main body op, 3 interface/mounting ops, 3 subtract/drill/pocket/channel ops, 2 fillet/chamfer "
    "ops, 1 pattern op when repeated fasteners/holes exist, and 1 label/engrave op\n"
    "- every important sub-part from the part_tree should be represented by at least one geometry operation\n"
    "- every P0 internal_feature_target and every important part_tree child must map to at least one geometry_ops[].id "
    "or geometry_ops[].target using the same meaningful words\n"
    "- every geometry op that creates or modifies a physical feature must include args.at as [x_mm, y_mm, z_mm] in "
    "millimeters, centered on the vehicle/subsystem local datum\n"
    "- every op should include useful dimensions such as x_mm/y_mm/z_mm, d_mm/h_mm, radius_mm, depth_mm, w_mm/l_mm, "
    "or count/radius_mm for patterns\n"
    "- coordinate placement must be physically distributed across the subsystem, not all [0,0,0]\n"
    "- avoid generic box-first layouts unless the real subsystem is rectangular; rockets/nozzles/tanks/airframes/rotors/"
    "gears must use curved or swept operations such as cylinder, revolve, loft, sweep, pattern_polar, channel\n"
    "- include physical service/inspection evidence as geometry: removable cover, pocket, channel, hatch/window, port, callout engrave\n"
    "- for every critical joint, include locking/preload evidence in geometry or cad_brief\n"
    "- cad_brief.rev must match pattern \\d+\\.\\d+(\\.\\d+)?\n"
    "- cad_brief requires: name, rev, material, envelope_mm ([x,y,z] numbers), build_direction, mass_est_g"
)

S3_SYS = (
    "You are Blueprint XPU. Output ONLY raw JSON - no prose, no markdown, no explanation.\n\n"
    'Stage 3: output "verify" (verification checks) and "risk" (risk register).\n'
    "Rules:\n"
    "- verify[].result must be exactly one of: pass, warn, fail\n"
    "- risk[].id must match ^R\\d+$\n"
    "- risk[].severity must be exactly one of: low, med, high\n"
    "- risk array must have at most 5 items\n"
    "- Each risk item needs: id, desc, mit\n"
    "- Include checks for schema completeness, mass budget, P0-to-geometry traceability, interface reciprocity, "
    "and fastener locking/preload evidence."
)

S4_SYS = (
    "You are Blueprint XPU. Output ONLY raw JSON - no prose, no markdown, no explanation.\n\n"
    'Stage 4: output "print_profile" and "slicer_job".\n'
    "Rules:\n"
    "- print_profile.supports must be exactly one of: none, tree, grid, block, min\n"
    "- slicer_job.tool must be exactly one of: prusaslicer, preform, eosprint, cura, ideamaker\n"
    "- slicer_job.input_stl and slicer_job.output must be plain file-path strings\n"
    "- Do NOT include sha256 unless you have a real 64-character lowercase hex string"
)

WORKSPACE_PREFIX = (
    "Reasoning: low\n\n"  # gpt-oss(harmony) reasoning budget directive; harmless to others
)


def now_iso():
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ── 프롬프트 빌더 (Minimal.html 포팅) ────────────────────────────────────────
def p0_plan_prompt(part_brief, vehicle, part):
    return (
        f"Vehicle assembly: {vehicle['label']}\n"
        f"Vehicle description: {vehicle['desc']}\n"
        f"Subsystem: {part['label']}\nSubsystem spec: {part['spec']}\n\n"
        f"Design context:\n{part_brief}\n\n"
        "Return JSON with: schema='blueprint_npu_subsystem_plan_v1', vehicle_id, part_id, subsystem_role, "
        "physics_paths[], adjacent_interfaces[] (>=3, each with target_part, interface_type, connection_type, dof, "
        "clearance_mm, assembly_order_hint, required_feature, coordinate_region), internal_features[] (5-9), "
        "internal_feature_targets[], integration_opportunities[], manufacturing_strategy{}, verification_focus[]."
    )


def s1_user_prompt(brief, hint=""):
    dom = f"\nDomain context: {hint}" if hint else ""
    return (
        f"Design brief: {brief}{dom}\n\n"
        'Output JSON: {"version":"bp-npu-r6","ts":"' + now_iso() + '","project":"<name>","object":"<name>",'
        '"brief":{"requirements":[...],"constraints":{"material":"<m>","process":"<FDM|SLA|LPBF|DED|BinderJet>",'
        '"envelope_mm":[x,y,z],"min_wall_mm":<n>,"overhang_deg":45,"tol_mm":0.2}},'
        '"part_tree":{"id":"asm-001","name":"<name>","qty":1,"children":['
        '{"id":"p-001","name":"<feature>","qty":1,"children":[]}, ...5-9 children...]}}'
    )


def s2_user_prompt(brief, merged):
    mat = (((merged.get("brief") or {}).get("constraints") or {}).get("material")) or "PETG"
    parts = ", ".join(n.get("name", "") for n in ((merged.get("part_tree") or {}).get("children") or []))
    return (
        f"Design brief: {brief}\n\nStage 1 context - object: \"{merged.get('object','')}\", material: {mat}\n"
        f"Parts: {parts}\n\n"
        'Output JSON with "geometry_ops" (12-24 ops, each {op,id,target?,args:{at:[x,y,z], plus dims like '
        'x_mm/y_mm/z_mm,d_mm/h_mm,radius_mm,depth_mm,w_mm/l_mm,count}}) and "cad_brief" '
        '{name,rev:"1.0",material,envelope_mm:[x,y,z],build_direction:"+Z",key_dims_mm:{},'
        'wall_thickness_mm:{min,typ},tolerances_mm:{fit},mass_est_g}.'
    )


def s3_user_prompt(brief, merged):
    ops = ", ".join(o.get("op", "") for o in (merged.get("geometry_ops") or []))
    parts = ", ".join(n.get("name", "") for n in ((merged.get("part_tree") or {}).get("children") or []))
    return (
        f"Design brief: {brief}\n\nParts: {parts}\nGeometry ops: {ops or '(none)'}\n\n"
        'Output JSON: {"verify":[{"check":"...","result":"pass|warn|fail","value":"...","rule":"..."}, ...>=2],'
        '"risk":[{"id":"R01","desc":"...","mit":"...","severity":"low|med|high"}, ...1-5]}'
    )


def s4_user_prompt(brief, merged):
    mat = (((merged.get("brief") or {}).get("constraints") or {}).get("material")) or "PETG"
    obj = str(merged.get("object", "part")).lower().replace(" ", "-")
    return (
        f"Design brief: {brief}\nMaterial: {mat}\n\n"
        'Output JSON: {"print_profile":{"printer":"...","material":"' + mat + '","layer_mm":0.2,'
        '"supports":"none|tree|grid|block|min","orientation":"+Z","est_time":"2h30m","filament_g":<n>,"walls":3,'
        '"infill":"gyroid 20%"},"slicer_job":{"tool":"prusaslicer","input_stl":"output/' + obj + '.stl",'
        '"output":"output/' + obj + '.gcode","args":["--load","profile.ini","--export-gcode"],'
        '"profile":"' + mat + '_standard.ini"}}'
    )


# ── micro-pack (디스크에서 직접 로드; serve /packs 라우트 불필요) ────────────
_PACK_CACHE = {}


def load_pack(seed, fname):
    key = f"{seed}/{fname}"
    if key not in _PACK_CACHE:
        p = PACKS / seed / fname
        try:
            _PACK_CACHE[key] = json.loads(p.read_text(encoding="utf-8")) if p.exists() else None
        except Exception:
            _PACK_CACHE[key] = None
    return _PACK_CACHE[key]


def pack_tokens(s):
    out = []
    for w in str(s or "").lower().replace("_", " ").replace("/", " ").split():
        w = "".join(c for c in w if c.isalnum())
        if len(w) >= 3:
            out.append(w)
    return out


def match_subsystem_for_part(skeleton, part):
    subs = (skeleton or {}).get("required_subsystems") or []
    if not subs:
        return None
    part_tok = set(pack_tokens(f"{part['label']} {part['spec']}"))
    best, best_score = None, 0
    for sub in subs:
        sub_tok = pack_tokens(f"{sub.get('id','')} {sub.get('discipline','')} {sub.get('function','')} "
                              f"{' '.join(sub.get('evidence_features') or [])}")
        score = sum(1 for t in sub_tok if t in part_tok)
        if score > best_score:
            best_score, best = score, sub
    return dict(best, _match_score=best_score) if best and best_score >= 2 else None


def micro_pack_clause(pack):
    if not pack or not pack.get("subsystem"):
        return ""
    sub = pack["subsystem"]
    lines = [
        "ENGINEERING MICRO-PACK (PASS-1, design only this subsystem):",
        f"- discipline: {sub.get('discipline')} - role: {sub.get('function')}",
        f"- required evidence_features (each must appear in part_tree/geometry_ops): "
        f"{', '.join(sub.get('evidence_features') or [])}",
    ]
    for doc in pack.get("criteria") or []:
        for c in doc.get("criteria") or []:
            lines.append(f"- [{c.get('criterion')}] good: {c.get('good')} | bad: {c.get('bad')}")
    if pack.get("boundary_note"):
        lines.append(f"- BOUNDARY: {pack['boundary_note']}")
    lines.append("Do not modify other subsystems or the global envelope; respect interfaces from the skeleton.")
    return "\n".join(lines)


# ── 생성 규칙 블록 (Minimal.html synthesizeAssemblySubsystem 포팅) ───────────
RULES = (
    "Output target: detailed manufacturable assembly-subsystem blueprint, not a standalone single-part choice and not "
    "a generic block. It must fit the complete vehicle architecture.\n"
    "Granularity rule: decompose this subsystem into 5-9 meaningful internal child features in part_tree when possible "
    "(shell/body, flange/interface, fastener pattern, channel/duct, rib/stiffener, seal/gasket, sensor/avionics pocket, "
    "service access, mounting datum, harness/pipe interface).\n"
    "Geometry rule: represent those internal features with 12-24 explicit coordinate-bearing geometry_ops, not prose. "
    "Every physical feature must include args.at [x,y,z] and real dimensions, distributed across the local subsystem "
    "volume; do not stack all features at the origin.\n"
    "Interface rule: include at least three adjacent-module interfaces or mounting datums and at least three "
    "negative/service features such as holes, pockets, ducts, channels, ports, or access cuts.\n"
    "Reciprocal interface rule: name exact neighboring subsystem labels when they mate, and choose "
    "connection_type + DOF + clearance_mm + required_feature so the neighbor can declare the same joint family back.\n"
    "Budget rule: cad_brief.mass_est_g must be a numeric grams value, and verify must include a mass/budget check.\n"
    "Joint evidence rule: critical joints need visible insert/washer/locking/preload evidence and torque_Nm or preload intent.\n"
    "Training-quality rule: make part_tree children and geometry_ops mutually traceable by id/name."
)


def build_part_brief(vehicle, part, micro_clause):
    return (
        f"Subsystem module: {part['label']} (fixed BOM item inside {vehicle['label']})\n"
        f"Spec: {part['spec']}\n"
        f"Vehicle context: {vehicle['desc']}\n"
        f"Suggested material: {vehicle.get('material','PETG')}, process: {vehicle.get('process','FDM')}\n"
        f"{micro_clause}\n{RULES}"
    )


# ── JSON 추출 (Minimal.html extractJSON 포팅) ────────────────────────────────
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


# ── stage 출력 약함 검사 (Minimal.html stageOutputIssues 포팅, 재시도 게이트) ─
def stage_issues(stage, obj):
    if not isinstance(obj, dict):
        return ["not an object"]
    iss = []
    if stage == "p0":
        if not str(obj.get("subsystem_role", "")).strip():
            iss.append("missing subsystem_role")
        if len(obj.get("adjacent_interfaces") or []) < 3:
            iss.append("requires >=3 adjacent_interfaces")
        if max(len(obj.get("internal_feature_targets") or []), len(obj.get("internal_features") or [])) < 5:
            iss.append("requires >=5 internal feature targets")
    elif stage == "s1":
        ch = (obj.get("part_tree") or {}).get("children") or []
        if not obj.get("brief") or not obj.get("part_tree"):
            iss.append("requires brief and part_tree")
        if len(ch) < 2:
            iss.append("requires >=2 child features")
    elif stage == "s2":
        ops = obj.get("geometry_ops") or []
        coord = sum(1 for o in ops if isinstance((o or {}).get("args", {}).get("at"), list))
        if len(ops) < 8:
            iss.append("requires >=8 geometry operations")
        if coord < 5:
            iss.append("requires coordinate-bearing ops (args.at)")
        if not isinstance(obj.get("cad_brief"), dict):
            iss.append("requires cad_brief")
    elif stage == "s3":
        if len(obj.get("verify") or []) < 2:
            iss.append("requires verify checks")
        if len(obj.get("risk") or []) < 1:
            iss.append("requires >=1 risk")
    elif stage == "s4":
        if not isinstance(obj.get("print_profile"), dict):
            iss.append("requires print_profile")
        if not isinstance(obj.get("slicer_job"), dict):
            iss.append("requires slicer_job")
    return iss


# ── LM 호출 (Minimal.html lmStudioGenerateFull 포팅) ─────────────────────────
def lm_call(system, user, temperature):
    body = {
        "messages": [
            {"role": "system", "content": WORKSPACE_PREFIX + system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
        "max_tokens": NUM_PREDICT,
        "stream": False,
    }
    if LM_MODEL:
        body["model"] = LM_MODEL
    data = json.dumps(body).encode("utf-8")
    hdrs = {"Content-Type": "application/json"}
    if LM_API_KEY:
        hdrs["Authorization"] = f"Bearer {LM_API_KEY}"
    req = urllib.request.Request(f"{LM_URL}/chat/completions", data=data, headers=hdrs)
    with urllib.request.urlopen(req, timeout=900) as r:
        resp = json.loads(r.read().decode("utf-8"))
    msg = (resp.get("choices") or [{}])[0].get("message") or {}
    text = msg.get("content") or ""
    if "{" not in text:  # reasoning 채널 구제
        think = msg.get("reasoning_content") or msg.get("reasoning") or ""
        if "{" in think:
            text = f"{text}\n{think}"
    return text


def generate_with_retry(system, user, stage, temp_base, max_retries=2):
    last = None
    note = ""
    for attempt in range(max_retries + 1):
        temp = max(0.15, temp_base * (0.65 ** attempt))
        try:
            text = lm_call(system, user + note, temp)
        except Exception as e:
            note = f"\n\nERROR: {e}. Output corrected JSON only."
            continue
        obj = extract_json(text)
        if obj is None:
            note = "\n\nERROR: no valid JSON found. Output a single raw JSON object only."
            continue
        iss = stage_issues(stage, obj)
        if iss and attempt < max_retries:
            note = "\n\nERROR: previous output was weak:\n" + "\n".join(f"- {i}" for i in iss[:4]) + \
                   "\nFix these and output corrected JSON only."
            last = obj
            continue
        return obj
    return last


# ── 한 서브시스템 생성 (P0->S1->S2->S3->S4 병합) ─────────────────────────────
def synthesize_subsystem(vehicle, part, seed, log):
    skeleton = load_pack(seed, "skeleton.json")
    matched = match_subsystem_for_part(skeleton, part) if skeleton else None
    micro_clause = ""
    if matched:
        mp = load_pack(seed, f"{matched['id']}.json")
        if mp:
            micro_clause = "\n" + micro_pack_clause(mp) + "\n"
            log(f"    micro-pack <- {matched['id']} ({matched.get('discipline')})")
    part_brief = build_part_brief(vehicle, part, micro_clause)

    plan = generate_with_retry(P0_PLAN_SYS, p0_plan_prompt(part_brief, vehicle, part), "p0", 0.45)
    staged = part_brief + (f"\nSubsystem planning output:\n{json.dumps(plan, ensure_ascii=False)}\n" if plan else "")

    merged = {}
    s1 = generate_with_retry(S1_SYS, s1_user_prompt(staged), "s1", 0.5)
    if s1:
        merged = s1
    s2 = generate_with_retry(S2_SYS, s2_user_prompt(staged, merged), "s2", 0.4)
    if s2:
        if s2.get("geometry_ops"):
            merged["geometry_ops"] = s2["geometry_ops"]
        if s2.get("cad_brief"):
            merged["cad_brief"] = s2["cad_brief"]
    s3 = generate_with_retry(S3_SYS, s3_user_prompt(staged, merged), "s3", 0.4)
    if s3:
        merged["verify"] = s3.get("verify", merged.get("verify"))
        merged["risk"] = s3.get("risk", merged.get("risk"))
    s4 = generate_with_retry(S4_SYS, s4_user_prompt(staged, merged), "s4", 0.4)
    if s4:
        merged["print_profile"] = s4.get("print_profile", merged.get("print_profile"))
        merged["slicer_job"] = s4.get("slicer_job", merged.get("slicer_job"))

    merged["_subsystem_plan"] = plan
    merged.setdefault("cad_brief", {}).setdefault("material", vehicle.get("material", "PETG"))
    n_ops = len(merged.get("geometry_ops") or [])
    log(f"    {part['label']}: ops {n_ops} · parts {len((merged.get('part_tree') or {}).get('children') or [])}")
    return merged, plan, n_ops


# ── 자동 큐레이션 게이트 (STEP1~4 Python 출력 재사용) ────────────────────────
def read_reports(seed):
    base = OUT / f"{seed}_generated"

    def rj(p):
        try:
            return json.loads((base / p).read_text(encoding="utf-8"))
        except Exception:
            return {}
    interference = rj("assembly_interference_report.json")
    analysis = rj("analysis_report.json")
    resolution = rj("geometry_resolution.json")
    return interference, analysis, resolution


def auto_decision(parts_total, parts_ok, interference, analysis, resolution):
    blocked = (interference.get("counts") or {}).get("blocked_pairs", 0)
    low_res = resolution.get("low_res_parts") or []
    sizing = analysis.get("sizing") or {}
    fos = sizing.get("solver_fos", sizing.get("worst_fos"))
    status = analysis.get("status")
    # REJECT는 '모델이 책임지는 결함'만: 무효/불완전/LOW-RES(ops 부족).
    # blocked_pairs는 우리 조립 배치(코드)가 만든 간섭이라 모델 설계 품질이 아님 →
    # 자동 reject가 아니라 HOLD(사람 검토)로 분류한다(정직: 배치 탓임을 명시).
    reasons = []
    if parts_ok < parts_total:
        reasons.append(f"incomplete: {parts_ok}/{parts_total} parts got a blueprint")
    if low_res:
        reasons.append(f"LOW-RES parts {low_res} (model gave too few ops)")
    if reasons:
        return "reject", "; ".join(reasons)
    if status == "ok" and isinstance(fos, (int, float)) and fos >= 1.5:
        note = f"FoS {fos}, analysis ok"
        if blocked and blocked > 0:
            note += f" · blocked {blocked} (our placement, not design - review layout)"
        return "keep", note
    return "hold", f"mid: blocked {blocked}, FoS {fos}, status {status}"


# ── 한 후보(어셈블리) 생성 + audit + 게이트 + persist ────────────────────────
def run_candidate(seed, vehicle, gen_seed, log):
    run_meta = {"seed": gen_seed, "model": LM_MODEL or "lmstudio", "generator": "generate_batch.py",
                "started": now_iso()}
    t0 = time.time()
    parts = vehicle["parts"]
    # 팩 prewarm: 스레드 진입 전 단일 스레드에서 캐시 채움(캐시 레이스 방지).
    sk = load_pack(seed, "skeleton.json")
    if sk:
        for part in parts:
            m = match_subsystem_for_part(sk, part)
            if m:
                load_pack(seed, f"{m['id']}.json")

    def work(item):
        i, part = item
        log(f"  [{i+1}/{len(parts)}] {part['label']}")
        try:
            bp, _plan, n_ops = synthesize_subsystem(vehicle, part, seed, log)
            ok = n_ops >= 1 and bool((bp.get("part_tree") or {}).get("children"))
        except Exception as e:
            log(f"    ! {part['label']} failed: {e}")
            bp, ok = None, False
        return i, part, bp, ok

    results = [None] * len(parts)
    if WORKERS > 1:           # 동시 생성 (vLLM 배치 활용)
        with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as ex:
            for i, part, bp, ok in ex.map(work, list(enumerate(parts))):
                results[i] = (part, bp, ok)
    else:                     # 순차 (Ollama 등)
        for item in enumerate(parts):
            i, part, bp, ok = work(item)
            results[i] = (part, bp, ok)

    parts_ok = sum(1 for r in results if r and r[2])
    parts_out = [{"id": p["id"], "label": p["label"], "spec": p["spec"],
                  "subsystem_plan": (bp or {}).get("_subsystem_plan"), "blueprint": bp}
                 for (p, bp, ok) in results]

    bundle = {"schema": "blueprint_npu_assembly_curation_v1", "vehicle": vehicle,
              "run_meta": dict(run_meta, duration_s=round(time.time() - t0)),
              "parts": [p for p in parts_out if p.get("blueprint")]}
    if not bundle["parts"]:
        log("  candidate produced no usable parts — skipping")
        return None

    # 1) 디스크 저장 (serve.py 재사용)
    exp = serve.export_bundle_to_seed_dir(bundle)
    run_dir = exp["dir"]
    log(f"  exported -> {run_dir} ({exp['parts']} parts, {exp['joints']} joints)")

    # 2) CAD audit (run_full_pipeline subprocess)
    try:
        subprocess.run([sys.executable, "run_full_pipeline.py", seed, "--dir", run_dir],
                       cwd=str(CAD_DIR), timeout=1200, capture_output=True, text=True)
    except Exception as e:
        log(f"  audit pipeline error: {e}")

    interference, analysis, resolution = read_reports(seed)
    decision, why = auto_decision(len(vehicle["parts"]), parts_ok, interference, analysis, resolution)
    log(f"  AUTO-{decision.upper()}: {why}")

    # 3) corpus 적재 (실제 messages + payload)
    composite = {"part_tree": {"children": [{"id": p["id"], "name": p["label"]} for p in bundle["parts"]]},
                 "parts": [p["blueprint"] for p in bundle["parts"]]}
    row = {
        "id": f"gb-{seed}-{int(time.time()*1000)}-{random.randint(100,999)}",
        "ts": now_iso(), "kind": "assembly", "decision": decision, "seed": seed,
        "vehicle_id": vehicle["id"], "title": vehicle["label"],
        "run_meta": bundle["run_meta"],
        "engineering_scorecard": {"score": (analysis.get("score") if isinstance(analysis.get("score"), (int, float)) else None),
                                  "blocked_pairs": (interference.get("counts") or {}).get("blocked_pairs", 0),
                                  "sizing_fos": (analysis.get("sizing") or {}).get("solver_fos"),
                                  "auto_reason": why},
        "messages": [
            {"role": "system", "content": "You are Blueprint XPU. Given a vehicle assembly brief, output a "
             "schema_v6 multi-subsystem blueprint as raw JSON (part_tree + coordinate-bearing geometry_ops + "
             "cad_brief + verify + risk per subsystem). No prose."},
            {"role": "user", "content": f"Design brief: {vehicle['desc']}\nSeed: {seed}\n"
             f"Decompose into these subsystems and output the assembly blueprint JSON: "
             f"{', '.join(p['label'] for p in vehicle['parts'])}"},
            {"role": "assistant", "content": json.dumps(composite, ensure_ascii=False)},
        ],
        "payload": bundle,
    }
    res = serve.persist_curation_row(row)
    log(f"  corpus: {res.get('total')} total ({res.get('kept')} keep / {res.get('rejected')} reject)")
    return decision


# ── 체크포인트 ───────────────────────────────────────────────────────────────
def load_ckpt():
    try:
        return json.loads(CKPT_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"done": 0, "by_seed": {}}


def save_ckpt(ck):
    CKPT_FILE.parent.mkdir(parents=True, exist_ok=True)
    CKPT_FILE.write_text(json.dumps(ck, ensure_ascii=False, indent=1), encoding="utf-8")


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="all", help="all | comma list (e.g. cubesat,robot_arm)")
    ap.add_argument("--n", type=int, default=0, help="total candidates across selected seeds (round-robin)")
    ap.add_argument("--per-seed", type=int, default=0, help="candidates per seed (overrides --n)")
    ap.add_argument("--resume", action="store_true", help="continue from batch_checkpoint.json")
    ap.add_argument("--inspect-vehicle", default="", help="print the BOM for a seed and exit")
    a = ap.parse_args(argv[1:])

    vehicles = json.loads(VEHICLES_FILE.read_text(encoding="utf-8"))
    if a.inspect_vehicle:
        v = vehicles.get(a.inspect_vehicle)
        print(json.dumps(v, ensure_ascii=False, indent=2) if v else f"no vehicle for seed {a.inspect_vehicle}")
        return 0

    seeds = SEED_LIST if a.seeds == "all" else [s.strip() for s in a.seeds.split(",") if s.strip()]
    seeds = [s for s in seeds if s in vehicles]
    if not seeds:
        print("no valid seeds"); return 1

    # 작업 큐: per-seed 우선, 아니면 n개를 seed 라운드로빈
    queue = []
    if a.per_seed > 0:
        for s in seeds:
            queue += [s] * a.per_seed
    else:
        n = a.n or 1
        i = 0
        while len(queue) < n:
            queue.append(seeds[i % len(seeds)]); i += 1

    ck = load_ckpt() if a.resume else {"done": 0, "by_seed": {}}
    start = ck["done"] if a.resume else 0
    print(f"[batch] LM {LM_URL} · seeds {seeds} · {len(queue)} candidates · start at {start}")
    tally = {"keep": 0, "reject": 0, "hold": 0}
    for idx in range(start, len(queue)):
        seed = queue[idx]
        gen_seed = random.randint(1, 2_000_000)
        print(f"\n[{idx+1}/{len(queue)}] seed={seed} gen_seed={gen_seed}")
        try:
            decision = run_candidate(seed, vehicles[seed], gen_seed, lambda m: print(m, flush=True))
            if decision in tally:
                tally[decision] += 1
        except KeyboardInterrupt:
            print("\n[batch] interrupted — checkpoint saved"); save_ckpt(ck); return 130
        except Exception as e:
            print(f"  candidate error: {e}")
        ck["done"] = idx + 1
        ck["by_seed"][seed] = ck["by_seed"].get(seed, 0) + 1
        save_ckpt(ck)
    print(f"\n[batch] done · keep {tally['keep']} / reject {tally['reject']} / hold {tally['hold']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
