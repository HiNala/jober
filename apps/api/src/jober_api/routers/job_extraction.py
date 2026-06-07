from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.db.session import get_session
from jober_api.services.job_extraction.service import (
    ExtractionBlockedError,
    enqueue_browser_extraction,
    extract_from_fixture_html,
    get_cached_extraction,
)

router = APIRouter(prefix="/job-targets", tags=["job-extraction"])


@router.get("/{job_target_id}/job-profile")
async def get_job_profile(
    job_target_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    cached = await get_cached_extraction(session, job_target_id)
    if cached is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No extracted profile")
    return dict(cached.model_dump())


@router.post("/{job_target_id}/extract")
async def extract_job_profile(
    job_target_id: uuid.UUID,
    body: dict[str, object] | None = None,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    payload = body or {}
    force = bool(payload.get("force", False))
    fixture_html = payload.get("fixture_html")
    fixture_url = str(payload.get("fixture_url") or "https://example.com/job")

    try:
        if fixture_html:
            result = await extract_from_fixture_html(
                session,
                job_target_id=job_target_id,
                url=fixture_url,
                html=str(fixture_html),
                force=force,
            )
            await session.commit()
            return dict(result.model_dump())

        queued = await enqueue_browser_extraction(
            session,
            job_target_id=job_target_id,
            force=force,
        )
        await session.commit()
        return queued
    except ExtractionBlockedError as exc:
        await session.commit()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Human checkpoint required",
                "gate": exc.gate.value,
                "run_id": str(exc.run_id),
            },
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
