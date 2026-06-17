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
"""

import http.server
import socketserver
import sys
import os
import json
import webbrowser
from pathlib import Path

PORT       = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 8080
NO_BROWSER = '--no-browser' in sys.argv
ROOT = Path(__file__).resolve().parent.parent

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

SCHEMA = None
def get_schema():
    global SCHEMA
    if SCHEMA is None:
        SCHEMA = json.loads((ROOT / 'schema_v6.json').read_text(encoding='utf-8'))
    return SCHEMA


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
        if self.path == '/validate':
            self._handle_validate()
        else:
            self.send_response(404)
            self.end_headers()

    # ── GET 추가 라우트 ────────────────────────────────────────
    def do_GET(self):
        if self.path == '/schema':
            self._handle_schema()
        else:
            super().do_GET()

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

    # ── /schema ────────────────────────────────────────────────
    def _handle_schema(self):
        data = json.dumps(get_schema(), ensure_ascii=False).encode('utf-8')
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
    print(f"  Ollama  : http://127.0.0.1:11434")
    print(f"  API     : POST {url}/validate  |  GET {url}/schema")
    print(f"\n  Ctrl+C to stop\n")

    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        httpd.allow_reuse_address = True
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
