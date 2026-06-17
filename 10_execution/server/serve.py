"""
Blueprint NPU · Local HTTP Server + Validation API
----------------------------------------------------
사용법:
    python server/serve.py          # 기본 포트 8080
    python server/serve.py 9090     # 포트 지정

엔드포인트:
    GET  /         → 정적 파일 서빙 (index.html 등)
    POST /validate → schema_v6.json 기반 JSON 검증
    GET  /schema   → schema_v6.json 내용 반환
    GET  /context-pack → 로컬 공학 에이전트용 compact context pack
"""

import http.server
import socketserver
import sys
import os
import json
import webbrowser
import urllib.error
import urllib.request
from pathlib import Path

PORT       = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 8080
NO_BROWSER = '--no-browser' in sys.argv
# 트리: REPO/10_execution/server/serve.py → REPO = parents[2]
REPO        = Path(__file__).resolve().parents[2]
WEB_ROOT    = REPO / '10_execution' / 'ui'          # 정적 서빙 루트 (HTML+vendor+assets)
SCHEMA_FILE = REPO / '00_contract' / 'schema_v6.json'
ROOT        = WEB_ROOT  # 정적 핸들러/디렉토리 호환용 별칭
WORKSPACE_CONTRACT_VERSION = 'blueprint_folder_bound_engineering_agent_v1'
CONTEXT_PACK_VERSION = 'blueprint_engineering_context_pack_v1'

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

SCHEMA = None
def get_schema():
    global SCHEMA
    if SCHEMA is None:
        SCHEMA = json.loads(SCHEMA_FILE.read_text(encoding='utf-8'))
    return SCHEMA


# ── 생성 번들 → CAD 파이프라인 입력 (seeds_generated/<seed>/<run_id>/) ──────
VEHICLE_TO_SEED = {
    'wing_long_range': 'long_range_recon_wing',
    'tiltrotor_vtol': 'tiltrotor',
    'cubesat_3u': 'cubesat',
    'small_launch_vehicle': 'small_launch_vehicle',
    'arm_6dof': 'robot_arm',
    'haptic_glove_pair': 'haptic_glove',
}

INTERFACE_MATE = {
    'mount': 'face', 'seal': 'face', 'electrical': 'connector',
    'slide': 'slide', 'pin': 'pin', 'snap': 'snap', 'hinge': 'pin',
}


