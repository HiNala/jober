from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from jober_schemas.recovery import FailureAnalyticsRead, FailureReportRead
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.db.session import get_session
from jober_api.services.recovery.service import (
    get_failure_analytics,
    get_failure_report,
    recovery_fill_from_fixture,
    resume_from_checkpoint,
)

router = APIRouter(tags=["recovery"])


@router.post("/job-targets/{job_target_id}/recovery-fill")
async def recovery_fill(
    job_target_id: uuid.UUID,
    body: dict[str, object] | None = None,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    payload = body or {}
    fixture_html = payload.get("fixture_html")
    if not fixture_html:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="fixture_html is required",
        )
    try:
        result = await recovery_fill_from_fixture(
            session,
            job_target_id=job_target_id,
            fixture_html=str(fixture_html),
            platform=str(payload.get("platform") or "greenhouse"),
            force_brittle=bool(payload.get("force_brittle")),
            simulate_failure_class=(
                str(payload["simulate_failure_class"])
                if payload.get("simulate_failure_class")
                else None
            ),
        )
        await session.commit()
        return result
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get("/job-targets/{job_target_id}/failure-report", response_model=FailureReportRead)
async def failure_report_for_job(
    job_target_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    from jober_api.services.recovery.service import get_failure_report_for_job

    result = await get_failure_report_for_job(session, job_target_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No failure report")
    return result


@router.get("/application-runs/{run_id}/failure-report", response_model=FailureReportRead)
async def failure_report(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    try:
        return await get_failure_report(session, run_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/application-runs/{run_id}/resume")
async def resume_run(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    try:
        result = await resume_from_checkpoint(session, run_id)
        await session.commit()
        return result
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get("/recovery/failure-analytics", response_model=FailureAnalyticsRead)
async def failure_analytics(
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    return await get_failure_analytics(session)
