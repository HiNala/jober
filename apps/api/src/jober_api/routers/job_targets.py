from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.db.session import get_session
from jober_api.models.enums import JobTargetStatus
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.serializers.job_target import serialize_job_target

router = APIRouter(prefix="/job-targets", tags=["job-targets"])


@router.get("")
async def list_job_targets(
    session: AsyncSession = Depends(get_session),
    status_filter: JobTargetStatus | None = Query(None, alias="status"),
    priority: str | None = None,
    company: str | None = None,
    role: str | None = None,
    location: str | None = None,
    ats_guess: str | None = None,
    limit: int = Query(500, ge=1, le=2000),
    offset: int = Query(0, ge=0),
) -> dict[str, object]:
    repo = JobTargetRepository(session)
    rows = await repo.list_filtered(
        status=status_filter,
        priority=priority,
        company=company,
        role=role,
        location=location,
        limit=limit,
        offset=offset,
    )
    serialized = [serialize_job_target(row) for row in rows]
    if ats_guess:
        serialized = [row for row in serialized if row.get("ats_guess") == ats_guess]
    return {"items": serialized, "total": len(serialized)}


@router.patch("/{job_target_id}")
async def patch_job_target(
    job_target_id: UUID,
    body: dict[str, object],
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    allowed = {"status", "applied_date", "follow_up_date", "notes", "priority"}
    updates = {k: v for k, v in body.items() if k in allowed and v is not None}
    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid fields")

    if "status" in updates and isinstance(updates["status"], str):
        try:
            updates["status"] = JobTargetStatus(updates["status"])
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid status",
            ) from exc

    for date_field in ("applied_date", "follow_up_date"):
        raw_date = updates.get(date_field)
        if isinstance(raw_date, str):
            try:
                updates[date_field] = date.fromisoformat(raw_date)
            except ValueError as exc:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid {date_field}",
                ) from exc

    repo = JobTargetRepository(session)
    updated = await repo.update_fields(job_target_id, **updates)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    await session.commit()
    return serialize_job_target(updated)


@router.get("/{job_target_id}")
async def get_job_target(
    job_target_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    repo = JobTargetRepository(session)
    row = await repo.get(job_target_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return serialize_job_target(row)
