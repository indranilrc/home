"""Build the site and serve it locally, mounted at the configured base_path.

Usage: python tools/preview.py [--port 8000] [--drafts]
"""
from __future__ import annotations

import argparse
import functools
import http.server
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402

from build import build_site  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--drafts", action="store_true")
    a = ap.parse_args()
    out = ROOT / "_site"
    build_site(out, include_drafts=a.drafts)
    base = (yaml.safe_load((ROOT / "content" / "site.yml").read_text()).get("base_path") or "").rstrip("/")

    class Handler(http.server.SimpleHTTPRequestHandler):
        def translate_path(self, path):
            if base and (path == base or path.startswith(base + "/")):
                path = path[len(base):] or "/"
            return super().translate_path(path)

        def send_error(self, code, message=None, explain=None):
            page = out / "404.html"
            if code == 404 and page.exists():
                body = page.read_bytes()
                self.send_response(404)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            super().send_error(code, message, explain)

    handler = functools.partial(Handler, directory=str(out))
    print(f"Preview: http://localhost:{a.port}{base}/   (Ctrl+C to stop)")
    http.server.ThreadingHTTPServer(("127.0.0.1", a.port), handler).serve_forever()


if __name__ == "__main__":
    main()
