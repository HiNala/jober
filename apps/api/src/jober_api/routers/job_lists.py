from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.auth.enforcement import RBACRouter
from jober_api.auth.middleware import require_auth
from jober_api.auth.permissions import Permission
from jober_api.auth.tenant_guard import require_job_for_tenant
from jober_api.db.session import get_session
from jober_api.models.job_list import JobList, JobListItem
from jober_api.repositories.job_list import JobListRepository
from jober_api.services.analytics.collector import emit_server_event
from jober_api.services.analytics.rollups import server_session_id
from jober_api.services.library.service import (
    DEFAULT_LIBRARY_LIMIT,
    MAX_LIBRARY_LIMIT,
    serialize_job_list,
)

router = RBACRouter(permission=Permission.AUTHENTICATED, prefix="/job-lists", tags=["job-lists"])


class JobListCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=512)


class JobListUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=512)
    archived: bool | None = None


class JobListItemAdd(BaseModel):
    job_target_id: uuid.UUID


class JobListReorder(BaseModel):
    item_ids: list[uuid.UUID]


@router.get("")
async def list_job_lists(
    request: Request,
    include_archived: bool = False,
    limit: int = Query(DEFAULT_LIBRARY_LIMIT, ge=1, le=MAX_LIBRARY_LIMIT),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    auth = require_auth(request)
    from jober_api.services.library import service as library_service

    items = await library_service.list_job_lists(
        session,
        auth.tenant_id,
        auth.user_id,
        include_archived=include_archived,
        limit=limit,
        offset=offset,
    )
    return {"items": items, "limit": limit, "offset": offset}


@router.post("")
async def create_job_list(
    request: Request,
    body: JobListCreate,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    auth = require_auth(request)
    row = JobList(
        id=uuid.uuid4(),
        tenant_id=auth.tenant_id,
        user_id=auth.user_id,
        name=body.name.strip(),
        description=body.description,
    )
    session.add(row)
    await emit_server_event(
        session,
        name="list.create",
        session_id=server_session_id(user_id=auth.user_id),
        user_id=auth.user_id,
        tenant_id=auth.tenant_id,
        props={"list_id": str(row.id)},
    )
    await session.commit()
    repo = JobListRepository(session, auth.tenant_id)
    loaded = await repo.get(row.id)
    assert loaded is not None
    return serialize_job_list(loaded)


@router.patch("/{list_id}")
async def update_job_list(
    list_id: uuid.UUID,
    request: Request,
    body: JobListUpdate,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    auth = require_auth(request)
    repo = JobListRepository(session, auth.tenant_id)
    row = await repo.get(list_id)
    if row is None or row.user_id != auth.user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    if body.name is not None:
        row.name = body.name.strip()
    if body.description is not None:
        row.description = body.description
    if body.archived is not None:
        row.archived = body.archived
    await session.commit()
    refreshed = await repo.get(list_id)
    assert refreshed is not None
    return serialize_job_list(refreshed)


@router.post("/{list_id}/items")
async def add_job_list_item(
    list_id: uuid.UUID,
    request: Request,
    body: JobListItemAdd,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    auth = require_auth(request)
    await require_job_for_tenant(session, auth.tenant_id, body.job_target_id)
    repo = JobListRepository(session, auth.tenant_id)
    row = await repo.get(list_id)
    if row is None or row.user_id != auth.user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    if any(item.job_target_id == body.job_target_id for item in row.items):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Job already in list")
    sort_order = max((item.sort_order for item in row.items), default=-1) + 1
    session.add(
        JobListItem(
            id=uuid.uuid4(),
            job_list_id=list_id,
            job_target_id=body.job_target_id,
            sort_order=sort_order,
        )
    )
    await session.commit()
    refreshed = await repo.get(list_id)
    assert refreshed is not None
    return serialize_job_list(refreshed)


@router.delete("/{list_id}/items/{item_id}")
async def remove_job_list_item(
    list_id: uuid.UUID,
    item_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    auth = require_auth(request)
    repo = JobListRepository(session, auth.tenant_id)
    row = await repo.get(list_id)
    if row is None or row.user_id != auth.user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    item = next((i for i in row.items if i.id == item_id), None)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    await session.delete(item)
    await session.commit()
    refreshed = await repo.get(list_id)
    assert refreshed is not None
    return serialize_job_list(refreshed)


@router.post("/{list_id}/reorder")
async def reorder_job_list(
    list_id: uuid.UUID,
    request: Request,
    body: JobListReorder,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    auth = require_auth(request)
    repo = JobListRepository(session, auth.tenant_id)
    row = await repo.get(list_id)
    if row is None or row.user_id != auth.user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    by_id = {item.id: item for item in row.items}
    for index, item_id in enumerate(body.item_ids):
        item = by_id.get(item_id)
        if item is not None:
            item.sort_order = index
    await session.commit()
    refreshed = await repo.get(list_id)
    assert refreshed is not None
    return serialize_job_list(refreshed)
