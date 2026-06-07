from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any

from jober_extraction.gates import GateKind, detect_access_gates
from jober_fill.runner import FieldFillOutcome, ObservationInput, run_fill_loop
from jober_forms.scanner import scan_multistep_form
from sqlalchemy import text

from jober_worker.browser.checkpoints import gate_checkpoint
from jober_worker.browser.event_writer import persist_browser_event
from jober_worker.browser.session import browser_session
from jober_worker.browser.typed_actions import TypedBrowserActions
from jober_worker.db import get_sync_session
from jober_worker.fill_context import is_sensitive_observation, load_fill_context
from jober_worker.run_event_writer import persist_observation_as_run_event, persist_run_event
from jober_worker.storage import ObjectStorage


def _attempt_keys(run_id: uuid.UUID, attempt_index: int) -> dict[str, str]:
    base = f"runs/{run_id}/attempts/{attempt_index}"
    return {
        "trace": f"{base}/trace.zip",
        "screenshot": f"{base}/screenshot.png",
        "dom": f"{base}/dom.json",
    }


def run_fixture_form_fill(
    *,
    run_id: uuid.UUID,
    attempt_id: uuid.UUID,
    job_target_id: uuid.UUID,
    fixture_html: str,
    observations: list[dict[str, Any]],
    profile_values: dict[str, Any],
    observation_attempt_id: uuid.UUID | None = None,
    resume_path: str | None = None,
    cover_letter_path: str | None = None,
) -> dict[str, Any]:
    """CI-safe fill against inline HTML (no navigation)."""
    obs_attempt = observation_attempt_id or attempt_id
    attempt_index = 1
    keys = _attempt_keys(run_id, attempt_index)
    storage = ObjectStorage()
    file_paths: dict[str, str] = {}
    if resume_path:
        file_paths["resume_upload"] = resume_path
    if cover_letter_path:
        file_paths["cover_letter_upload"] = cover_letter_path

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

    persist_run_event(
        run_id=run_id,
        event_type="run.started",
        message="Fixture fill run started",
        attempt_index=attempt_index,
        payload={"job_target_id": str(job_target_id)},
    )

    with browser_session(run_id=run_id, attempt_index=attempt_index) as session:

        def _on_event(obs: Any, selector: str | None, screenshot_key: str | None) -> None:
            persist_browser_event(
                attempt_id=attempt_id,
                observation=obs,
                selector=selector,
                screenshot_key=screenshot_key,
            )
            persist_observation_as_run_event(
                run_id=run_id,
                attempt_index=attempt_index,
                event_type=obs.event_type,
                message=obs.message,
                screenshot_key=screenshot_key,
                payload={"url": obs.url, "selector": selector},
            )

        actions = TypedBrowserActions(
            session.page,
            attempt_id=attempt_id,
            run_id=run_id,
            attempt_index=attempt_index,
            on_event=_on_event,
            storage=storage,
        )
        session.page.set_content(fixture_html, wait_until="domcontentloaded")
        actions.wait_for_network_idle(timeout_ms=5000)

        html = actions.content_html()
        visible = actions.get_visible_text()
        gates = detect_access_gates(html, visible)
        if gates:
            gate = gates[0]
            checkpoint = actions.request_human_checkpoint(
                gate_checkpoint(gate),
                f"Resolve {gate.value} before filling.",
            )
            screenshot = actions.screenshot()
            storage.put_bytes(keys["screenshot"], screenshot, "image/png")
            _persist_fill_checkpoint(
                run_id=run_id,
                attempt_id=attempt_id,
                gate=gate,
                prompt=checkpoint["prompt"],
            )
            persist_run_event(
                run_id=run_id,
                event_type="human.required",
                message=checkpoint["prompt"],
                attempt_index=attempt_index,
                payload={"gate": gate.value},
                screenshot_key=keys["screenshot"],
            )
            return {
                "status": "needs_human",
                "gate": gate.value,
                "filled": [],
                "failed": [],
            }

        outcomes = _fill_with_rescan(actions, obs_inputs, profile_values, file_paths)
        sensitive = [o for o in outcomes if o.error == "sensitive_field_checkpoint"]
        if sensitive:
            actions.request_human_checkpoint(
                "sensitive_field",
                "Resolve sensitive fields before auto-fill.",
            )
            _persist_sensitive_checkpoint(run_id=run_id, prompt="Sensitive fields require review")
            persist_run_event(
                run_id=run_id,
                event_type="human.required",
                message="Sensitive fields require review",
                attempt_index=attempt_index,
                payload={"gate": "sensitive_field"},
            )
            _update_observation_statuses(obs_attempt, outcomes, obs_inputs)
            return {
                "status": "needs_human",
                "gate": "sensitive_field",
                "needs_review": [o.field_key for o in sensitive],
            }

        dom_key = keys["dom"]
        storage.put_bytes(dom_key, actions.dom_snapshot().encode(), "text/html")
        screenshot = actions.screenshot()
        storage.put_bytes(keys["screenshot"], screenshot, "image/png")

        _update_observation_statuses(obs_attempt, outcomes, obs_inputs)
        _persist_fill_success(run_id, attempt_id, keys)
        for outcome in outcomes:
            if outcome.status == "filled":
                persist_run_event(
                    run_id=run_id,
                    event_type="field.filled",
                    message=f'filled field="{outcome.field_key}" status=ok',
                    attempt_index=attempt_index,
                    payload={"field_key": outcome.field_key},
                )
        persist_run_event(
            run_id=run_id,
            event_type="state.changed",
            message="Fill step completed",
            attempt_index=attempt_index,
            payload={"status": "fill_form", "step": "fill_form"},
            screenshot_key=keys["screenshot"],
        )

        return {
            "status": "succeeded",
            "filled": [o.field_key for o in outcomes if o.status == "filled"],
            "failed": [o.field_key for o in outcomes if o.status == "failed"],
            "needs_review": [o.field_key for o in outcomes if o.status == "needs_review"],
            "fill_diffs": {
                o.field_key: o.fill_diff.to_dict()
                for o in outcomes
                if o.fill_diff is not None
            },
            "artifact_keys": keys,
        }


