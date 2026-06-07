from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.application_run import ApplicationRun
from jober_api.models.enums import JobTargetStatus, RunStatus
from jober_api.models.job_target import JobTarget
from jober_api.models.user_profile import UserProfile
from jober_api.privacy.browser_state import delete_run_storage_state
from jober_api.repositories.application_run import ApplicationRunRepository
from jober_api.storage.keys import run_prefix
from jober_api.storage.minio_client import ObjectStorage

_DELETE_CONFIRM_PHRASE = "DELETE ALL MY DATA"


async def purge_run(
    session: AsyncSession,
    run_id: uuid.UUID,
    *,
    commit: bool = True,
) -> dict[str, Any]:
    runs = ApplicationRunRepository(session)
    run = await runs.get(run_id)
    if run is None:
        msg = "Run not found"
        raise ValueError(msg)
    storage = ObjectStorage()
    removed_objects = await storage.remove_prefix(run_prefix(run_id))
    await delete_run_storage_state(run_id)
    await session.delete(run)
    if commit:
        await session.commit()
    return {"run_id": str(run_id), "removed_objects": removed_objects, "status": "purged"}


async def cleanup_runs(
    session: AsyncSession,
    *,
    before: datetime | None = None,
    run_status: RunStatus | None = None,
    job_status: JobTargetStatus | None = None,
) -> dict[str, Any]:
    stmt = select(ApplicationRun).join(JobTarget)
    if before is not None:
        stmt = stmt.where(ApplicationRun.created_at < before)
    if run_status is not None:
        stmt = stmt.where(ApplicationRun.status == run_status)
    if job_status is not None:
        stmt = stmt.where(JobTarget.status == job_status)
    runs = list((await session.execute(stmt)).scalars())
    purged = 0
    removed_objects = 0
    for run in runs:
        result = await purge_run(session, run.id, commit=False)
        purged += 1
        removed_objects += int(result["removed_objects"])
    await session.commit()
    return {
        "purged_runs": purged,
        "removed_objects": removed_objects,
        "filters": {
            "before": before.isoformat() if before else None,
            "run_status": run_status.value if run_status else None,
            "job_status": job_status.value if job_status else None,
        },
    }


async def export_all_data(session: AsyncSession) -> dict[str, Any]:
    profiles = list((await session.execute(select(UserProfile))).scalars())
    all_jobs = list((await session.execute(select(JobTarget))).scalars())
    runs = list((await session.execute(select(ApplicationRun))).scalars())
    return {
        "exported_at": datetime.now(UTC).isoformat(),
        "profiles": [
            {
                "id": str(p.id),
                "name": p.name,
                "email": p.email,
                "field_consent": p.field_consent,
                "has_sensitive_vault": bool(p.sensitive_eeo_answers),
            }
            for p in profiles
        ],
        "job_targets": [
            {
                "id": str(j.id),
                "company": j.company,
                "role": j.role,
                "status": j.status.value,
                "priority": j.priority,
            }
            for j in all_jobs
        ],
        "application_runs": [
            {
                "id": str(r.id),
                "job_target_id": str(r.job_target_id),
                "status": r.status.value,
                "policy": r.policy.value,
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
            }
            for r in runs
        ],
    }


async def delete_all_data(session: AsyncSession, *, confirm: str) -> dict[str, Any]:
    if confirm.strip() != _DELETE_CONFIRM_PHRASE:
        msg = f"Confirmation phrase must be exactly: {_DELETE_CONFIRM_PHRASE}"
        raise ValueError(msg)
    storage = ObjectStorage()
    removed_objects = 0
    for prefix in ("runs/", "resumes/", "documents/"):
        removed_objects += await storage.remove_prefix(prefix)
    await session.execute(delete(ApplicationRun))
    await session.execute(delete(JobTarget))
    await session.execute(delete(UserProfile))
    await session.commit()
    return {
        "status": "deleted",
        "removed_objects": removed_objects,
        "deleted_at": datetime.now(UTC).isoformat(),
    }
