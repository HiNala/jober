from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.auth.middleware import require_auth
from jober_api.db.session import get_session
from jober_api.models.enums import JobTargetStatus, RunStatus
from jober_api.services.privacy.retention import (
    cleanup_runs,
    delete_all_data,
    export_all_data,
    purge_run,
)

router = APIRouter(prefix="/privacy", tags=["privacy"])


class CleanupRequest(BaseModel):
    before: datetime | None = None
    run_status: RunStatus | None = None
    job_status: JobTargetStatus | None = None


class DeleteAllRequest(BaseModel):
    confirm: str = Field(..., min_length=8)


@router.post("/runs/{run_id}/purge")
async def purge_run_endpoint(
    run_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    auth = require_auth(request)
    try:
        return await purge_run(session, run_id, tenant_id=auth.tenant_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/cleanup")
async def cleanup_endpoint(
    body: CleanupRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    auth = require_auth(request)
    return await cleanup_runs(
        session,
        tenant_id=auth.tenant_id,
        before=body.before,
        run_status=body.run_status,
        job_status=body.job_status,
    )


@router.get("/export-all")
async def export_all_endpoint(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    auth = require_auth(request)
    data = await export_all_data(session, tenant_id=auth.tenant_id, user_id=auth.user_id)
    await session.commit()
    return data


@router.delete("/delete-all")
async def delete_all_endpoint(
    body: DeleteAllRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    auth = require_auth(request)
    try:
        return await delete_all_data(
            session,
            tenant_id=auth.tenant_id,
            user_id=auth.user_id,
            confirm=body.confirm,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
