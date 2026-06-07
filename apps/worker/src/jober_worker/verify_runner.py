from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any

from jober_fill.runner import ObservationInput, run_fill_loop
from jober_verify.idempotency import detect_already_applied_on_page
from jober_verify.readiness import evaluate_readiness
from sqlalchemy import text

from jober_worker.browser.session import browser_session
from jober_worker.browser.typed_actions import TypedBrowserActions
from jober_worker.db import get_sync_session
from jober_worker.fill_runner import _attempt_keys
from jober_worker.storage import ObjectStorage


def run_fixture_verify_readiness(
    *,
    run_id: uuid.UUID,
    attempt_id: uuid.UUID,
    fixture_html: str,
    observations: list[dict[str, Any]],
    profile_values: dict[str, Any],
    file_paths: dict[str, str] | None = None,
    refilled: bool = True,
    require_uploads: bool = False,
) -> dict[str, Any]:
    attempt_index = 1
    keys = _attempt_keys(run_id, attempt_index)
    storage = ObjectStorage()
    paths = file_paths or {}

    obs_inputs = [
        ObservationInput(
            field_key=str(o["field_key"]),
            label=o.get("label"),
            field_type=o.get("field_type"),
            mapped_profile_field=o.get("mapped_profile_field"),
            status=str(o.get("status", "skipped")),
            is_sensitive=bool(o.get("is_sensitive", False)),
        )
        for o in observations
    ]

    with browser_session(run_id=run_id, attempt_index=attempt_index) as session:
        actions = TypedBrowserActions(
            session.page,
            attempt_id=attempt_id,
            run_id=run_id,
            attempt_index=attempt_index,
            storage=storage,
        )
        session.page.set_content(fixture_html, wait_until="domcontentloaded")
        actions.wait_for_network_idle(timeout_ms=5000)

        html = actions.content_html()
        visible = actions.get_visible_text()
        if detect_already_applied_on_page(html=html, visible_text=visible):
            screenshot = actions.screenshot()
            storage.put_bytes(keys["screenshot"], screenshot, "image/png")
            return {
                "status": "already_applied",
                "readiness": {"passed": False, "checks": []},
                "artifact_keys": keys,
                "gate": "already_applied",
            }

        if refilled:
            run_fill_loop(obs_inputs, profile_values, paths, actions)

        report = evaluate_readiness(session.page, require_uploads=require_uploads)
        screenshot = actions.screenshot()
        storage.put_bytes(keys["screenshot"], screenshot, "image/png")
        storage.put_bytes(keys["dom"], actions.dom_snapshot().encode(), "text/html")

        return {
            "status": "ready" if report.passed else "not_ready",
            "readiness": report.to_dict(),
            "artifact_keys": keys,
        }


def persist_verify_result(
    *,
    run_id: uuid.UUID,
    attempt_id: uuid.UUID,
    passed: bool,
    readiness: dict[str, Any],
    artifact_keys: dict[str, str],
    human_summary: str,
    already_applied: bool = False,
) -> None:
    now = datetime.now(UTC)
    if already_applied:
        status = "skipped"
        step = "verify_ready"
        reason = "already_applied"
    elif passed:
        status = "review_and_submit"
        step = "review_and_submit"
        reason = None
    else:
        status = "needs_human"
        step = "verify_ready"
        reason = "readiness_failed"

    with get_sync_session() as session:
        session.execute(
            text(
                """
                UPDATE application_runs
                SET status = :status,
                    current_step = :step,
                    human_review_required_reason = :reason,
                    updated_at = :now
                WHERE id = :run_id
                """
            ),
            {
                "status": status,
                "step": step,
                "reason": reason,
                "now": now,
                "run_id": str(run_id),
            },
        )
        session.execute(
            text(
                """
                UPDATE application_attempts
                SET final_screenshot_object_key = :screenshot,
                    dom_snapshot_object_key = :dom,
                    updated_at = :now
                WHERE id = :attempt_id
                """
            ),
            {
                "screenshot": artifact_keys.get("screenshot"),
                "dom": artifact_keys.get("dom"),
                "now": now,
                "attempt_id": str(attempt_id),
            },
        )
        if passed:
            session.execute(
                text(
                    """
                    INSERT INTO human_checkpoints (
                        id, run_id, checkpoint_type, prompt, options, status,
                        created_at, updated_at
                    ) VALUES (
                        gen_random_uuid(), :run_id, 'review_submit', :prompt,
                        CAST(:options AS jsonb), 'open', :now, :now
                    )
                    """
                ),
                {
                    "run_id": str(run_id),
                    "prompt": "Review the application and submit when ready.",
                    "options": json.dumps({"human_summary": human_summary, "readiness": readiness}),
                    "now": now,
                },
            )
        session.commit()
