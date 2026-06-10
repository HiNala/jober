from __future__ import annotations

import asyncio
import json
import uuid
from collections.abc import AsyncIterator, Iterable
from typing import Any

from jober_schemas.run_console import RunEventType
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.application_attempt import ApplicationAttempt
from jober_api.models.application_run import ApplicationRun
from jober_api.models.enums import CheckpointStatus, CheckpointType, RunStatus
from jober_api.models.human_checkpoint import HumanCheckpoint
from jober_api.models.job_target import JobTarget
from jober_api.models.run_event import RunEvent
from jober_api.privacy.redaction import scrub_event_message
from jober_api.repositories.application_run import ApplicationRunRepository
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.repositories.run_event import RunEventRepository
from jober_api.services.verification.service import skip_submit, submit_application
from jober_api.storage.keys import (
    run_attempt_dom_key,
    run_attempt_screenshot_key,
    run_attempt_trace_key,
    run_attempt_video_key,
)
from jober_api.storage.minio_client import ObjectStorage

_SCREENSHOT_THROTTLE_SEC = 2.0
_SSE_MAX_EVENTS_PER_POLL = 50
_SSE_HEARTBEAT_SEC = 15.0
_SSE_RETRY_MS = 3000


async def append_run_event(
    session: AsyncSession,
    *,
    run_id: uuid.UUID,
    event_type: str | RunEventType,
    message: str,
    level: str = "info",
    payload: dict[str, Any] | None = None,
    screenshot_key: str | None = None,
    attempt_index: int | None = None,
) -> RunEvent:
    repo = RunEventRepository(session)
    return await repo.append(
        run_id=run_id,
        event_type=str(event_type),
        message=message,
        level=level,
        payload=payload,
        screenshot_key=screenshot_key,
        attempt_index=attempt_index,
    )


def _event_to_dict(event: RunEvent, screenshot_url: str | None = None) -> dict[str, Any]:
    return {
        "id": str(event.id),
        "seq": int(event.seq),
        "ts": event.ts.isoformat(),
        "event_type": event.event_type,
        "level": event.level,
        "message": event.message,
        "payload": event.payload or {},
        "screenshot_key": event.screenshot_key,
        "screenshot_url": screenshot_url,
        "attempt_index": event.attempt_index,
    }


async def _presign(storage: ObjectStorage, key: str | None) -> str | None:
    if not key:
        return None
    try:
        return await storage.presigned_get(key)
    except Exception:  # noqa: BLE001
        return None


async def _presign_map(storage: ObjectStorage, keys: Iterable[str | None]) -> dict[str, str | None]:
    unique = list(dict.fromkeys(key for key in keys if key))
    if not unique:
        return {}
    urls = await asyncio.gather(*[_presign(storage, key) for key in unique])
    return dict(zip(unique, urls, strict=True))


def _cached_url(cache: dict[str, str | None], key: str | None) -> str | None:
    if not key:
        return None
    return cache.get(key)


def _coalesce_screenshot_events(events: list[RunEvent]) -> list[RunEvent]:
    """Keep all textual events; throttle browser.screenshot to latest per bucket."""
    out: list[RunEvent] = []
    last_screenshot_seq = 0
    pending_screenshot: RunEvent | None = None
    for event in events:
        if event.event_type != RunEventType.BROWSER_SCREENSHOT.value:
            if pending_screenshot is not None:
                out.append(pending_screenshot)
                pending_screenshot = None
            out.append(event)
            continue
        if int(event.seq) - last_screenshot_seq >= 1:
            pending_screenshot = event
            last_screenshot_seq = int(event.seq)
    if pending_screenshot is not None:
        out.append(pending_screenshot)
    return out


