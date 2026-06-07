from __future__ import annotations

import argparse
import threading
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from jober_fixtures.outcomes import FIXTURE_OUTCOMES

PAGES_ROOT = Path(__file__).resolve().parent / "pages"

# slug -> relative path under pages/
ROUTE_MAP: dict[str, tuple[str, ...]] = {
    "behaviors/single-step": ("behaviors", "single_step.html"),
    "behaviors/multi-step": ("behaviors", "multi_step.html"),
    "behaviors/combobox": ("behaviors", "combobox.html"),
    "behaviors/dropzone": ("behaviors", "dropzone.html"),
    "behaviors/required-validation": ("behaviors", "required_validation.html"),
    "behaviors/conditional-fields": ("behaviors", "conditional_fields.html"),
    "behaviors/shifting-selector": ("behaviors", "shifting_selector.html"),
    "behaviors/already-applied": ("behaviors", "already_applied.html"),
    "behaviors/submit-success": ("behaviors", "submit_success.html"),
    "behaviors/uncertain-confirmation": ("behaviors", "uncertain_confirmation.html"),
    "gates/login": ("gates", "login_gate.html"),
    "gates/captcha": ("gates", "captcha_gate.html"),
    "security/injection": ("security", "injection.html"),
    "jobs/greenhouse": ("jobs", "greenhouse.html"),
    "jobs/lever": ("jobs", "lever.html"),
    "jobs/ashby": ("jobs", "ashby.html"),
    "jobs/workday": ("jobs", "workday.html"),
    "platforms/greenhouse": ("platforms", "greenhouse_apply.html"),
    "platforms/lever": ("platforms", "lever_apply.html"),
    "platforms/ashby": ("platforms", "ashby_apply.html"),
    "platforms/workday": ("platforms", "workday_apply.html"),
}


def create_app() -> FastAPI:
    app = FastAPI(title="Jober ATS Fixtures", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/catalog")
    def catalog() -> dict[str, Any]:
        return {
            "routes": sorted(ROUTE_MAP.keys()),
            "outcomes": {k: v.__dict__ for k, v in FIXTURE_OUTCOMES.items()},
        }

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        links = "\n".join(f'<li><a href="/{slug}">{slug}</a></li>' for slug in sorted(ROUTE_MAP))
        return f"<html><body><h1>ATS Fixtures</h1><ul>{links}</ul></body></html>"

    for slug, parts in ROUTE_MAP.items():

        def _make_handler(route_parts: tuple[str, ...]) -> Any:
            def _handler() -> HTMLResponse:
                path = PAGES_ROOT.joinpath(*route_parts)
                if not path.is_file():
                    raise HTTPException(status_code=404, detail=f"Missing fixture file: {path}")
                return HTMLResponse(path.read_text(encoding="utf-8"))

            return _handler

        app.get(f"/{slug}", response_class=HTMLResponse, name=slug)(_make_handler(parts))

    return app


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve synthetic ATS fixture pages")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    uvicorn.run(create_app(), host=args.host, port=args.port, log_level="warning")


class FixtureServer:
    """In-process fixture server for pytest session fixtures."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8765) -> None:
        self.host = host
        self.port = port
        self._thread: threading.Thread | None = None
        self._server: uvicorn.Server | None = None

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def start(self) -> str:
        config = uvicorn.Config(create_app(), host=self.host, port=self.port, log_level="warning")
        self._server = uvicorn.Server(config)

        def _run() -> None:
            assert self._server is not None
            self._server.run()

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()
        return self.base_url

    def stop(self) -> None:
        if self._server is not None:
            self._server.should_exit = True
        if self._thread is not None:
            self._thread.join(timeout=5)
