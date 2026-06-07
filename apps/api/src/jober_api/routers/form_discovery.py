from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.db.session import get_session
from jober_api.models.enums import FieldObservationStatus
from jober_api.services.form_discovery.service import (
    discover_from_fixture_html,
    list_field_observations,
    update_field_observation,
)

router = APIRouter(prefix="/job-targets", tags=["form-discovery"])


@router.post("/{job_target_id}/discover-form")
async def discover_form(
    job_target_id: uuid.UUID,
    body: dict[str, object] | None = None,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    payload = body or {}
    fixture_html = payload.get("fixture_html")
    platform = str(payload.get("platform") or "generic")
    if not fixture_html:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="fixture_html required (browser worker path coming in Mission 08)",
        )
    try:
        result = await discover_from_fixture_html(
            session,
            job_target_id=job_target_id,
            html=str(fixture_html),
            platform=platform,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    await session.commit()
    return dict(result.model_dump())


@router.get("/{job_target_id}/field-observations")
async def get_field_observations(
    job_target_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    items = await list_field_observations(session, job_target_id)
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No field observations")
    return {"items": [item.model_dump() for item in items]}


@router.patch("/field-observations/{observation_id}")
async def patch_field_observation(
    observation_id: uuid.UUID,
    body: dict[str, object],
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    mapped = body.get("mapped_profile_field")
    raw_status = body.get("status")
    remember = bool(body.get("remember", False))
    platform = str(body.get("platform") or "generic")
    status_enum = FieldObservationStatus(str(raw_status)) if raw_status else None
    try:
        result = await update_field_observation(
            session,
            observation_id,
            mapped_profile_field=str(mapped) if mapped is not None else None,
            status=status_enum,
            remember=remember,
            platform=platform,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    await session.commit()
    return dict(result.model_dump())