async def get_console_snapshot(
    session: AsyncSession,
    run_id: uuid.UUID,
    tenant_id: uuid.UUID | None = None,
) -> dict[str, Any]:
    runs = ApplicationRunRepository(session, tenant_id)
    run = await runs.get(run_id)
    if run is None:
        msg = "Run not found"
        raise ValueError(msg)

    jobs = JobTargetRepository(session, tenant_id)
    job = await jobs.get(run.job_target_id)
    if job is None:
        msg = "Job target not found"
        raise ValueError(msg)

    storage = ObjectStorage()
    events_repo = RunEventRepository(session)
    events = await events_repo.list_since(run_id, after_seq=0, limit=1000)
    coalesced = _coalesce_screenshot_events(events)

    latest_screenshot_key: str | None = None
    for event in reversed(events):
        if event.screenshot_key:
            latest_screenshot_key = event.screenshot_key
            break
    if latest_screenshot_key is None:
        attempt_stmt = (
            select(ApplicationAttempt)
            .where(ApplicationAttempt.run_id == run_id)
            .order_by(ApplicationAttempt.attempt_index.desc())
            .limit(1)
        )
        attempt = (await session.execute(attempt_stmt)).scalar_one_or_none()
        if attempt and attempt.final_screenshot_object_key:
            latest_screenshot_key = attempt.final_screenshot_object_key

    cp_stmt = (
        select(HumanCheckpoint)
        .where(
            HumanCheckpoint.run_id == run_id,
            HumanCheckpoint.status == CheckpointStatus.OPEN,
        )
        .order_by(HumanCheckpoint.created_at.desc())
        .limit(1)
    )
    checkpoint = (await session.execute(cp_stmt)).scalar_one_or_none()
    open_checkpoint = None
    if checkpoint:
        open_checkpoint = {
            "id": str(checkpoint.id),
            "checkpoint_type": checkpoint.checkpoint_type.value,
            "prompt": checkpoint.prompt,
            "options": checkpoint.options or {},
        }

    attempt_rows = list(
        (
            await session.execute(
                select(ApplicationAttempt)
                .where(ApplicationAttempt.run_id == run_id)
                .order_by(ApplicationAttempt.attempt_index.asc())
            )
        ).scalars()
    )
    presign_keys: list[str | None] = [latest_screenshot_key]
    state_changed = RunEventType.STATE_CHANGED.value
    state_events = [event for event in events if event.event_type == state_changed]
    presign_keys.extend(event.screenshot_key for event in state_events)
    presign_keys.extend(event.screenshot_key for event in coalesced)
    for attempt in attempt_rows:
        idx = attempt.attempt_index
        presign_keys.extend(
            [
                attempt.trace_object_key or run_attempt_trace_key(run_id, idx),
                attempt.video_object_key or run_attempt_video_key(run_id, idx),
                attempt.final_screenshot_object_key or run_attempt_screenshot_key(run_id, idx),
                attempt.dom_snapshot_object_key or run_attempt_dom_key(run_id, idx),
            ]
        )
    url_cache = await _presign_map(storage, presign_keys)

    timeline: list[dict[str, Any]] = []
    for event in state_events:
        timeline.append(
            {
                "seq": int(event.seq),
                "ts": event.ts.isoformat(),
                "status": (event.payload or {}).get("status"),
                "step": (event.payload or {}).get("step"),
                "screenshot_key": event.screenshot_key,
                "screenshot_url": _cached_url(url_cache, event.screenshot_key),
            }
        )

    artifacts: list[dict[str, Any]] = []
    for attempt in attempt_rows:
        idx = attempt.attempt_index
        trace_key = attempt.trace_object_key or run_attempt_trace_key(run_id, idx)
        video_key = attempt.video_object_key or run_attempt_video_key(run_id, idx)
        screenshot_key = attempt.final_screenshot_object_key or run_attempt_screenshot_key(
            run_id, idx
        )
        dom_key = attempt.dom_snapshot_object_key or run_attempt_dom_key(run_id, idx)
        artifacts.append(
            {
                "attempt_index": idx,
                "trace_url": _cached_url(url_cache, trace_key),
                "video_url": _cached_url(url_cache, video_key),
                "screenshot_url": _cached_url(url_cache, screenshot_key),
                "dom_url": _cached_url(url_cache, dom_key),
            }
        )

    serialized_events: list[dict[str, Any]] = []
    for event in coalesced:
        serialized_events.append(
            _event_to_dict(event, _cached_url(url_cache, event.screenshot_key))
        )

    checkpoint_data = run.checkpoint_data or {}
    generate_letter = checkpoint_data.get("generate_cover_letter")
    run_options = {
        "generate_cover_letter": (bool(generate_letter) if generate_letter is not None else None),
    }

    return {
        "run_id": str(run.id),
        "job_target_id": str(run.job_target_id),
        "company": job.company,
        "role": job.role,
        "status": run.status.value,
        "current_step": run.current_step.value if run.current_step else None,
        "attempt_count": run.attempt_count,
        "latest_screenshot_url": _cached_url(url_cache, latest_screenshot_key),
        "latest_screenshot_key": latest_screenshot_key,
        "open_checkpoint": open_checkpoint,
        "run_options": run_options,
        "timeline": timeline,
        "artifacts": artifacts,
        "last_event_seq": await events_repo.max_seq(run_id),
        "events": serialized_events,
    }