def run_browser_form_fill(
    *,
    run_id: uuid.UUID,
    attempt_id: uuid.UUID,
    job_target_id: uuid.UUID,
    url: str,
) -> dict[str, Any]:
    ctx = load_fill_context(job_target_id, attempt_id)
    attempt_index = 1
    keys = _attempt_keys(run_id, attempt_index)
    storage = ObjectStorage()
    try:
        file_paths: dict[str, str] = {}
        if ctx.resume_path:
            file_paths["resume_upload"] = str(ctx.resume_path)
        if ctx.cover_letter_path:
            file_paths["cover_letter_upload"] = str(ctx.cover_letter_path)

        obs_inputs = [
            ObservationInput(
                field_key=o.field_key,
                label=o.label,
                field_type=o.field_type,
                mapped_profile_field=o.mapped_profile_field,
                status=o.status,
                is_sensitive=is_sensitive_observation(o),
            )
            for o in ctx.observations
        ]

        with browser_session(run_id=run_id, attempt_index=attempt_index) as session:

            def _on_event(obs: Any, selector: str | None, screenshot_key: str | None) -> None:
                persist_browser_event(
                    attempt_id=attempt_id,
                    observation=obs,
                    selector=selector,
                    screenshot_key=screenshot_key,
                )

            actions = TypedBrowserActions(
                session.page,
                attempt_id=attempt_id,
                run_id=run_id,
                attempt_index=attempt_index,
                on_event=_on_event,
                storage=storage,
            )
            actions.goto(url)
            actions.wait_for_network_idle(timeout_ms=20000)

            html = actions.content_html()
            visible = actions.get_visible_text()
            gates = detect_access_gates(html, visible)
            if gates:
                gate = gates[0]
                checkpoint = actions.request_human_checkpoint(
                    gate_checkpoint(gate),
                    f"Resolve {gate.value} before filling.",
                )
                screenshot = actions.screenshot()
                storage.put_bytes(keys["screenshot"], screenshot, "image/png")
                _persist_fill_checkpoint(
                    run_id=run_id,
                    attempt_id=attempt_id,
                    gate=gate,
                    prompt=checkpoint["prompt"],
                )
                return {"status": "needs_human", "gate": gate.value}

            discover_attempt = ctx.observation_attempt_id or attempt_id
            outcomes = _fill_with_rescan(actions, obs_inputs, ctx.profile_values, file_paths)
            storage.put_bytes(keys["dom"], actions.dom_snapshot().encode(), "text/html")
            storage.put_bytes(keys["screenshot"], actions.screenshot(), "image/png")
            _update_observation_statuses(discover_attempt, outcomes, obs_inputs)
            _persist_fill_success(run_id, attempt_id, keys)
            return {
                "status": "succeeded",
                "filled": [o.field_key for o in outcomes if o.status == "filled"],
                "failed": [o.field_key for o in outcomes if o.status == "failed"],
            }
    finally:
        ctx.temp_dir.cleanup()


