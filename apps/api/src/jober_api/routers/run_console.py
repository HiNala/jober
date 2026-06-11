from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from jober_schemas.run_console import (
    CheckpointResolveRead,
    CheckpointResolveRequest,
    RunConsoleSnapshotRead,
    RunOptionsPatchRequest,
)
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.auth.enforcement import RBACRouter
from jober_api.auth.middleware import require_auth
from jober_api.auth.permissions import Permission
from jober_api.db.session import async_session_factory, get_session
from jober_api.errors import CODE_CHECKPOINT_ALREADY_RESOLVED, error_detail
from jober_api.privacy.browser_state import save_run_storage_state
from jober_api.repositories.application_run import ApplicationRunRepository
from jober_api.services.console.service import (
    get_console_snapshot,
    get_recent_events,
    patch_run_options,
    resolve_checkpoint,
    stream_run_events,
)

router = RBACRouter(permission=Permission.AUTHENTICATED, tags=["run-console"])


@router.get("/console/recent-events")
async def recent_run_events(
    request: Request,
    session: AsyncSession = Depends(get_session),
    limit: int = 25,
) -> dict[str, object]:
    auth = require_auth(request)
    events = await get_recent_events(session, tenant_id=auth.tenant_id, limit=min(limit, 100))
    return {"items": events}


@router.get("/application-runs/{run_id}/console", response_model=RunConsoleSnapshotRead)
async def run_console_snapshot(
    run_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    auth = require_auth(request)
    try:
        return await get_console_snapshot(session, run_id, auth.tenant_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/application-runs/{run_id}/events")
async def run_events_sse(run_id: uuid.UUID, request: Request) -> StreamingResponse:
    auth = require_auth(request)
    last_event_id = request.headers.get("Last-Event-ID") or request.query_params.get("after_seq")
    after_seq = int(last_event_id) if last_event_id and str(last_event_id).isdigit() else 0
    poll_once = request.query_params.get("poll_once") == "1"

    async def _generator() -> AsyncIterator[str]:
        async with async_session_factory() as session:
            run = await ApplicationRunRepository(session, auth.tenant_id).get(run_id)
            if run is None:
                yield 'event: error\ndata: {"detail":"Run not found"}\n\n'
                return
        async for chunk in stream_run_events(
            async_session_factory,
            run_id,
            after_seq=after_seq,
            poll_once=poll_once,
        ):
            yield chunk

    return StreamingResponse(
        _generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/runs/{run_id}/events")
async def run_events_sse_alias(run_id: uuid.UUID, request: Request) -> StreamingResponse:
    """Alias for Mission 11 docs — forwards to application-runs SSE."""
    return await run_events_sse(run_id, request)


@router.post(
    "/application-runs/{run_id}/checkpoints/{checkpoint_id}/resolve",
    response_model=CheckpointResolveRead,
)
async def resolve_run_checkpoint(
    run_id: uuid.UUID,
    checkpoint_id: uuid.UUID,
    request: Request,
    body: CheckpointResolveRequest,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    auth = require_auth(request)
    payload = body.model_dump()
    try:
        result = await resolve_checkpoint(
            session,
            tenant_id=auth.tenant_id,
            run_id=run_id,
            checkpoint_id=checkpoint_id,
            action=str(payload["action"]),
            value=payload.get("value"),
            fixture_html=None,
        )
        return result
    except ValueError as exc:
        message = str(exc)
        if message == "Checkpoint already resolved":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error_detail(message, code=CODE_CHECKPOINT_ALREADY_RESOLVED),
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=message,
        ) from exc


class BrowserStorageStateRequest(BaseModel):
    """Playwright storage state after human login — encrypted at rest, never plaintext in DB."""

    state: dict[str, Any] = Field(..., description="Playwright context.storage_state() JSON")


@router.patch("/application-runs/{run_id}/run-options")
async def update_run_options(
    run_id: uuid.UUID,
    request: Request,
    body: RunOptionsPatchRequest,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    auth = require_auth(request)
    try:
        result = await patch_run_options(
            session,
            run_id,
            auth.tenant_id,
            generate_cover_letter=body.generate_cover_letter,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    await session.commit()
    return result


@router.put("/application-runs/{run_id}/browser-storage-state")
async def save_browser_storage_state(
    run_id: uuid.UUID,
    request: Request,
    body: BrowserStorageStateRequest,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    auth = require_auth(request)
    run = await ApplicationRunRepository(session, auth.tenant_id).get(run_id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    key = await save_run_storage_state(run_id, body.state)
    return {"storage_key": key, "status": "saved"}