async def patch_run_options(
    session: AsyncSession,
    run_id: uuid.UUID,
    tenant_id: uuid.UUID,
    *,
    generate_cover_letter: bool | None,
) -> dict[str, Any]:
    runs = ApplicationRunRepository(session, tenant_id)
    run = await runs.get(run_id)
    if run is None:
        msg = "Run not found"
        raise ValueError(msg)
    checkpoint = dict(run.checkpoint_data or {})
    if generate_cover_letter is None:
        checkpoint.pop("generate_cover_letter", None)
    else:
        checkpoint["generate_cover_letter"] = generate_cover_letter
    run.checkpoint_data = checkpoint or None
    await session.flush()
    return {
        "generate_cover_letter": checkpoint.get("generate_cover_letter"),
    }


async def stream_run_events(
    session_factory: Any,
    run_id: uuid.UUID,
    *,
    after_seq: int = 0,
    poll_once: bool = False,
) -> AsyncIterator[str]:
    storage = ObjectStorage()
    last_seq = after_seq
    last_screenshot_emit = 0.0
    last_heartbeat = 0.0
    loop = asyncio.get_event_loop()
    yield f"retry: {_SSE_RETRY_MS}\n\n"

    while True:
        async with session_factory() as session:
            repo = RunEventRepository(session)
            events = await repo.list_since(run_id, after_seq=last_seq, limit=200)
        coalesced = _coalesce_screenshot_events(events)
        screenshot_keys = [event.screenshot_key for event in coalesced]
        url_cache = await _presign_map(storage, screenshot_keys)
        emitted = 0
        for event in coalesced:
            if emitted >= _SSE_MAX_EVENTS_PER_POLL:
                break
            if event.event_type == RunEventType.BROWSER_SCREENSHOT.value:
                now = loop.time()
                if now - last_screenshot_emit < _SCREENSHOT_THROTTLE_SEC:
                    last_seq = int(event.seq)
                    continue
                last_screenshot_emit = now
            payload = _event_to_dict(event, _cached_url(url_cache, event.screenshot_key))
            last_seq = int(event.seq)
            emitted += 1
            yield f"id: {last_seq}\nevent: {event.event_type}\ndata: {json.dumps(payload)}\n\n"
        if poll_once:
            return
        now = loop.time()
        if not coalesced and now - last_heartbeat >= _SSE_HEARTBEAT_SEC:
            yield ": heartbeat\n\n"
            last_heartbeat = now
        await asyncio.sleep(0.5)


