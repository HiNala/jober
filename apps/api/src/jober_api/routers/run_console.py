from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from jober_schemas.run_console import (
    CheckpointResolveRead,
    CheckpointResolveRequest,
    RunConsoleSnapshotRead,
)
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.db.session import async_session_factory, get_session
from jober_api.privacy.browser_state import save_run_storage_state
from jober_api.services.console.service import (
    get_console_snapshot,
    get_recent_events,
    resolve_checkpoint,
    stream_run_events,
)

router = APIRouter(tags=["run-console"])


@router.get("/console/recent-events")
async def recent_run_events(
    session: AsyncSession = Depends(get_session),
    limit: int = 25,
) -> dict[str, object]:
    events = await get_recent_events(session, limit=min(limit, 100))
    return {"items": events}


@router.get("/application-runs/{run_id}/console", response_model=RunConsoleSnapshotRead)
async def run_console_snapshot(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    try:
        return await get_console_snapshot(session, run_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/application-runs/{run_id}/events")
async def run_events_sse(run_id: uuid.UUID, request: Request) -> StreamingResponse:
    last_event_id = request.headers.get("Last-Event-ID") or request.query_params.get("after_seq")
    after_seq = int(last_event_id) if last_event_id and str(last_event_id).isdigit() else 0
    poll_once = request.query_params.get("poll_once") == "1"

    async def _generator() -> AsyncIterator[str]:
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
    body: CheckpointResolveRequest,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    payload = body.model_dump()
    try:
        result = await resolve_checkpoint(
            session,
            run_id=run_id,
            checkpoint_id=checkpoint_id,
            action=str(payload["action"]),
            value=payload.get("value"),
            fixture_html=None,
        )
        return result
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


class BrowserStorageStateRequest(BaseModel):
    """Playwright storage state after human login — encrypted at rest, never plaintext in DB."""

    state: dict[str, Any] = Field(..., description="Playwright context.storage_state() JSON")


@router.put("/application-runs/{run_id}/browser-storage-state")
async def save_browser_storage_state(
    run_id: uuid.UUID,
    body: BrowserStorageStateRequest,
) -> dict[str, str]:
    key = await save_run_storage_state(run_id, body.state)
    return {"storage_key": key, "status": "saved"}
