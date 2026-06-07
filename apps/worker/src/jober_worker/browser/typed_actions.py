from __future__ import annotations

import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal, cast

from playwright.sync_api import Page

from jober_worker.browser.actions import BrowserActions, Observation
from jober_worker.browser.locators import resolve_field_locator, resolve_file_input
from jober_worker.storage import ObjectStorage


class TypedBrowserActions(BrowserActions):
    """Typed fill/upload tools with locator priority and event emission."""

    def __init__(
        self,
        page: Page,
        *,
        attempt_id: uuid.UUID | None = None,
        run_id: uuid.UUID | None = None,
        attempt_index: int = 1,
        on_event: Callable[[Observation, str | None, str | None], None] | None = None,
        storage: ObjectStorage | None = None,
    ) -> None:
        super().__init__(page)
        self._attempt_id = attempt_id
        self._run_id = run_id
        self._attempt_index = attempt_index
        self._on_event = on_event
        self._storage = storage or ObjectStorage()

    def _emit(
        self,
        event_type: str,
        message: str,
        *,
        selector: str | None = None,
        screenshot: bool = False,
        metadata: dict[str, Any] | None = None,
        level: str = "info",
    ) -> Observation:
        screenshot_key: str | None = None
        if screenshot and self._run_id is not None:
            data = self.page.screenshot(full_page=False)
            screenshot_key = (
                f"runs/{self._run_id}/attempts/{self._attempt_index}/events/"
                f"{event_type}_{len(self.observations)}.png"
            )
            self._storage.put_bytes(screenshot_key, data, "image/png")
        obs = self.record_observation(
            event_type,
            message,
            metadata={**(metadata or {}), "level": level, "selector": selector},
        )
        if self._on_event is not None:
            self._on_event(obs, selector, screenshot_key)
        return obs

    def click_by_role(self, role: str, *, name: str | None = None) -> None:
        loc = (
            self.page.get_by_role(cast(Any, role), name=name)
            if name
            else self.page.get_by_role(cast(Any, role))
        )
        loc.first.click()
        self._emit(
            "click_by_role",
            f"Clicked role={role} name={name!r}",
            selector=f'role={role}',
            screenshot=True,
        )

    def click_by_text(self, text: str) -> None:
        self.page.get_by_text(text, exact=False).first.click()
        self._emit("click_by_text", f"Clicked text {text!r}", screenshot=True)

    def fill_by_label(self, label: str, value: str) -> tuple[str, str | None]:
        resolved = resolve_field_locator(
            self.page,
            label=label,
            field_key=label,
            field_type="text",
        )
        resolved.locator.fill(value)
        self._emit(
            "fill_by_label",
            f"Filled {label!r}",
            selector=resolved.selector,
            screenshot=True,
            metadata={"strategy": resolved.strategy},
        )
        return resolved.strategy, self._read_locator_value(resolved.locator)

    def select_by_label(self, label: str, value: str) -> tuple[str, str | None]:
        resolved = resolve_field_locator(
            self.page,
            label=label,
            field_key=label,
            field_type="select",
        )
        tag = resolved.locator.evaluate("el => el.tagName.toLowerCase()")
        if tag == "select":
            resolved.locator.select_option(label=value)
        else:
            resolved.locator.fill(value)
        self._emit(
            "select_by_label",
            f"Selected {label!r}",
            selector=resolved.selector,
            screenshot=True,
        )
        return resolved.strategy, self._read_locator_value(resolved.locator)

    def check_by_label(self, label: str, *, checked: bool = True) -> tuple[str, str | None]:
        resolved = resolve_field_locator(
            self.page,
            label=label,
            field_key=label,
            field_type="checkbox",
        )
        if checked:
            resolved.locator.check()
        else:
            resolved.locator.uncheck()
        self._emit("check_by_label", f"Checked {label!r}={checked}", selector=resolved.selector)
        return resolved.strategy, str(checked)

    def upload_file(self, control: str, file_path: str) -> tuple[str, str | None]:
        path = Path(file_path)
        if not path.exists():
            msg = f"Upload file missing: {file_path}"
            raise FileNotFoundError(msg)
        resolved = resolve_file_input(self.page, control=control, field_key=control)
        resolved.locator.set_input_files(str(path))
        self._emit(
            "upload_file",
            f"Uploaded {path.name} to {control!r}",
            selector=resolved.selector,
            screenshot=True,
            metadata={"file_key": path.name},
        )
        return resolved.strategy, path.name

    def read_value_by_label(self, label: str) -> str | None:
        resolved = resolve_field_locator(
            self.page,
            label=label,
            field_key=label,
            field_type="text",
        )
        return self._read_locator_value(resolved.locator)

    def _read_locator_value(self, locator: Any) -> str | None:
        try:
            tag = locator.evaluate("el => el.tagName.toLowerCase()")
            if tag == "select":
                return str(locator.evaluate("el => el.options[el.selectedIndex]?.text || ''"))
            if locator.evaluate("el => el.type === 'checkbox'"):
                return "true" if locator.is_checked() else "false"
            return str(locator.input_value())
        except Exception:  # noqa: BLE001
            return None

    def request_human_checkpoint(
        self,
        checkpoint_type: Literal[
            "login",
            "captcha",
            "two_factor",
            "sensitive_field",
            "manual_intervention",
        ],
        prompt: str,
    ) -> dict[str, str]:
        from datetime import UTC, datetime

        self._emit(
            "request_human_checkpoint",
            prompt,
            screenshot=True,
            metadata={"checkpoint_type": checkpoint_type},
            level="warning",
        )
        return {
            "checkpoint_type": checkpoint_type,
            "prompt": prompt,
            "requested_at": datetime.now(UTC).isoformat(),
        }

    def dom_snapshot(self) -> str:
        html = self.content_html()
        self._emit("dom_snapshot", f"Captured DOM ({len(html)} bytes)")
        return html