def export_bundle_to_seed_dir(bundle):
    import time as _time

    vehicle = bundle.get('vehicle') or {}
    vid = str(vehicle.get('id') or 'unknown')
    seed = VEHICLE_TO_SEED.get(vid, vid)
    parts = [p for p in bundle.get('parts', []) if p.get('blueprint')]
    if not parts:
        raise ValueError('bundle has no generated parts (blueprint missing)')

    run_id = _time.strftime('%Y%m%d_%H%M%S')
    out_dir = REPO / '20_dataset' / 'seeds_generated' / seed / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    # ── 다중 루트 합성 blueprint: N개 생성 파트를 part_tree 루트로, op는 해당 루트로 타깃팅
    # → build_part_states 가 N개 루트 솔리드를 만들어 어셈블리 전체를 CAD/audit 한다.
    children, geometry_ops = [], []
    for i, p in enumerate(parts):
        pid = p.get('id') or f'new-{i + 1:03d}'
        bp = p.get('blueprint') or {}
        children.append({'id': pid, 'name': p.get('label', pid), 'qty': 1,
                         'material': bp.get('cad_brief', {}).get('material', 'PETG'),
                         'process': bp.get('cad_brief', {}).get('process', 'FDM'), 'children': []})
        for op in (bp.get('geometry_ops') or []):
            op2 = dict(op)
            op2['target'] = pid   # 이 op을 해당 루트에 귀속
            geometry_ops.append(op2)

    # envelope: vehicle.envelope 문자열에서 숫자 추출, 실패 시 기본값
    import re as _re
    nums = _re.findall(r'\d+(?:\.\d+)?', str(vehicle.get('envelope', '')))
    envelope = [float(n) for n in nums[:3]] if len(nums) >= 3 else [400.0, 400.0, 400.0]
    best = max(parts, key=lambda p: len((p['blueprint'].get('part_tree') or {}).get('children', []) or []))
    bb = best['blueprint'].get('brief', {})
    composite_bp = {
        'version': 'bp-npu-r6',
        'ts': _time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'project': seed,
        'object': vehicle.get('label', seed),
        'brief': bb if bb else {'requirements': [], 'constraints': {
            'material': vehicle.get('material', 'PETG'), 'process': vehicle.get('process', 'FDM'),
            'envelope_mm': envelope, 'min_wall_mm': 1.5, 'overhang_deg': 45, 'tol_mm': 0.2}},
        'cad_brief': {'name': vehicle.get('label', seed), 'rev': '1.0',
                      'material': vehicle.get('material', 'PETG'), 'envelope_mm': envelope,
                      'build_direction': 'Z'},
        'part_tree': {'id': 'asm', 'name': vehicle.get('label', seed), 'qty': 1, 'children': children},
        'geometry_ops': geometry_ops,
    }
    package = {
        'schema': 'blueprint_generated_package_v1',
        'seed': seed,
        'run_id': run_id,
        'vehicle': vehicle,
        'run_meta': bundle.get('run_meta', {}),
        'schema_v6_blueprint': composite_bp,
        'generated_parts': [
            {'id': p.get('id'), 'label': p.get('label'), 'spec': p.get('spec'), 'blueprint': p.get('blueprint')}
            for p in parts
        ],
    }
    (out_dir / 'package.json').write_text(json.dumps(package, ensure_ascii=False, indent=1), encoding='utf-8')

    # adjacent_interfaces → joints/fasteners 자동 유도
    labels = {str(p.get('label', '')).lower(): p.get('id') for p in parts}

    def resolve_part(name):
        name = str(name or '').lower()
        for label, pid in labels.items():
            if name and (name in label or label in name):
                return pid
        return None

    joints, fasteners, seen = [], [], set()
    for p in parts:
        plan = p.get('subsystem_plan') or p['blueprint'].get('_subsystem_plan') or {}
        for iface in plan.get('adjacent_interfaces', []) or []:
            target = resolve_part(iface.get('target_part'))
            if not target or target == p.get('id'):
                continue
            pair = tuple(sorted([p.get('id'), target]))
            itype = str(iface.get('interface_type', 'mount')).lower()
            if pair + (itype,) in seen:
                continue
            seen.add(pair + (itype,))
            feature = str(iface.get('required_feature', ''))
            if any(k in feature.lower() for k in ('bolt', 'screw', 'fastener', 'm3', 'm4')):
                fasteners.append({
                    'id': f'F{len(fasteners) + 1}', 'standard': 'M3', 'kind': 'screw',
                    'qty': 4, 'anchor': 'corners_4', 'joins': [p.get('id'), target],
                    'hole': 'clearance', 'note': feature[:80],
                })
            joints.append({
                'id': f'J{len(joints) + 1}',
                'partA': p.get('id'), 'partB': target,
                'mate': INTERFACE_MATE.get(itype, 'face'),
                'clearance_mm': 0.25,
                'note': f"{itype}: {feature}"[:100],
            })
    assembly = {
        'version': 'bp-assembly-v1-generated',
        'target': vid,
        'joints': joints,
        'fasteners': fasteners,
        'hardware_bom': [{'standard': 'M3', 'qty': sum(f['qty'] for f in fasteners)}] if fasteners else [],
    }
    (out_dir / 'assembly.json').write_text(json.dumps(assembly, ensure_ascii=False, indent=1), encoding='utf-8')

    return {
        'ok': True,
        'seed': seed,
        'dir': str(out_dir.relative_to(REPO)),
        'parts': len(parts),
        'joints': len(joints),
        'fasteners': len(fasteners),
        'next': f'python 10_execution/cad/build_solid.py {seed} --dir "{out_dir.relative_to(REPO)}"',
    }


