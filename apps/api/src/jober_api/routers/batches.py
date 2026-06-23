from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.auth.enforcement import RBACRouter, requires
from jober_api.auth.middleware import require_auth
from jober_api.auth.permissions import Permission
from jober_api.config import settings
from jober_api.db.session import get_session
from jober_api.errors import budget_exceeded_http
from jober_api.repositories.application_run import ApplicationRunRepository
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

router = RBACRouter(permission=Permission.AUTHENTICATED, tags=["batches"])


@router.get("/dashboard/summary")
async def get_dashboard_summary(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    auth = require_auth(request)
    return await dashboard_summary(session, auth.tenant_id)


@router.post("/batches/preview")
async def post_batch_preview(
    request: Request,
    body: dict[str, Any],
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    auth = require_auth(request)
    filters = body.get("filters") or {}
    return await preview_batch(session, filters, auth.tenant_id)


@router.post("/batches")
async def post_create_batch(
    request: Request,
    body: dict[str, Any],
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    auth = require_auth(request)
    try:
        scheduled_raw = body.get("scheduled_at")
        scheduled_at = datetime.fromisoformat(str(scheduled_raw)) if scheduled_raw else None
        batch = await create_batch(
            session,
            tenant_id=auth.tenant_id,
            plan=auth.plan,
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
        return await serialize_batch(session, batch.id, auth.tenant_id)
    except BatchValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@router.get("/batches/daily-plan")
async def get_daily_plan(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    auth = require_auth(request)
    return await generate_daily_plan(session, auth.tenant_id)


@router.get("/batches/{batch_id}")
async def get_batch(
    batch_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    auth = require_auth(request)
    try:
        return await serialize_batch(session, batch_id, auth.tenant_id)
    except BatchValidationError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/batches/{batch_id}/enqueue")
async def post_enqueue_batch(
    batch_id: uuid.UUID,
    request: Request,
    body: dict[str, Any] | None = None,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    auth = require_auth(request)
    payload = body or {}
    try:
        run_at_raw = payload.get("run_at")
        run_at = datetime.fromisoformat(str(run_at_raw)) if run_at_raw else None
        result = await enqueue_batch(session, batch_id, tenant_id=auth.tenant_id, run_at=run_at)
        await session.commit()
        return result
    except BatchValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    except BudgetExceededError as exc:
        raise budget_exceeded_http(str(exc) or None) from exc


@router.post("/queue/pause-all")
async def post_pause_all(request: Request) -> dict[str, str]:
    auth = require_auth(request)
    return await pause_all_batches(auth.tenant_id)


@router.post("/queue/resume-all")
async def post_resume_all(request: Request) -> dict[str, str]:
    auth = require_auth(request)
    return await resume_all_batches(auth.tenant_id)


@router.post("/batches/{batch_id}/pause")
async def post_pause_batch(
    batch_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    auth = require_auth(request)
    try:
        await pause_batch(session, batch_id, auth.tenant_id)
    except BatchValidationError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return {"status": "paused", "batch_id": str(batch_id)}


@router.post("/batches/{batch_id}/resume")
async def post_resume_batch(
    batch_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    auth = require_auth(request)
    try:
        await resume_batch(session, batch_id, auth.tenant_id)
    except BatchValidationError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return {"status": "resumed", "batch_id": str(batch_id)}


@router.post("/application-runs/{run_id}/cancel")
async def post_cancel_run(
    run_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    auth = require_auth(request)
    runs_repo = ApplicationRunRepository(session, auth.tenant_id)
    if await runs_repo.get(run_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    await cancel_run(session, run_id)
    await session.commit()
    return {"status": "cancelled", "run_id": str(run_id)}


@router.post("/batch-items/{item_id}/skip")
async def post_skip_batch_item(
    item_id: uuid.UUID,
    request: Request,
    body: dict[str, Any] | None = None,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    auth = require_auth(request)
    reason = (body or {}).get("reason", "skipped_by_user")
    try:
        await skip_batch_item(session, item_id, auth.tenant_id, reason=str(reason))
        await session.commit()
        return {"status": "skipped", "item_id": str(item_id)}
    except BatchValidationError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/batches/{batch_id}/reorder")
async def patch_reorder_batch(
    batch_id: uuid.UUID,
    request: Request,
    body: dict[str, Any],
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    auth = require_auth(request)
    ordered = [uuid.UUID(str(value)) for value in body.get("ordered_item_ids", [])]
    try:
        await reorder_batch_items(session, batch_id, auth.tenant_id, ordered)
    except BatchValidationError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    await session.commit()
    return {"status": "reordered", "batch_id": str(batch_id)}


@router.patch("/queue/concurrency")
@requires(Permission.ADMIN_CONFIG_MANAGE)
async def patch_queue_concurrency(request: Request, body: dict[str, Any]) -> dict[str, Any]:
    require_auth(request)
    value = int(body.get("max_concurrency", settings.batch_max_concurrency))
    redis_control.set_max_concurrency(value)
    return {"max_concurrency": value}
