"""Minimal HTTP health endpoints for Railway/Docker worker probes."""

from __future__ import annotations

import json
import os
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any


def _celery_ready() -> tuple[bool, dict[str, Any]]:
    try:
        result = subprocess.run(
            ["celery", "-A", "jober_worker.celery_app", "inspect", "ping"],
            capture_output=True,
            timeout=10,
            check=False,
        )
        ok = b"pong" in result.stdout
        return ok, {"celery": {"ok": ok, "detail": "ok" if ok else "no pong"}}
    except Exception as exc:  # noqa: BLE001
        return False, {"celery": {"ok": False, "detail": str(exc)}}


class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path == "/healthz":
            body = json.dumps({"status": "ok"}).encode()
            status = 200
        elif path == "/readyz":
            ok, checks = _celery_ready()
            body = json.dumps(
                {"status": "ready" if ok else "not_ready", "checks": checks},
            ).encode()
            status = 200 if ok else 503
        else:
            body = b""
            status = 404
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


def serve() -> None:
    port = int(os.environ.get("PORT", "8080"))
    server = HTTPServer(("0.0.0.0", port), _HealthHandler)
    server.serve_forever()


def start_background() -> threading.Thread:
    thread = threading.Thread(target=serve, daemon=True, name="worker-health")
    thread.start()
    return thread


if __name__ == "__main__":
    serve()
