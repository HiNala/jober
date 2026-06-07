from __future__ import annotations

import os
from typing import Any

import httpx


class JoberApiClient:
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or os.getenv("JOBER_API_URL") or "http://localhost:8000").rstrip(
            "/"
        )

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def list_jobs(self) -> list[dict[str, Any]]:
        with httpx.Client(timeout=30.0) as client:
            res = client.get(self._url("/api/job-targets"))
            res.raise_for_status()
            body = res.json()
            return list(body.get("items", body))

    def fill_fixture(self, job_id: str, fixture_html: str) -> dict[str, Any]:
        with httpx.Client(timeout=120.0) as client:
            res = client.post(
                self._url(f"/api/job-targets/{job_id}/fill-form"),
                json={"fixture_html": fixture_html},
            )
            res.raise_for_status()
            return res.json()

    def console_snapshot(self, run_id: str) -> dict[str, Any]:
        with httpx.Client(timeout=30.0) as client:
            res = client.get(self._url(f"/api/application-runs/{run_id}/console"))
            res.raise_for_status()
            return res.json()

    def resolve_checkpoint(self, run_id: str, checkpoint_id: str, action: str) -> dict[str, Any]:
        with httpx.Client(timeout=60.0) as client:
            res = client.post(
                self._url(f"/api/application-runs/{run_id}/checkpoints/{checkpoint_id}/resolve"),
                json={"action": action},
            )
            res.raise_for_status()
            return res.json()

    def stream_events(self, run_id: str, after_seq: int = 0):
        url = self._url(f"/api/application-runs/{run_id}/events")
        if after_seq:
            url = f"{url}?after_seq={after_seq}"
        with httpx.Client(timeout=None) as client:
            with client.stream("GET", url, headers={"Accept": "text/event-stream"}) as response:
                response.raise_for_status()
                event: dict[str, str] = {}
                for line in response.iter_lines():
                    if line is None:
                        continue
                    if line == "":
                        if "data" in event:
                            yield event
                        event = {}
                        continue
                    if line.startswith(":"):
                        continue
                    key, _, value = line.partition(":")
                    event[key.strip()] = value.strip()
                    if key.strip() == "data":
                        event["data"] = value.strip()
