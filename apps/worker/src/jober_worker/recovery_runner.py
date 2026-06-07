from __future__ import annotations

import uuid
from typing import Any

from jober_fill.runner import ObservationInput, run_fill_loop
from jober_recover.strategy import RecoveryStrategy
from jober_recover.taxonomy import classify_failure
from playwright.sync_api import Page

from jober_worker.attempt_manager import load_checkpoint, persist_checkpoint
from jober_worker.browser.session import browser_session
from jober_worker.browser.typed_actions import TypedBrowserActions
from jober_worker.fill_runner import _attempt_keys
from jober_worker.storage import ObjectStorage


class CssLocatorFillActions:
    """Intentionally brittle strategy for recovery tests."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def fill_by_label(self, label: str, value: str) -> tuple[str, str | None]:
        del label, value
        loc = self.page.locator("#legacy-email")
        if loc.count() == 0:
            msg = "Could not resolve #legacy-email selector"
            raise ValueError(msg)
        loc.fill("wrong")
        return "css", None

    def select_by_label(self, label: str, value: str) -> tuple[str, str | None]:
        return self.fill_by_label(label, value)

    def check_by_label(self, label: str, *, checked: bool = True) -> tuple[str, str | None]:
        return self.fill_by_label(label, str(checked))

    def upload_file(
        self, control: str, file_path: str, *, field_key: str | None = None
    ) -> tuple[str, str | None]:
        del control, file_path, field_key
        msg = "Upload not supported in css recovery stub"
        raise ValueError(msg)

    def read_value_by_label(self, label: str) -> str | None:
        del label
        return None


def run_fixture_recovery_fill(
    *,
    run_id: uuid.UUID,
    attempt_id: uuid.UUID,
    fixture_html: str,
    observations: list[dict[str, Any]],
    profile_values: dict[str, Any],
    strategy: RecoveryStrategy,
) -> dict[str, Any]:
    attempt_index = 1
    keys = _attempt_keys(run_id, attempt_index)
    storage = ObjectStorage()
    checkpoint = load_checkpoint(run_id)
    completed_fields = set(checkpoint.get("filled_fields", []))

    obs_inputs = [
        ObservationInput(
            field_key=str(o["field_key"]),
            label=o.get("label"),
            field_type=o.get("field_type"),
            mapped_profile_field=o.get("mapped_profile_field"),
            status=(
                "skipped"
                if o["field_key"] in completed_fields
                else str(o.get("status", "skipped"))
            ),
            is_sensitive=bool(o.get("is_sensitive", False)),
        )
        for o in observations
    ]

    with browser_session(run_id=run_id, attempt_index=attempt_index) as session:
        actions: Any
        if strategy.locator_mode == "css":
            actions = CssLocatorFillActions(session.page)
        else:
            actions = TypedBrowserActions(session.page, run_id=run_id, storage=storage)

        session.page.set_content(fixture_html, wait_until="domcontentloaded")

        try:
            outcomes = run_fill_loop(obs_inputs, profile_values, {}, actions)
            filled = [o.field_key for o in outcomes if o.status == "filled"]
            failed = [o for o in outcomes if o.status == "failed"]
            if failed:
                err = failed[0].error or "fill failed"
                failure_class = classify_failure(step="fill_form", error_message=err)
                screenshot = session.page.screenshot()
                storage.put_bytes(keys["screenshot"], screenshot, "image/png")
                storage.put_bytes(keys["dom"], session.page.content().encode(), "text/html")
                return {
                    "status": "failed",
                    "failure_class": failure_class.value,
                    "error": err,
                    "artifact_keys": keys,
                }

            all_filled = list(set(completed_fields) | set(filled))
            persist_checkpoint(
                run_id=run_id,
                step="fill_form",
                data={"filled_fields": all_filled, "strategy": strategy.name},
            )
            screenshot = session.page.screenshot()
            storage.put_bytes(keys["screenshot"], screenshot, "image/png")
            storage.put_bytes(keys["dom"], session.page.content().encode(), "text/html")
            return {
                "status": "succeeded",
                "filled": all_filled,
                "strategy": strategy.name,
                "artifact_keys": keys,
                "resumed_from_checkpoint": bool(completed_fields),
            }
        except Exception as exc:  # noqa: BLE001
            err = str(exc)
            failure_class = classify_failure(step="fill_form", error_message=err)
            screenshot = session.page.screenshot()
            storage.put_bytes(keys["screenshot"], screenshot, "image/png")
            storage.put_bytes(keys["dom"], session.page.content().encode(), "text/html")
            return {
                "status": "failed",
                "failure_class": failure_class.value,
                "error": err,
                "artifact_keys": keys,
            }