def audit_bundle_pipeline(bundle):
    """생성 번들 → 합성 패키지 → CAD 파이프라인(subprocess) → 간섭 audit 리포트.
    build123d 무거운 import ×4 라 ~30~90s. 수동 audit 버튼용."""
    import subprocess as _sp

    exported = export_bundle_to_seed_dir(bundle)
    seed = exported['seed']
    run_dir = exported['dir']                 # REPO 상대
    gen = f'{seed}_generated'                 # CAD 출력 폴더명 (validate/audit 의 seed 인자)
    cad = REPO / '10_execution' / 'cad'
    py = sys.executable

    # 단일 오케스트레이터 1회 호출 (build123d import 1번 — 5-subprocess 대비 대폭 단축)
    logs = []
    try:
        r = _sp.run([py, '-X', 'utf8', 'run_full_pipeline.py', seed, '--dir', run_dir],
                    cwd=str(cad), capture_output=True, text=True, timeout=400)
    except _sp.TimeoutExpired:
        return {'ok': False, 'stage': 'run_full_pipeline', 'error': 'timeout (400s)', 'dir': run_dir, 'logs': logs}
    tail = (r.stdout or '')[-800:] + (('\n' + r.stderr[-600:]) if r.returncode != 0 and r.stderr else '')
    logs.append({'step': 'run_full_pipeline', 'rc': r.returncode, 'tail': tail.strip()})

    report_path = REPO / '10_execution' / 'cad' / 'output' / gen / 'assembly_interference_report.json'
    readiness_path = REPO / '10_execution' / 'cad' / 'output' / gen / 'print' / 'print_readiness.json'
    if not report_path.exists():
        return {'ok': False, 'error': 'interference report not produced', 'dir': run_dir, 'logs': logs}
    report = json.loads(report_path.read_text(encoding='utf-8'))
    readiness = json.loads(readiness_path.read_text(encoding='utf-8')) if readiness_path.exists() else {}
    analysis_path = REPO / '10_execution' / 'cad' / 'output' / gen / 'analysis_report.json'
    analysis = json.loads(analysis_path.read_text(encoding='utf-8')) if analysis_path.exists() else None
    return {
        'ok': True,
        'seed': seed,
        'generated_seed': gen,
        'dir': run_dir,
        'report': report,
        'analysis': analysis,
        'print_verdict': readiness.get('verdict'),
        'report_url': f'/output/{gen}/assembly_interference_report.json',
        'logs': logs,
    }


# ── 큐레이션 학습 코퍼스 디스크 영구화 (localStorage 100-cap 무관, 세대 누적) ──────
CURATION_DIR = REPO / '30_model' / 'curation'
CURATION_LOG = CURATION_DIR / 'curation_log.jsonl'
CURATION_INDEX = CURATION_DIR / 'curation_index.json'
_CURATION_IDS = None  # 중복 스킵용 id 캐시


def _load_curation_ids():
    global _CURATION_IDS
    if _CURATION_IDS is not None:
        return _CURATION_IDS
    ids = set()
    if CURATION_LOG.exists():
        for line in CURATION_LOG.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                ids.add(json.loads(line).get('id'))
            except Exception:
                pass
    _CURATION_IDS = ids
    return ids


def _curation_index():
    if CURATION_INDEX.exists():
        try:
            return json.loads(CURATION_INDEX.read_text(encoding='utf-8'))
        except Exception:
            pass
    return {'schema': 'blueprint_curation_index_v1', 'total': 0, 'kept': 0, 'rejected': 0,
            'by_seed': {}, 'last_ts': None}


def persist_curation_row(row):
    CURATION_DIR.mkdir(parents=True, exist_ok=True)
    rid = row.get('id')
    if not rid:
        raise ValueError('curation row has no id')
    ids = _load_curation_ids()
    idx = _curation_index()
    if rid in ids:
        return {'ok': True, 'persisted': False, 'reason': 'duplicate id',
                'total': idx['total'], 'kept': idx['kept'], 'rejected': idx['rejected']}
    with CURATION_LOG.open('a', encoding='utf-8') as f:
        f.write(json.dumps(row, ensure_ascii=False) + '\n')
    ids.add(rid)
    decision = str(row.get('decision', '')).lower()
    seed = row.get('seed') or (row.get('input_context') or {}).get('seed') or row.get('vehicle_id') or 'unknown'
    idx['total'] += 1
    if decision == 'keep':
        idx['kept'] += 1
    elif decision == 'reject':
        idx['rejected'] += 1
    idx['by_seed'][seed] = idx['by_seed'].get(seed, 0) + 1
    idx['last_ts'] = row.get('ts')
    CURATION_INDEX.write_text(json.dumps(idx, ensure_ascii=False, indent=1), encoding='utf-8')
    return {'ok': True, 'persisted': True, 'total': idx['total'], 'kept': idx['kept'], 'rejected': idx['rejected']}


