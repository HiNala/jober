from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.application_attempt import ApplicationAttempt
from jober_api.models.application_run import ApplicationRun
from jober_api.models.form_field_observation import FormFieldObservation
from jober_api.models.job_target import JobTarget
from jober_api.repositories.application_run import ApplicationRunRepository
from jober_api.repositories.job_target import JobTargetRepository


async def require_job_for_tenant(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    job_target_id: uuid.UUID,
) -> JobTarget:
    job = await JobTargetRepository(session, tenant_id).get(job_target_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job target not found")
    return job


async def require_run_for_tenant(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    run_id: uuid.UUID,
) -> ApplicationRun:
    run = await ApplicationRunRepository(session, tenant_id).get(run_id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return run


async def require_observation_for_tenant(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    observation_id: uuid.UUID,
) -> FormFieldObservation:
    observation = await session.get(FormFieldObservation, observation_id)
    if observation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Observation not found")
    attempt = await session.get(ApplicationAttempt, observation.attempt_id)
    if attempt is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Observation not found")
    await require_run_for_tenant(session, tenant_id, attempt.run_id)
    return observation
