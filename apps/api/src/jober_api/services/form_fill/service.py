from __future__ import annotations

import asyncio
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.application_attempt import ApplicationAttempt
from jober_api.models.enums import AttemptStatus, RunPolicy, RunStatus
from jober_api.repositories.application_run import ApplicationRunRepository
from jober_api.repositories.form_field_observation import FormFieldObservationRepository
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.repositories.user_profile import UserProfileRepository
from jober_api.services.form_discovery.service import _serialize_observation
from jober_api.vault.field_registry import FIELD_BY_KEY, FieldTier
from jober_api.vault.fill_policy import resolve_field_fill


class FillBlockedError(Exception):
    def __init__(self, *, gate: str, run_id: uuid.UUID) -> None:
        self.gate = gate
        self.run_id = run_id
        super().__init__(gate)


async def fill_from_fixture_html(
    session: AsyncSession,
    *,
    job_target_id: uuid.UUID,
    fixture_html: str,
    observations_attempt_id: uuid.UUID | None = None,
) -> dict[str, Any]:
    jobs = JobTargetRepository(session)
    job = await jobs.get(job_target_id)
    if job is None:
        msg = "Job target not found"
        raise ValueError(msg)

    obs_repo = FormFieldObservationRepository(session)
    if observations_attempt_id:
        rows = await obs_repo.list_for_attempt(observations_attempt_id)
    else:
        rows = await obs_repo.list_for_job_latest(job_target_id)
    if not rows:
        msg = "No field observations — run discover-form first"
        raise ValueError(msg)

    profiles = UserProfileRepository(session)
    profile = await profiles.get_singleton()
    profile_values: dict[str, Any] = {}
    if profile:
        for row in rows:
            mapped = row.mapped_profile_field
            if not mapped or mapped in ("resume_upload", "cover_letter_upload"):
                continue
            resolution = resolve_field_fill(profile, mapped)
            if resolution.outcome.value == "value":
                profile_values[mapped] = resolution.value

    runs = ApplicationRunRepository(session)
    now = datetime.now(UTC)
    run = await runs.create(
        job_target_id=job_target_id,
        status=RunStatus.FILL_FORM,
        current_step=RunStatus.FILL_FORM,
        policy=RunPolicy.DRY_RUN,
        started_at=now,
    )
    attempt = ApplicationAttempt(
        run_id=run.id,
        attempt_index=1,
        status=AttemptStatus.RUNNING,
        strategy_name="fixture_fill_form",
        started_at=now,
    )
    session.add(attempt)
    await session.flush()
    await session.refresh(attempt)

    observation_payloads = []
    for row in rows:
        spec = FIELD_BY_KEY.get(row.mapped_profile_field or "")
        observation_payloads.append(
            {
                "field_key": row.field_key,
                "label": row.label,
                "field_type": row.field_type,
                "mapped_profile_field": row.mapped_profile_field,
                "status": row.status.value,
                "is_sensitive": spec is not None and spec.tier == FieldTier.SENSITIVE,
            }
        )

    from jober_worker.fill_runner import run_fixture_form_fill

    discover_attempt_id = rows[0].attempt_id
    fill_run_id = run.id
    fill_attempt_id = attempt.id
    await session.commit()

    result = await asyncio.to_thread(
        run_fixture_form_fill,
        run_id=fill_run_id,
        attempt_id=fill_attempt_id,
        job_target_id=job_target_id,
        fixture_html=fixture_html,
        observations=observation_payloads,
        profile_values=profile_values,
        observation_attempt_id=discover_attempt_id,
    )

    attempt_row = await session.get(ApplicationAttempt, fill_attempt_id)
    if attempt_row is None:
        msg = "Fill run state lost after browser thread"
        raise ValueError(msg)
    attempt = attempt_row

    if result.get("status") == "needs_human":
        attempt.status = AttemptStatus.FAILED
        attempt.completed_at = now
        await runs.update_fields(fill_run_id, status=RunStatus.NEEDS_HUMAN, completed_at=now)
        raise FillBlockedError(gate=str(result.get("gate", "unknown")), run_id=fill_run_id)

    attempt.status = AttemptStatus.SUCCEEDED
    attempt.completed_at = now
    await runs.update_fields(fill_run_id, status=RunStatus.FILL_FORM, completed_at=now)

    updated = await obs_repo.list_for_attempt(discover_attempt_id)
    fill_diffs: dict[str, object] = result.get("fill_diffs", {})
    filled_keys = set(result.get("filled", []))
    items: list[dict[str, object]] = []
    for row in updated:
        item = _serialize_observation(row)
        payload = item.model_dump()
        if row.field_key in filled_keys:
            payload["status"] = "filled"
        if row.field_key in fill_diffs:
            evidence = dict(payload.get("evidence") or {})
            evidence["fill_diff"] = fill_diffs[row.field_key]
            payload["evidence"] = evidence
        items.append(payload)
    return {
        "run_id": str(fill_run_id),
        "attempt_id": str(fill_attempt_id),
        "status": result.get("status"),
        "filled": result.get("filled", []),
        "failed": result.get("failed", []),
        "fill_diffs": fill_diffs,
        "items": items,
    }


async def enqueue_browser_fill(
    session: AsyncSession,
    *,
    job_target_id: uuid.UUID,
) -> dict[str, Any]:
    jobs = JobTargetRepository(session)
    job = await jobs.get(job_target_id)
    if job is None:
        msg = "Job target not found"
        raise ValueError(msg)
    if not job.direct_apply_url:
        msg = "Job target has no direct_apply_url"
        raise ValueError(msg)

    runs = ApplicationRunRepository(session)
    now = datetime.now(UTC)
    run = await runs.create(
        job_target_id=job_target_id,
        status=RunStatus.FILL_FORM,
        current_step=RunStatus.FILL_FORM,
        policy=RunPolicy.DRY_RUN,
        started_at=now,
    )
    attempt = ApplicationAttempt(
        run_id=run.id,
        attempt_index=1,
        status=AttemptStatus.PENDING,
        strategy_name="browser_fill_form",
        started_at=now,
    )
    session.add(attempt)
    await session.flush()

    task_id: str | None = None
    warning: str | None = None
    try:
        from jober_worker.tasks import fill_form

        async_result = fill_form.delay(str(run.id), str(job_target_id), job.direct_apply_url)
        task_id = async_result.id
    except Exception as exc:  # noqa: BLE001
        warning = f"Celery dispatch failed: {exc}"

    payload: dict[str, Any] = {
        "run_id": str(run.id),
        "status": "queued",
        "task_id": task_id,
    }
    if warning:
        payload["warning"] = warning
    return payload
