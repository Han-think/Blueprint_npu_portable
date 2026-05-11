"""
Blueprint NPU · Local HTTP Server
----------------------------------
브라우저에서 file:// 대신 http://127.0.0.1:8080 으로 접근하면
Ollama fetch CORS 문제가 해결됩니다.

사용법:
    python server/serve.py          # 기본 포트 8080
    python server/serve.py 9090     # 포트 지정

실행 후 브라우저에서: http://127.0.0.1:8080
"""

import http.server
import socketserver
import sys
import os
import webbrowser
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080

# 프로젝트 루트 (server/ 의 상위 디렉토리)
ROOT = Path(__file__).resolve().parent.parent


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        # Ollama CORS: 브라우저가 로컬 fetch를 허용하도록
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        # JS 모듈 MIME 타입
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, fmt, *args):
        # 조용한 로깅 (JS/CSS asset 요청 숨김)
        path = args[0].split()[1] if args else ''
        if any(path.endswith(ext) for ext in ('.js', '.css', '.svg', '.png', '.ico')):
            return
        print(f"  {self.address_string()} → {fmt % args}")


def main():
    os.chdir(ROOT)
    url = f"http://127.0.0.1:{PORT}"
    print(f"\n  Blueprint NPU · Local Server")
    print(f"  Serving: {ROOT}")
    print(f"  URL:     {url}")
    print(f"  Ollama:  http://127.0.0.1:11434")
    print(f"\n  Ctrl+C to stop\n")

    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        httpd.allow_reuse_address = True
        try:
            webbrowser.open(url)
        except Exception:
            pass
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  Server stopped.")


if __name__ == "__main__":
    main()
