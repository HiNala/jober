from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.auth.middleware import require_auth
from jober_api.db.session import get_session
from jober_api.services.library import service as library_service

router = APIRouter(prefix="/library", tags=["library"])


@router.get("/resumes")
async def library_resumes(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    auth = require_auth(request)
    items = await library_service.list_resumes(session, auth.tenant_id)
    return {"items": items}


@router.get("/cover-letters")
async def library_cover_letters(
    request: Request,
    q: str | None = None,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    auth = require_auth(request)
    items = await library_service.list_cover_letters(session, auth.tenant_id, query=q)
    return {"items": items}


@router.get("/runs")
async def library_runs(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    auth = require_auth(request)
    items = await library_service.list_runs(session, auth.tenant_id)
    return {"items": items}


@router.get("/search")
async def library_search(
    request: Request,
    q: str = Query(..., min_length=1, max_length=200),
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    auth = require_auth(request)
    return await library_service.search_library(
        session,
        auth.tenant_id,
        auth.user_id,
        q,
    )
