from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal

from playwright.sync_api import Page


@dataclass
class Observation:
    event_type: str
    message: str
    url: str | None = None
    metadata: dict[str, Any] | None = None


class BrowserActions:
    """Deterministic action API — no model-driven freeform automation."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.observations: list[Observation] = []

    def goto(self, url: str, *, wait_until: str = "domcontentloaded") -> None:
        self.page.goto(url, wait_until=wait_until)
        self.record_observation("goto", f"Opened {url}", url=url)

    def get_visible_text(self) -> str:
        text = self.page.inner_text("body")
        self.record_observation("get_visible_text", f"Captured {len(text)} chars")
        return text

    def extract_accessibility_tree(self) -> dict[str, Any]:
        snapshot = self.page.accessibility.snapshot()
        tree = snapshot or {}
        self.record_observation("extract_accessibility_tree", "Captured a11y tree")
        return tree if isinstance(tree, dict) else {"children": tree}

    def extract_form_controls(self) -> list[dict[str, Any]]:
        controls = self.page.evaluate(
            """() => Array.from(document.querySelectorAll('input,select,textarea,button'))
            .map((el) => ({
              tag: el.tagName.toLowerCase(),
              type: el.getAttribute('type'),
              name: el.getAttribute('name'),
              id: el.id || null,
              label: el.getAttribute('aria-label'),
            }))"""
        )
        self.record_observation("extract_form_controls", f"Found {len(controls)} controls")
        return controls

    def screenshot(self) -> bytes:
        data = self.page.screenshot(full_page=True)
        self.record_observation("screenshot", "Captured screenshot")
        return data

    def wait_for_network_idle(self, *, timeout_ms: int = 15000) -> None:
        self.page.wait_for_load_state("networkidle", timeout=timeout_ms)
        self.record_observation("wait_for_network_idle", "Network idle")

    def evaluate_js_readonly(self, expression: str) -> Any:
        if not expression.strip().startswith("(") and not expression.strip().startswith("["):
            msg = "Read-only evaluate must be an expression literal"
            raise ValueError(msg)
        result = self.page.evaluate(expression)
        self.record_observation("evaluate_js_readonly", "Evaluated read-only JS")
        return result

    def record_observation(
        self,
        event_type: str,
        message: str,
        *,
        url: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Observation:
        obs = Observation(
            event_type=event_type,
            message=message,
            url=url or self.page.url,
            metadata=metadata,
        )
        self.observations.append(obs)
        return obs

    def request_human_checkpoint(
        self,
        checkpoint_type: Literal["login", "captcha", "two_factor"],
        prompt: str,
    ) -> dict[str, str]:
        self.record_observation(
            "request_human_checkpoint",
            prompt,
            metadata={"checkpoint_type": checkpoint_type},
        )
        return {
            "checkpoint_type": checkpoint_type,
            "prompt": prompt,
            "requested_at": datetime.now(UTC).isoformat(),
        }

    def content_html(self) -> str:
        return self.page.content()

    def dump_observations_json(self) -> str:
        payload = [
            {
                "event_type": o.event_type,
                "message": o.message,
                "url": o.url,
                "metadata": o.metadata,
            }
            for o in self.observations
        ]
        return json.dumps(payload)
