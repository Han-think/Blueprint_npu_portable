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
NUM_PREDICT = 12000
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
    "- For each adjacent_interface, include stack_up_mm (cumulative tolerance from assembly datum to mating face) "
    "and fit_class (e.g. H7/h6, LC2, LT3).\n"
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
    "- MANDATORY: decompose the subsystem into exactly 5-9 meaningful internal child features. "
    "Fewer than 5 children is ALWAYS rejected. Each child becomes a separate manufactured feature that will "
    "receive its own geometry_ops in the next stage.\n"
    "- Every P0 internal_feature_target from the supplied subsystem plan must appear as a named part_tree child or synonym.\n"
    "- Required child categories (include ALL that apply to this subsystem):\n"
    "  * primary body/shell/housing (the main structural shape)\n"
    "  * interface flange or mounting bracket (how it connects to neighbors)\n"
    "  * fastener pattern / insert / bolt circle\n"
    "  * internal channel, duct, or fluid path\n"
    "  * rib, stiffener, or structural reinforcement\n"
    "  * seal, gasket, or environmental barrier\n"
    "  * sensor pocket, avionics bay, or electronics cavity\n"
    "  * service access panel, inspection window, or maintenance port\n"
    "  * harness/cable/pipe routing path\n"
    "- Child features must be physical/functional, not vague labels. Name them specifically "
    "(e.g. 'bearing_seat' not 'feature_1', 'coolant_channel' not 'internal_feature').\n"
    "- Avoid one-piece or shallow part_tree; sparse trees are rejected as training-poor."
)

