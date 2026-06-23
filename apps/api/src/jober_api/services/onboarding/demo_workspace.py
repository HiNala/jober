from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.enums import AuditAction
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.repositories.user_profile import UserProfileRepository
from jober_api.services.audit.service import record_audit
from jober_api.services.onboarding.demo_data import DEMO_JOBS, DEMO_PROFILE


class DemoWorkspaceError(Exception):
    def __init__(self, message: str, *, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


async def seed_demo_workspace(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
) -> dict[str, int]:
    jobs = JobTargetRepository(session, tenant_id)
    existing = await jobs.list_filtered(limit=1)
    if existing:
        raise DemoWorkspaceError(
            "Workspace already has jobs — import or clear your queue before loading demo data.",
            status_code=409,
        )

    profiles = UserProfileRepository(session, tenant_id)
    profile = await profiles.get_or_create_for_tenant()
    await profiles.update_fields(profile, **DEMO_PROFILE)

    created = 0
    for row in DEMO_JOBS:
        await jobs.create(tenant_id=tenant_id, **row)
        created += 1

    await record_audit(
        session,
        tenant_id=tenant_id,
        user_id=user_id,
        action=AuditAction.POLICY_UPDATE,
        message="Demo workspace loaded",
        details={"jobs_created": created},
    )
    await session.commit()
    return {"jobs_created": created, "profile_seeded": 1}