async def resolve_checkpoint(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID | None = None,
    run_id: uuid.UUID,
    checkpoint_id: uuid.UUID,
    action: str,
    value: str | None = None,
    fixture_html: str | None = None,
) -> dict[str, Any]:
    run_row = await ApplicationRunRepository(session, tenant_id).get(run_id)
    if run_row is None:
        msg = "Run not found"
        raise ValueError(msg)
    stmt = select(HumanCheckpoint).where(
        HumanCheckpoint.id == checkpoint_id,
        HumanCheckpoint.run_id == run_id,
    )
    checkpoint = (await session.execute(stmt)).scalar_one_or_none()
    if checkpoint is None:
        msg = "Checkpoint not found"
        raise ValueError(msg)
    if checkpoint.status != CheckpointStatus.OPEN:
        msg = "Checkpoint already resolved"
        raise ValueError(msg)

    action_norm = action.casefold()
    runs = ApplicationRunRepository(session)

    if checkpoint.checkpoint_type == CheckpointType.REVIEW_SUBMIT:
        if action_norm == "approve":
            result = await submit_application(
                session,
                run_id=run_id,
                fixture_html=fixture_html,
                human_approved=True,
            )
            await append_run_event(
                session,
                run_id=run_id,
                event_type=RunEventType.HUMAN_REQUIRED,
                message="Checkpoint approved — submitting application",
                payload={"checkpoint_id": str(checkpoint_id), "action": "approve"},
            )
            await session.commit()
            return {
                "checkpoint_id": str(checkpoint_id),
                "status": CheckpointStatus.RESOLVED.value,
                "run_status": result.get("run_status", RunStatus.VERIFY_SUBMISSION.value),
                "action": "approve",
            }
        if action_norm == "skip":
            result = await skip_submit(session, run_id=run_id)
            await append_run_event(
                session,
                run_id=run_id,
                event_type=RunEventType.HUMAN_REQUIRED,
                message="Checkpoint skipped by operator",
                payload={"checkpoint_id": str(checkpoint_id), "action": "skip"},
            )
            await session.commit()
            return {
                "checkpoint_id": str(checkpoint_id),
                "status": CheckpointStatus.DISMISSED.value,
                "run_status": result.get("status", RunStatus.SKIPPED.value),
                "action": "skip",
            }
        if action_norm == "deny":
            checkpoint.status = CheckpointStatus.DISMISSED
            await runs.update_fields(run_id, status=RunStatus.NEEDS_HUMAN)
            await append_run_event(
                session,
                run_id=run_id,
                event_type=RunEventType.HUMAN_REQUIRED,
                message="Checkpoint denied — needs human review",
                payload={"checkpoint_id": str(checkpoint_id), "action": "deny"},
            )
            await session.commit()
            return {
                "checkpoint_id": str(checkpoint_id),
                "status": CheckpointStatus.DISMISSED.value,
                "run_status": RunStatus.NEEDS_HUMAN.value,
                "action": "deny",
            }
        if action_norm == "edit":
            await append_run_event(
                session,
                run_id=run_id,
                event_type=RunEventType.HUMAN_REQUIRED,
                message="Operator chose to edit fields before submit",
                payload={"checkpoint_id": str(checkpoint_id), "action": "edit", "value": value},
            )
            await session.commit()
            return {
                "checkpoint_id": str(checkpoint_id),
                "status": CheckpointStatus.OPEN.value,
                "run_status": RunStatus.REVIEW_AND_SUBMIT.value,
                "action": "edit",
            }
        msg = f"Unsupported action: {action}"
        raise ValueError(msg)

    # Generic gate checkpoints (captcha, login, sensitive, etc.)
    if action_norm == "approve":
        checkpoint.status = CheckpointStatus.RESOLVED
        checkpoint.resolved_value = scrub_event_message(str(value)) if value is not None else None
        await runs.update_fields(run_id, status=RunStatus.FILL_FORM)
        await append_run_event(
            session,
            run_id=run_id,
            event_type=RunEventType.STATE_CHANGED,
            message="Human gate cleared — resuming run",
            payload={"checkpoint_type": checkpoint.checkpoint_type.value, "action": "approve"},
        )
        await session.commit()
        return {
            "checkpoint_id": str(checkpoint_id),
            "status": CheckpointStatus.RESOLVED.value,
            "run_status": RunStatus.FILL_FORM.value,
            "action": "approve",
        }
    if action_norm in ("deny", "skip"):
        checkpoint.status = CheckpointStatus.DISMISSED
        await runs.update_fields(run_id, status=RunStatus.SKIPPED)
        await session.commit()
        return {
            "checkpoint_id": str(checkpoint_id),
            "status": CheckpointStatus.DISMISSED.value,
            "run_status": RunStatus.SKIPPED.value,
            "action": action_norm,
        }
    msg = f"Unsupported action: {action}"
    raise ValueError(msg)


async def artifact_url_for_key(session: AsyncSession, key: str) -> str:
    del session
    storage = ObjectStorage()
    url = await storage.presigned_get(key)
    return url


async def get_recent_events(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID | None = None,
    limit: int = 25,
) -> list[dict[str, Any]]:
    stmt = (
        select(RunEvent, JobTarget.company, JobTarget.role)
        .join(ApplicationRun, RunEvent.run_id == ApplicationRun.id)
        .join(JobTarget, ApplicationRun.job_target_id == JobTarget.id)
        .order_by(RunEvent.ts.desc())
        .limit(limit)
    )
    if tenant_id is not None:
        stmt = stmt.where(ApplicationRun.tenant_id == tenant_id)
    rows = (await session.execute(stmt)).all()
    items: list[dict[str, Any]] = []
    for event, company, role in reversed(rows):
        items.append(
            {
                "id": str(event.id),
                "seq": int(event.seq),
                "ts": event.ts.isoformat(),
                "level": event.level,
                "event_type": event.event_type,
                "message": event.message,
                "run_id": str(event.run_id),
                "company": company,
                "role": role,
            }
        )
    return items