S2_SYS = (
    "You are Blueprint XPU. Output ONLY raw JSON - no prose, no markdown, no explanation.\n\n"
    'Stage 2: given design context, output "geometry_ops" and "cad_brief".\n'
    "Rules:\n"
    "- geometry_ops[].op must be exactly one of: cylinder box sphere shell extrude revolve sweep loft fillet chamfer "
    "drill boss pocket pattern_polar pattern_linear channel engrave mirror union subtract intersect\n"
    "- CRITICAL MINIMUM: every part_tree child must have AT LEAST 4 geometry_ops referencing it by target name. "
    "With N children, produce at least N*4 total ops (e.g. 7 children = 28+ ops). "
    "A child with only 1 op (like just 'nominal-part-body') triggers AUTOMATIC REJECTION as LOW-RES.\n"
    "- Per-child op recipe (minimum 4 each):\n"
    "  * 1 body/shape op: box, cylinder, shell, extrude, revolve, loft, or sweep\n"
    "  * 1 subtract op: drill, pocket, channel, or subtract\n"
    "  * 1 interface op: boss, pattern_polar, pattern_linear, or engrave\n"
    "  * 1 finish op: fillet, chamfer, or mirror\n"
    "  * Additional ops as needed to reach 4-8 per child\n"
    "- every P0 internal_feature_target and every part_tree child must map to geometry_ops[].target "
    "using the same name. Zero unmapped children allowed.\n"
    "- every geometry op must include args.at as [x_mm, y_mm, z_mm] in millimeters, centered on the "
    "vehicle/subsystem local datum. Coordinates must be physically distributed - no two children at identical coords.\n"
    "- every op must include real dimensions: x_mm/y_mm/z_mm, d_mm/h_mm, radius_mm, depth_mm, w_mm/l_mm, "
    "or count/radius_mm for patterns. No zero or placeholder dimensions.\n"
    "- geometry must match the physical form: rockets/nozzles/tanks use cylinder/revolve/loft, "
    "airframes/rotors use sweep/loft/pattern_polar, gears use pattern_polar, "
    "housings use box+pocket+drill, linkages use cylinder+boss+channel.\n"
    "- include physical service evidence as geometry: removable cover, inspection pocket, channel, port, engrave\n"
    "- for every critical joint, include locking/preload evidence in geometry or cad_brief\n"
    "- cad_brief.rev must match pattern \\d+\\.\\d+(\\.\\d+)?\n"
    "- cad_brief requires: name, rev, material, envelope_mm ([x,y,z] numbers), build_direction, mass_est_g\n"
    "- cad_brief must include assembly_sequence: ordered list of "
    "{step, action (install|fasten|align|press|route), target, tool, torque_Nm_or_force_N, datum}. "
    "Include disassembly_sequence for field-serviceable parts."
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
    "and fastener locking/preload evidence.\n"
    "- verify must include a boundary_conditions object: "
    "fixture_points [{at:[x,y,z], type:fixed|pinned|roller}], "
    "thermal_zones [{at:[x,y,z], W_or_degC:number, role:source|sink}], "
    "pressure_faces [{face:string, Pa:number}] for downstream CFD/FEA."
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
    children = (merged.get("part_tree") or {}).get("children") or []
    parts = ", ".join(n.get("name", "") for n in children)
    n_children = len(children)
    min_ops = max(20, n_children * 4)
    return (
        f"Design brief: {brief}\n\nStage 1 context - object: \"{merged.get('object','')}\", material: {mat}\n"
        f"Parts ({n_children} children): {parts}\n\n"
        f"MANDATORY: produce at least {min_ops} geometry_ops ({n_children} children x 4 ops minimum each). "
        f"Every child listed above MUST have 4+ ops targeting it by name. "
        f"Children with <4 ops = LOW-RES = REJECTED.\n\n"
        'Output JSON with "geometry_ops" (each {op,id,target,args:{at:[x,y,z], plus dims like '
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
    "CRITICAL - Per-child geometry rule: EVERY part_tree child MUST have AT LEAST 4 dedicated geometry_ops that "
    "reference it by id or target name. Parts with fewer than 4 ops are classified LOW-RES and the entire candidate "
    "is REJECTED. With 5-9 children this means 20-36+ total ops minimum. Do NOT concentrate ops on one child and "
    "leave others sparse. Distribute ops proportionally: primary body child gets 5-8 ops, each secondary child gets 4-6 ops.\n"
    "Op diversity per child: each child's ops must include at minimum: 1 body/shape op (box/cylinder/shell/extrude/revolve/loft), "
    "1 subtract/negative op (drill/pocket/channel/subtract), 1 interface/mounting op (boss/pattern_polar/pattern_linear), "
    "and 1 finish op (fillet/chamfer/engrave). A child with only 'nominal-part-body' is ALWAYS rejected.\n"
    "Coordinate distribution rule: geometry_ops args.at [x,y,z] must be physically distributed across the local subsystem "
    "volume. No two children's ops may share identical coordinates. Each child's ops must span at least 2 distinct "
    "coordinate regions within the subsystem envelope.\n"
    "Interface rule: include at least three adjacent-module interfaces or mounting datums and at least three "
    "negative/service features such as holes, pockets, ducts, channels, ports, or access cuts.\n"
    "Reciprocal interface rule: name exact neighboring subsystem labels when they mate, and choose "
    "connection_type + DOF + clearance_mm + required_feature so the neighbor can declare the same joint family back.\n"
    "Budget rule: cad_brief.mass_est_g must be a numeric grams value, and verify must include a mass/budget check.\n"
    "Joint evidence rule: critical joints need visible insert/washer/locking/preload evidence and torque_Nm or preload intent.\n"
    "Training-quality rule: make part_tree children and geometry_ops mutually traceable by id/name. "
    "Every child id that appears in part_tree must appear as a target in geometry_ops at least 4 times.\n"
    "Analysis-ready rule: verify must include a boundary_conditions object with "
    "fixture_points (list of {at:[x,y,z], type:fixed|pinned|roller}), "
    "thermal_zones (list of {at:[x,y,z], W_or_degC:number, role:source|sink}), "
    "and pressure_faces (list of {face:string, Pa:number}). "
    "These are coordinate-referenced so downstream CFD/FEA can set BCs directly.\n"
    "Assembly sequence rule: cad_brief must include assembly_sequence (ordered list of "
    "{step:int, action:install|fasten|align|press|route, target:string, tool:string, "
    "torque_Nm_or_force_N:number, datum:string}) and disassembly_sequence for field-serviceable parts.\n"
    "Tolerance stack-up rule: for each adjacent_interface in the subsystem plan, "
    "include stack_up_mm (cumulative tolerance from assembly datum to mating face) and fit_class (e.g. H7/h6, LC2).\n"
    "Dimensional realism rule: all dimensions must be physically plausible for the subsystem scale. "
    "A CubeSat part is 50-100mm, a robot arm link is 80-400mm, a tiltrotor blade is 200-1500mm. "
    "Wall thickness, hole diameters, fillet radii must match the stated material and process "
    "(FDM min wall 1.2mm, SLA 0.5mm, CNC 0.8mm). No zero-dimension or placeholder values."
)


def build_part_brief(vehicle, part, micro_clause, variant=""):
    desc = vehicle['desc']
    if variant:
        desc = f"{desc}\n{variant}"
    return (
        f"Subsystem module: {part['label']} (fixed BOM item inside {vehicle['label']})\n"
        f"Spec: {part['spec']}\n"
        f"Vehicle context: {desc}\n"
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
        if len(ch) < 5:
            iss.append(f"requires >=5 child features in part_tree (got {len(ch)}) - decompose subsystem fully")
    elif stage == "s2":
        ops = obj.get("geometry_ops") or []
        coord = sum(1 for o in ops if isinstance((o or {}).get("args", {}).get("at"), list))
        if len(ops) < 16:
            iss.append(f"requires >=16 geometry operations (got {len(ops)})")
        if coord < 10:
            iss.append(f"requires >=10 coordinate-bearing ops with args.at (got {coord})")
        if not isinstance(obj.get("cad_brief"), dict):
            iss.append("requires cad_brief")
        targets = {}
        for o in ops:
            t = (o or {}).get("target") or (o or {}).get("id") or ""
            if t:
                targets[t] = targets.get(t, 0) + 1
        sparse = [t for t, c in targets.items() if c < 2 and t not in ("asm-001",)]
        if len(sparse) > len(targets) // 2:
            iss.append(f"too many under-defined targets ({len(sparse)} with <2 ops) - distribute ops across all children")
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
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            print(f"    HTTP {e.code}: {body[:300]}", flush=True)
            note = f"\n\nERROR: {e}. Output corrected JSON only."
            continue
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
def synthesize_subsystem(vehicle, part, seed, log, variant=""):
    skeleton = load_pack(seed, "skeleton.json")
    matched = match_subsystem_for_part(skeleton, part) if skeleton else None
    micro_clause = ""
    if matched:
        mp = load_pack(seed, f"{matched['id']}.json")
        if mp:
            micro_clause = "\n" + micro_pack_clause(mp) + "\n"
            log(f"    micro-pack <- {matched['id']} ({matched.get('discipline')})")
    part_brief = build_part_brief(vehicle, part, micro_clause, variant=variant)

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


# ── 프롬프트 변형 (2차 배치용: seed당 다양한 설계 시나리오) ──────────────────
PROMPT_VARIANTS = {
    "cubesat": [
        "",
        "Mission variant: polar orbit Earth-observation, -40°C thermal design emphasis, radiation-hardened components",
        "Mission variant: LEO IoT communication demonstrator, antenna subsystem priority, low-power design",
        "Mission variant: technology education kit, design for disassembly and classroom demonstration",
        "Mission variant: deep-space CubeSat relay, high-gain antenna, extended thermal range +-120°C",
    ],
    "robot_arm": [
        "",
        "Application variant: food-grade hygienic design, IP67 sealed joints, NSF-compliant materials",
        "Application variant: collaborative robot mode, compliant joints, collision absorption, rounded edges",
        "Application variant: welding cell deployment, heat-shielded links, spark-resistant cable routing",
        "Application variant: cleanroom semiconductor handling, ESD-safe, particle-free joint seals",
    ],
    "tiltrotor": [
        "",
        "Mission variant: maritime surveillance, salt-fog resistant, flotation-equipped landing gear",
        "Mission variant: urban delivery, noise-constrained rotors, redundant tilt servos, obstacle avoidance pod",
        "Mission variant: high-altitude mapping (4000m+), thin-air optimized props, pressurized avionics bay",
    ],
    "small_launch_vehicle": [
        "",
        "Display variant: university teaching model, labeled cross-sections, transparent inspection windows",
        "Display variant: museum exhibit scale, reinforced for public handling, LED-lit internal features",
        "Display variant: engineering trade-study mock, swappable engine and tank dummy modules",
    ],
    "long_range_recon_wing": [
        "",
        "Mission variant: agricultural survey, multispectral sensor bay, low-altitude dust tolerance",
        "Mission variant: offshore wind farm inspection, salt-air resistant, high-wind launch capable",
        "Mission variant: wildfire monitoring, heat-resistant belly, real-time video relay, FLIR bay",
    ],
    "haptic_glove": [
        "",
        "Application variant: surgical training simulator, high-precision fingertip force, sterilizable shell",
        "Application variant: industrial teleop for hazmat, ruggedized exo-links, chemical-resistant TPU",
        "Application variant: VR gaming consumer product, lightweight (< 400g), quick-swap finger cartridges",
    ],
}


SEED_FOS_THRESHOLDS = {
    "cubesat":              {"reject_below": 1.5,  "keep_min": 3.0,  "good": 10.0, "excellent": 25.0},
    "robot_arm":            {"reject_below": 0.05, "keep_min": 0.15, "good": 0.5,  "excellent": 3.0},
    "tiltrotor":            {"reject_below": 0.1,  "keep_min": 0.6,  "good": 3.0,  "excellent": 10.0},
    "small_launch_vehicle": {"reject_below": 0.05, "keep_min": 0.5,  "good": 2.5,  "excellent": 10.0},
    "long_range_recon_wing":{"reject_below": 0.2,  "keep_min": 0.5,  "good": 1.0,  "excellent": 1.8},
    "haptic_glove":         {"reject_below": 0.05, "keep_min": 0.8,  "good": 5.0,  "excellent": 20.0},
}
SEED_FOS_DEFAULT = {"reject_below": 0.1, "keep_min": 1.5, "good": 5.0, "excellent": 15.0}


def fos_grade(fos, thresholds):
    if fos >= thresholds["excellent"]:
        return "A"
    if fos >= thresholds["good"]:
        return "B"
    if fos >= thresholds["keep_min"]:
        return "C"
    return None


def auto_decision(parts_total, parts_ok, interference, analysis, resolution,
                  seed_name=""):
    blocked = (interference.get("counts") or {}).get("blocked_pairs", 0)
    low_res = resolution.get("low_res_parts") or []
    sizing = analysis.get("sizing") or {}
    fos = sizing.get("solver_fos", sizing.get("worst_fos"))
    status = analysis.get("status")
    th = SEED_FOS_THRESHOLDS.get(seed_name, SEED_FOS_DEFAULT)
    reasons = []
    if parts_ok < parts_total:
        reasons.append(f"incomplete: {parts_ok}/{parts_total} parts got a blueprint")
    if low_res:
        reasons.append(f"LOW-RES parts {low_res} (model gave too few ops)")
    if reasons:
        return "reject", "; ".join(reasons), None
    if not isinstance(fos, (int, float)):
        return "hold", f"mid: blocked {blocked}, FoS {fos}, status {status}", None
    if fos < th["reject_below"]:
        return "reject", f"FoS {fos} below structural minimum {th['reject_below']} for {seed_name}", None
    grade = fos_grade(fos, th)
    if status == "ok" and grade:
        note = f"FoS {fos} [grade {grade}], analysis ok"
        if blocked and blocked > 0:
            note += f" · blocked {blocked} (our placement, not design - review layout)"
        return "keep", note, grade
    return "hold", f"mid: blocked {blocked}, FoS {fos}, status {status}", None


# ── 한 후보(어셈블리) 생성 + audit + 게이트 + persist ────────────────────────
def run_candidate(seed, vehicle, gen_seed, log, variant_idx=0):
    variants = PROMPT_VARIANTS.get(seed, [""])
    variant = variants[variant_idx % len(variants)] if variants else ""
    run_meta = {"seed": gen_seed, "model": LM_MODEL or "lmstudio", "generator": "generate_batch.py",
                "started": now_iso(), "variant_idx": variant_idx % len(variants)}
    if variant:
        log(f"  variant[{variant_idx % len(variants)}]: {variant[:80]}")
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
            bp, _plan, n_ops = synthesize_subsystem(vehicle, part, seed, log, variant=variant)
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
    skip_audit = os.environ.get("BP_SKIP_AUDIT", "").lower() in ("1", "true", "yes")
    if skip_audit:
        log(f"  (CAD audit skipped — BP_SKIP_AUDIT=1)")
        interference, analysis, resolution = {}, {}, {}
    else:
        try:
            subprocess.run([sys.executable, "run_full_pipeline.py", seed, "--dir", run_dir],
                           cwd=str(CAD_DIR), timeout=1200, capture_output=True, text=True)
        except Exception as e:
            log(f"  audit pipeline error: {e}")
        interference, analysis, resolution = read_reports(seed)

    decision, why, grade = auto_decision(len(vehicle["parts"]), parts_ok, interference, analysis, resolution,
                                         seed_name=seed)
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
                                  "grade": grade,
                                  "auto_reason": why},
        "messages": [
            {"role": "system", "content": "You are Blueprint XPU. Given a vehicle assembly brief, output a "
             "schema_v6 multi-subsystem blueprint as raw JSON (part_tree + coordinate-bearing geometry_ops + "
             "cad_brief + verify + risk per subsystem). No prose."},
            {"role": "user", "content": f"Design brief: {vehicle['desc']}"
             f"{chr(10) + variant if variant else ''}\nSeed: {seed}\n"
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


CURATION_LOG = REPO / "30_model" / "curation" / "curation_log.jsonl"


def _run_gap_analysis():
    if not CURATION_LOG.exists():
        print("[gap] no curation_log.jsonl found"); return 1
    rows = []
    for line in CURATION_LOG.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try: rows.append(json.loads(line))
            except Exception: pass

    by_seed = {}
    for r in rows:
        s = r.get("seed", "unknown")
        if s not in by_seed:
            by_seed[s] = {"keep": 0, "reject": 0, "hold": 0, "A": 0, "B": 0, "C": 0}
        d = str(r.get("decision", "")).lower()
        if d in by_seed[s]:
            by_seed[s][d] += 1
        g = (r.get("engineering_scorecard") or {}).get("grade")
        if g in ("A", "B", "C"):
            by_seed[s][g] += 1

    total_keep = sum(v["keep"] for v in by_seed.values())
    total_reject = sum(v["reject"] for v in by_seed.values())
    trainable = total_keep + total_reject
    print(f"\n[gap] corpus: {len(rows)} total, {trainable} trainable (keep {total_keep} + reject {total_reject})")
    print(f"[gap] gate: {trainable}/300 trial")
    if trainable < 300:
        print(f"[gap] NEED {300 - trainable} more keep/reject rows\n")

    print(f"{'seed':<25} {'keep':>5} {'rej':>4} {'hold':>4} | {'A':>3} {'B':>3} {'C':>3} | A%")
    print("-" * 62)
    recs = []
    for s in SEED_LIST:
        v = by_seed.get(s, {"keep": 0, "reject": 0, "hold": 0, "A": 0, "B": 0, "C": 0})
        a_pct = (v["A"] / v["keep"] * 100) if v["keep"] else 0
        print(f"{s:<25} {v['keep']:>5} {v['reject']:>4} {v['hold']:>4} | {v['A']:>3} {v['B']:>3} {v['C']:>3} | {a_pct:>4.0f}%")
        if a_pct < 20:
            recs.append(f"  > {s}: grade-A only {a_pct:.0f}% - needs higher-quality variants")
        if v["keep"] < total_keep / len(SEED_LIST) * 0.8:
            recs.append(f"  > {s}: underrepresented ({v['keep']} keep vs avg {total_keep // len(SEED_LIST)})")

    n_variants = len(PROMPT_VARIANTS.get(SEED_LIST[0], [""]))
    print(f"\n[gap] prompt variants per seed: {n_variants} (use all for diversity)")
    if recs:
        print("\n[gap] recommendations:")
        for r in recs:
            print(r)
    else:
        print("\n[gap] seed balance looks good")
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="all", help="all | comma list (e.g. cubesat,robot_arm)")
    ap.add_argument("--n", type=int, default=0, help="total candidates across selected seeds (round-robin)")
    ap.add_argument("--per-seed", type=int, default=0, help="candidates per seed (overrides --n)")
    ap.add_argument("--resume", action="store_true", help="continue from batch_checkpoint.json")
    ap.add_argument("--inspect-vehicle", default="", help="print the BOM for a seed and exit")
    ap.add_argument("--gap-analysis", action="store_true", help="analyze corpus gaps and recommend targeted production")
    a = ap.parse_args(argv[1:])

    vehicles = json.loads(VEHICLES_FILE.read_text(encoding="utf-8"))
    if a.inspect_vehicle:
        v = vehicles.get(a.inspect_vehicle)
        print(json.dumps(v, ensure_ascii=False, indent=2) if v else f"no vehicle for seed {a.inspect_vehicle}")
        return 0
    if a.gap_analysis:
        return _run_gap_analysis()

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
    variant_counters = {s: 0 for s in seeds}
    for idx in range(start, len(queue)):
        seed = queue[idx]
        gen_seed = random.randint(1, 2_000_000)
        vi = variant_counters.get(seed, 0)
        variant_counters[seed] = vi + 1
        print(f"\n[{idx+1}/{len(queue)}] seed={seed} gen_seed={gen_seed} variant={vi % len(PROMPT_VARIANTS.get(seed, ['']))}")
        try:
            decision = run_candidate(seed, vehicles[seed], gen_seed, lambda m: print(m, flush=True),
                                     variant_idx=vi)
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