def curation_stats():
    idx = _curation_index()
    # 세대 깊이: loop_parent_id 체인 최대 길이
    parent = {}
    if CURATION_LOG.exists():
        for line in CURATION_LOG.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
                parent[r.get('id')] = (r.get('loop_parent_id') or (r.get('input_context') or {}).get('loop_parent_id'))
            except Exception:
                pass

    def depth(node, guard=0):
        p = parent.get(node)
        if not p or p not in parent or guard > 64:
            return 1
        return 1 + depth(p, guard + 1)

    generations = max((depth(n) for n in parent), default=0)
    return {'ok': True, 'total': idx['total'], 'kept': idx['kept'], 'rejected': idx['rejected'],
            'by_seed': idx['by_seed'], 'generations': generations, 'last_ts': idx['last_ts']}


def _row_score(row):
    sc = row.get('engineering_scorecard') or {}
    for k in ('score', 'overall', 'total'):
        if isinstance(sc.get(k), (int, float)):
            return round(float(sc[k]), 1)
    if isinstance(row.get('rating'), (int, float)):
        return round(float(row['rating']) * 20, 1)
    return None


def curation_records():
    """계보 view 용 compact 레코드 목록 (parent→child 트리 + 세대별 점수 추세)."""
    out = []
    if CURATION_LOG.exists():
        for line in CURATION_LOG.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            out.append({
                'id': r.get('id'),
                'ts': r.get('ts'),
                'seed': r.get('seed') or (r.get('input_context') or {}).get('seed') or r.get('vehicle_id') or 'unknown',
                'decision': str(r.get('decision', '')).lower(),
                'title': r.get('title') or r.get('vehicle_id') or r.get('id'),
                'parent_id': r.get('loop_parent_id') or (r.get('input_context') or {}).get('loop_parent_id'),
                'score': _row_score(r),
                'score_delta': r.get('score_delta'),
            })
    return {'ok': True, 'records': out, 'count': len(out)}


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    # ── CORS 헤더 ──────────────────────────────────────────────
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    # ── POST 라우터 ────────────────────────────────────────────
    def do_POST(self):
        if self.path == '/lmstudio/v1/chat/completions':
            self._proxy_lmstudio('POST', '/chat/completions')
        elif self.path == '/validate':
            self._handle_validate()
        elif self.path == '/export-bundle':
            self._handle_export_bundle()
        elif self.path == '/audit-bundle':
            self._handle_audit_bundle()
        elif self.path == '/persist-curation':
            self._handle_persist_curation()
        else:
            self.send_response(404)
            self.end_headers()

    # ── GET 추가 라우트 ────────────────────────────────────────
    def do_GET(self):
        if self.path == '/lmstudio/v1/models':
            self._proxy_lmstudio('GET', '/models')
        elif self.path == '/schema':
            self._handle_schema()
        elif self.path == '/context-pack':
            self._handle_context_pack()
        elif self.path.startswith('/output/'):
            self._serve_file(self.path[len('/output/'):], REPO / '10_execution' / 'cad' / 'output')
        elif self.path.startswith('/seeds/'):
            self._serve_file(self.path[len('/seeds/'):], REPO / '20_dataset' / 'seeds')
        elif self.path.startswith('/packs/'):
            self._serve_file(self.path[len('/packs/'):], REPO / '20_dataset' / 'packs')
        elif self.path == '/curation-stats':
            self._handle_curation_stats()
        elif self.path == '/curation-records':
            self._handle_json(curation_records)
        elif self.path == '/lineage' or self.path == '/lineage.html':
            self._serve_file('lineage.html', REPO / '10_execution' / 'ui')
        else:
            super().do_GET()

    def _serve_file(self, rel_raw, base_dir):
        rel = rel_raw.split('?')[0].lstrip('/')
        base = base_dir.resolve()
        target = (base / rel).resolve()
        if not str(target).startswith(str(base)) or not target.is_file():
            self.send_response(404); self.end_headers(); return
        ctype = ('model/stl' if target.suffix == '.stl'
                 else 'image/svg+xml' if target.suffix == '.svg'
                 else 'application/json; charset=utf-8' if target.suffix in ('.json', '.jsonl')
                 else 'application/octet-stream')
        data = target.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _proxy_lmstudio(self, method, upstream_path):
        try:
            body = None
            if method == 'POST':
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length)
            req = urllib.request.Request(
                f'http://127.0.0.1:1234/v1{upstream_path}',
                data=body,
                method=method,
                headers={'Content-Type': 'application/json'}
            )
            # 로컬 20B 추론은 긴 프롬프트에서 2분을 훌쩍 넘긴다 — 끊는 판단은 UI 재시도 로직에 맡긴다
            with urllib.request.urlopen(req, timeout=600) as resp:
                data = resp.read()
                ctype = resp.headers.get('Content-Type', 'application/json; charset=utf-8')
                self.send_response(resp.status)
                self.send_header('Content-Type', ctype)
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as e:
            data = e.read() or json.dumps({'error': f'LM Studio HTTP {e.code}'}).encode('utf-8')
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            data = json.dumps({'error': f'LM Studio proxy error: {e}'}, ensure_ascii=False).encode('utf-8')
            self.send_response(502)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    # ── /validate ──────────────────────────────────────────────
    def _handle_validate(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body   = json.loads(self.rfile.read(length))
            schema = get_schema()

            if not HAS_JSONSCHEMA:
                resp = {
                    'valid': None,
                    'errors': [],
                    'warning': 'jsonschema 미설치 — pip install jsonschema 후 재시작'
                }
            else:
                validator = jsonschema.Draft202012Validator(
                    schema,
                    format_checker=jsonschema.FormatChecker()
                )
                errors = []
                for e in validator.iter_errors(body):
                    errors.append({
                        'path':    list(e.absolute_path),
                        'message': e.message,
                        'field':   '.'.join(str(p) for p in e.absolute_path) or '(root)'
                    })
                resp = {'valid': len(errors) == 0, 'errors': errors}

        except json.JSONDecodeError as e:
            resp = {'valid': False, 'errors': [{'path': [], 'field': '(root)', 'message': f'JSON 파싱 오류: {e}'}]}
        except Exception as e:
            resp = {'valid': False, 'errors': [{'path': [], 'field': '(root)', 'message': str(e)}]}

        data = json.dumps(resp, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    # ── /export-bundle: 생성된 어셈블리 번들 → CAD 파이프라인 입력으로 저장 ──
    def _handle_export_bundle(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            bundle = json.loads(self.rfile.read(length))
            resp = export_bundle_to_seed_dir(bundle)
            status = 200
        except json.JSONDecodeError as e:
            resp, status = {'ok': False, 'error': f'JSON 파싱 오류: {e}'}, 400
        except Exception as e:
            resp, status = {'ok': False, 'error': str(e)}, 500
        data = json.dumps(resp, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    # ── /persist-curation: keep/reject 판정을 디스크 코퍼스에 누적 ──
    def _handle_persist_curation(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            row = json.loads(self.rfile.read(length))
            resp = persist_curation_row(row)
            status = 200
        except json.JSONDecodeError as e:
            resp, status = {'ok': False, 'error': f'JSON 파싱 오류: {e}'}, 400
        except Exception as e:
            resp, status = {'ok': False, 'error': str(e)}, 500
        data = json.dumps(resp, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _handle_curation_stats(self):
        self._handle_json(curation_stats)

    def _handle_json(self, fn):
        try:
            resp = fn()
        except Exception as e:
            resp = {'ok': False, 'error': str(e)}
        data = json.dumps(resp, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    # ── /audit-bundle: 생성 번들 → CAD 파이프라인 → 간섭 audit 리포트 반환 ──
    def _handle_audit_bundle(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            bundle = json.loads(self.rfile.read(length))
            resp = audit_bundle_pipeline(bundle)
            status = 200 if resp.get('ok') else 500
        except json.JSONDecodeError as e:
            resp, status = {'ok': False, 'error': f'JSON 파싱 오류: {e}'}, 400
        except Exception as e:
            resp, status = {'ok': False, 'error': str(e)}, 500
        data = json.dumps(resp, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    # ── /schema ────────────────────────────────────────────────
    def _handle_schema(self):
        data = json.dumps(get_schema(), ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _handle_context_pack(self):
        pack = {
            'schema': CONTEXT_PACK_VERSION,
            'workspace_contract_version': WORKSPACE_CONTRACT_VERSION,
            'workspace_root': str(REPO),
            'source_of_truth': '00_contract/schema_v6.json',
            'model_provider_priority': ['lmstudio:gpt-oss-20b', 'ollama:qwen3:8b', 'ollama:qwen2.5:7b', 'ollama:qwen3:4b'],
            'reasoning_chain': [
                'function', 'physics_path', 'subsystem_role', 'interfaces',
                'internal_features', 'geometry_ops', 'manufacturing_strategy',
                'verification', 'loop_feedback'
            ],
            'p0_gate': {
                'required': [
                    'subsystem_role', 'physics_paths', 'adjacent_interfaces',
                    'internal_features', 'internal_feature_targets',
                    'manufacturing_strategy', 'verification_focus'
                ],
                'minimums': {
                    'adjacent_interfaces': 3,
                    'internal_feature_targets': 5
                }
            },
            'mrl05_categories': [
                'wall/process readiness', 'overhang/support readiness',
                'fastener/joint sanity', 'serviceability',
                'inspection readiness', 'mass/process traceability',
                'risk coverage'
            ],
            'geometry_quality': [
                '12-24 coordinate-bearing geometry_ops for assembly subsystem work',
                'distributed args.at coordinates',
                'trace part_tree children to geometry_ops ids/targets',
                'include interface, service, negative, and datum features'
            ],
            'grounding_discipline': [
                'Do not invent named mechanisms, exotic acronyms, miracle materials, hidden capabilities, or fictional manufacturing processes.',
                'Prefer conservative mock-assembly features: ribs, bosses, standoffs, access panels, datum pads, brackets, rails, harness channels, inspection windows, fastener holes, labeled interface zones.'
            ],
            'curation_policy': {
                'primary_training_candidate': 'kept assembly bundles',
                'auxiliary_reference': 'single-part outputs',
                'records': ['keep', 'reject', 'hold', 'loop_feedback', 'engineering_scorecard']
            },
            'safety_boundary': 'Educational mock assembly and design-review evidence only; not manufacturing, flight, medical, propulsion, or certification approval.'
        }
        data = json.dumps(pack, ensure_ascii=False, indent=2).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    # ── 로깅 (asset 요청 숨김) ─────────────────────────────────
    def log_message(self, fmt, *args):
        # args[0]가 문자열("GET /path HTTP/1.1")일 때만 경로 추출
        try:
            first = str(args[0]) if args else ''
            parts = first.split()
            path  = parts[1] if len(parts) >= 2 else first
        except Exception:
            path = ''
        # 정적 에셋 + favicon 요청은 로그 숨김
        skip_exts = ('.js', '.css', '.svg', '.png', '.ico', '.woff', '.woff2', '.ttf')
        if path.endswith(skip_exts):
            return
        print(f"  {self.address_string()} → {fmt % args}")


def main():
    os.chdir(ROOT)
    url = f"http://127.0.0.1:{PORT}"

    if HAS_JSONSCHEMA:
        print(f"\n  [OK]  jsonschema available -- /validate active")
    else:
        print(f"\n  [WARN] jsonschema not installed — run: pip install jsonschema")

    print(f"  Blueprint NPU · Local Server")
    print(f"  Serving : {ROOT}")
    print(f"  URL     : {url}")
    print(f"  LMStudio: http://127.0.0.1:1234/v1")
    print(f"  Ollama  : http://127.0.0.1:11434")
    print(f"  API     : POST {url}/validate  |  GET {url}/schema  |  GET {url}/context-pack")
    print(f"\n  Ctrl+C to stop\n")

    class ThreadingServer(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True

    with ThreadingServer(("127.0.0.1", PORT), Handler) as httpd:
        if not NO_BROWSER:
            try:
                webbrowser.open(url + '/Minimal.html')
            except Exception:
                pass
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  Server stopped.")


if __name__ == "__main__":
    main()
