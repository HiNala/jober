from __future__ import annotations

import uuid
from typing import Any

from fastapi import Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.auth.enforcement import RBACRouter
from jober_api.auth.middleware import require_auth
from jober_api.auth.permissions import Permission
from jober_api.db.session import get_session
from jober_api.services.discovery import service as discovery_service

router = RBACRouter(permission=Permission.AUTHENTICATED, prefix="/discovery", tags=["discovery"])


class DiscoverySearchBody(BaseModel):
    role: str | None = None
    stack: list[str] = Field(default_factory=list)
    location: str | None = None
    stage: str | None = None
    work_style: str | None = None
    board_urls: list[str] = Field(default_factory=list)
    list_id: str | None = None


class AcceptCandidatesBody(BaseModel):
    list_id: str
    candidates: list[dict[str, Any]]
    priority: str | None = None
    fit_lane: str | None = None


class SavedSearchBody(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    query: dict[str, Any] = Field(default_factory=dict)


class LinkSavedSearchBody(BaseModel):
    saved_search_id: str | None = None


@router.post("/search")
async def discovery_search(
    request: Request,
    body: DiscoverySearchBody,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    auth = require_auth(request)
    candidates = await discovery_service.search_candidates(
        session,
        tenant_id=auth.tenant_id,
        query=body.model_dump(),
    )
    return {"candidates": candidates}


@router.post("/accept")
async def discovery_accept(
    request: Request,
    body: AcceptCandidatesBody,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    auth = require_auth(request)
    try:
        list_id = uuid.UUID(body.list_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid list_id",
        ) from exc
    try:
        result = await discovery_service.accept_candidates(
            session,
            tenant_id=auth.tenant_id,
            user_id=auth.user_id,
            list_id=list_id,
            candidates=body.candidates,
            priority=body.priority,
            fit_lane=body.fit_lane,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    await session.commit()
    return result


@router.post("/lists/{list_id}/refresh")
async def discovery_refresh_list(
    list_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    auth = require_auth(request)
    try:
        candidates = await discovery_service.refresh_list_candidates(
            session,
            tenant_id=auth.tenant_id,
            user_id=auth.user_id,
            list_id=list_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return {"candidates": candidates}


@router.post("/lists/{list_id}/attach-import")
async def discovery_attach_import(
    list_id: uuid.UUID,
    request: Request,
    import_id: str = Query(..., min_length=1),
    session: AsyncSession = Depends(get_session),
) -> dict[str, int]:
    auth = require_auth(request)
    try:
        result = await discovery_service.attach_import_to_list(
            session,
            tenant_id=auth.tenant_id,
            user_id=auth.user_id,
            list_id=list_id,
            import_id=import_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    await session.commit()
    return result


@router.get("/saved-searches")
async def list_saved_searches(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    auth = require_auth(request)
    items = await discovery_service.list_saved_searches(
        session,
        tenant_id=auth.tenant_id,
        user_id=auth.user_id,
    )
    return {"items": items}


@router.post("/saved-searches")
async def create_saved_search(
    request: Request,
    body: SavedSearchBody,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    auth = require_auth(request)
    row = await discovery_service.create_saved_search(
        session,
        tenant_id=auth.tenant_id,
        user_id=auth.user_id,
        name=body.name,
        query=body.query,
    )
    await session.commit()
    return row


@router.patch("/lists/{list_id}/saved-search")
async def link_list_saved_search(
    list_id: uuid.UUID,
    request: Request,
    body: LinkSavedSearchBody,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    auth = require_auth(request)
    saved_id = uuid.UUID(body.saved_search_id) if body.saved_search_id else None
    try:
        await discovery_service.link_list_to_saved_search(
            session,
            tenant_id=auth.tenant_id,
            user_id=auth.user_id,
            list_id=list_id,
            saved_search_id=saved_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    await session.commit()
    return {"status": "linked"}