def _fill_with_rescan(
    actions: TypedBrowserActions,
    observations: list[ObservationInput],
    profile_values: dict[str, Any],
    file_paths: dict[str, str],
) -> list[FieldFillOutcome]:
    outcomes: list[FieldFillOutcome] = run_fill_loop(
        observations, profile_values, file_paths, actions
    )
    html = actions.content_html()
    new_fields = scan_multistep_form(html)
    if new_fields:
        actions.record_observation(
            "rescan",
            f"Discovered {len(new_fields)} fields after fill",
            metadata={"field_keys": [f.field_key for f in new_fields]},
        )
    return outcomes


def _persist_sensitive_checkpoint(*, run_id: uuid.UUID, prompt: str) -> None:
    now = datetime.now(UTC)
    with get_sync_session() as session:
        session.execute(
            text(
                """
                UPDATE application_runs
                SET status = 'needs_human',
                    human_review_required_reason = 'sensitive_field',
                    updated_at = :now
                WHERE id = :run_id
                """
            ),
            {"now": now, "run_id": str(run_id)},
        )
        session.execute(
            text(
                """
                INSERT INTO human_checkpoints (
                    id, run_id, checkpoint_type, prompt, status, created_at, updated_at
                ) VALUES (
                    gen_random_uuid(), :run_id, 'sensitive_field', :prompt, 'open', :now, :now
                )
                """
            ),
            {"run_id": str(run_id), "prompt": prompt, "now": now},
        )
        session.commit()


def _update_observation_statuses(
    attempt_id: uuid.UUID,
    outcomes: list[FieldFillOutcome],
    obs_inputs: list[ObservationInput],
) -> None:
    keyed = {o.field_key: o for o in obs_inputs}
    with get_sync_session() as session:
        for outcome in outcomes:
            obs = keyed.get(outcome.field_key)
            if obs is None:
                continue
            evidence = json.dumps(outcome.evidence or {})
            session.execute(
                text(
                    """
                    UPDATE form_field_observations
                    SET status = :status,
                        evidence = COALESCE(evidence, '{}'::jsonb) || CAST(:evidence AS jsonb),
                        updated_at = :now
                    WHERE attempt_id = :attempt_id AND field_key = :field_key
                    """
                ),
                {
                    "status": outcome.status,
                    "evidence": evidence,
                    "now": datetime.now(UTC),
                    "attempt_id": str(attempt_id),
                    "field_key": outcome.field_key,
                },
            )
        session.commit()


def _persist_fill_checkpoint(
    *,
    run_id: uuid.UUID,
    attempt_id: uuid.UUID,
    gate: GateKind,
    prompt: str,
) -> None:
    checkpoint_type = {
        GateKind.LOGIN: "login",
        GateKind.CAPTCHA: "captcha",
        GateKind.TWO_FACTOR: "two_factor",
    }[gate]
    now = datetime.now(UTC)
    with get_sync_session() as session:
        session.execute(
            text(
                """
                UPDATE application_runs
                SET status = 'needs_human',
                    human_review_required_reason = :reason,
                    updated_at = :now
                WHERE id = :run_id
                """
            ),
            {"reason": gate.value, "now": now, "run_id": str(run_id)},
        )
        session.execute(
            text(
                """
                INSERT INTO human_checkpoints (
                    id, run_id, checkpoint_type, prompt, status, created_at, updated_at
                ) VALUES (
                    gen_random_uuid(), :run_id, :ctype, :prompt, 'open', :now, :now
                )
                """
            ),
            {
                "run_id": str(run_id),
                "ctype": checkpoint_type,
                "prompt": prompt,
                "now": now,
            },
        )
        session.commit()


def _persist_fill_success(
    run_id: uuid.UUID,
    attempt_id: uuid.UUID,
    keys: dict[str, str],
) -> None:
    now = datetime.now(UTC)
    with get_sync_session() as session:
        session.execute(
            text(
                """
                UPDATE application_runs
                SET status = 'fill_form', current_step = 'fill_form',
                    completed_at = :now, updated_at = :now
                WHERE id = :run_id
                """
            ),
            {"now": now, "run_id": str(run_id)},
        )
        session.execute(
            text(
                """
                UPDATE application_attempts
                SET status = 'succeeded',
                    final_screenshot_object_key = :screenshot,
                    dom_snapshot_object_key = :dom,
                    completed_at = :now,
                    updated_at = :now
                WHERE id = :attempt_id
                """
            ),
            {
                "screenshot": keys["screenshot"],
                "dom": keys["dom"],
                "now": now,
                "attempt_id": str(attempt_id),
            },
        )
        session.commit()

