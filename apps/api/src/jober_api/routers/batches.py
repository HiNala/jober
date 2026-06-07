from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.config import settings
from jober_api.db.session import get_session
from jober_api.services.batch import redis_control
from jober_api.services.batch.daily_plan import generate_daily_plan
from jober_api.services.batch.service import (
    BatchValidationError,
    cancel_run,
    create_batch,
    dashboard_summary,
    enqueue_batch,
    pause_all_batches,
    pause_batch,
    preview_batch,
    reorder_batch_items,
    resume_all_batches,
    resume_batch,
    serialize_batch,
    skip_batch_item,
)
from jober_api.services.llm.gateway import BudgetExceededError

router = APIRouter(tags=["batches"])


@router.get("/dashboard/summary")
async def get_dashboard_summary(session: AsyncSession = Depends(get_session)) -> dict[str, Any]:
    return await dashboard_summary(session)


@router.post("/batches/preview")
async def post_batch_preview(
    body: dict[str, Any],
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    filters = body.get("filters") or {}
    return await preview_batch(session, filters)


@router.post("/batches")
async def post_create_batch(
    body: dict[str, Any],
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    try:
        scheduled_raw = body.get("scheduled_at")
        scheduled_at = datetime.fromisoformat(str(scheduled_raw)) if scheduled_raw else None
        batch = await create_batch(
            session,
            name=str(body.get("name") or "Batch"),
            policy=str(body.get("policy") or "review_before_submit"),
            filters=body.get("filters") or {},
            scheduled_at=scheduled_at,
            max_concurrency=int(body["max_concurrency"]) if body.get("max_concurrency") else None,
            site_cooldown_seconds=float(body["site_cooldown_seconds"])
            if body.get("site_cooldown_seconds")
            else None,
        )
        await session.commit()
        return await serialize_batch(session, batch.id)
    except BatchValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@router.get("/batches/daily-plan")
async def get_daily_plan(session: AsyncSession = Depends(get_session)) -> dict[str, Any]:
    return await generate_daily_plan(session)


@router.get("/batches/{batch_id}")
async def get_batch(
    batch_id: uuid.UUID, session: AsyncSession = Depends(get_session)
) -> dict[str, Any]:
    try:
        return await serialize_batch(session, batch_id)
    except BatchValidationError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/batches/{batch_id}/enqueue")
async def post_enqueue_batch(
    batch_id: uuid.UUID,
    body: dict[str, Any] | None = None,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    payload = body or {}
    try:
        run_at_raw = payload.get("run_at")
        run_at = datetime.fromisoformat(str(run_at_raw)) if run_at_raw else None
        result = await enqueue_batch(session, batch_id, run_at=run_at)
        await session.commit()
        return result
    except BatchValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    except BudgetExceededError as exc:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=str(exc)) from exc


@router.post("/queue/pause-all")
async def post_pause_all() -> dict[str, str]:
    return await pause_all_batches()


@router.post("/queue/resume-all")
async def post_resume_all() -> dict[str, str]:
    return await resume_all_batches()


@router.post("/batches/{batch_id}/pause")
async def post_pause_batch(batch_id: uuid.UUID) -> dict[str, str]:
    await pause_batch(batch_id)
    return {"status": "paused", "batch_id": str(batch_id)}


@router.post("/batches/{batch_id}/resume")
async def post_resume_batch(batch_id: uuid.UUID) -> dict[str, str]:
    await resume_batch(batch_id)
    return {"status": "resumed", "batch_id": str(batch_id)}


@router.post("/application-runs/{run_id}/cancel")
async def post_cancel_run(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    await cancel_run(session, run_id)
    await session.commit()
    return {"status": "cancelled", "run_id": str(run_id)}


@router.post("/batch-items/{item_id}/skip")
async def post_skip_batch_item(
    item_id: uuid.UUID,
    body: dict[str, Any] | None = None,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    reason = (body or {}).get("reason", "skipped_by_user")
    try:
        await skip_batch_item(session, item_id, reason=str(reason))
        await session.commit()
        return {"status": "skipped", "item_id": str(item_id)}
    except BatchValidationError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/batches/{batch_id}/reorder")
async def patch_reorder_batch(
    batch_id: uuid.UUID,
    body: dict[str, Any],
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    ordered = [uuid.UUID(str(value)) for value in body.get("ordered_item_ids", [])]
    await reorder_batch_items(session, batch_id, ordered)
    await session.commit()
    return {"status": "reordered", "batch_id": str(batch_id)}


@router.patch("/queue/concurrency")
async def patch_queue_concurrency(body: dict[str, Any]) -> dict[str, Any]:
    value = int(body.get("max_concurrency", settings.batch_max_concurrency))
    redis_control.set_max_concurrency(value)
    return {"max_concurrency": value}
