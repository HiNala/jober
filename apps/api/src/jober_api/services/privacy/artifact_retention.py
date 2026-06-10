from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.config import settings
from jober_api.models.enums import RunStatus
from jober_api.models.tenant import Tenant
from jober_api.services.privacy.retention import cleanup_runs

_TERMINAL_STATUSES = (
    RunStatus.SUCCEEDED,
    RunStatus.FAILED_FINAL,
    RunStatus.SKIPPED,
)


async def purge_stale_run_artifacts(session: AsyncSession) -> dict[str, Any]:
    """Remove terminal runs older than tenant retention (or platform default)."""
    tenants = list((await session.execute(select(Tenant))).scalars())
    purged_runs = 0
    removed_objects = 0
    for tenant in tenants:
        days = tenant.retention_days or settings.run_artifact_retention_days
        before = datetime.now(UTC) - timedelta(days=days)
        for status in _TERMINAL_STATUSES:
            result = await cleanup_runs(
                session,
                tenant_id=tenant.id,
                before=before,
                run_status=status,
            )
            purged_runs += int(result["purged_runs"])
            removed_objects += int(result["removed_objects"])
    return {
        "purged_runs": purged_runs,
        "removed_objects": removed_objects,
        "default_retention_days": settings.run_artifact_retention_days,
    }
