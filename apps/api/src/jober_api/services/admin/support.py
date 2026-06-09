from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.analytics import AnalyticsDailyCost
from jober_api.models.application_run import ApplicationRun
from jober_api.models.audit_log import AuditLogEntry
from jober_api.models.enum_utils import enum_value
from jober_api.models.enums import AdminAuditAction, AuditAction, RunStatus
from jober_api.models.tenant import Tenant
from jober_api.models.user import User
from jober_api.services.admin.audit import record_admin_audit


async def get_user_operational_view(
    session: AsyncSession,
    *,
    actor_user_id: uuid.UUID,
    target_user_id: uuid.UUID,
) -> dict[str, Any]:
    """Read-only operational metadata for support — no vault or document bodies."""
    user = await session.get(User, target_user_id)
    if user is None:
        raise LookupError("User not found")
    tenant = await session.get(Tenant, user.tenant_id)
    if tenant is None:
        raise LookupError("Tenant not found")

    await record_admin_audit(
        session,
        actor_user_id=actor_user_id,
        target_user_id=user.id,
        action=AdminAuditAction.SUPPORT_VIEW_ACCESSED,
        resource_type="user",
        resource_id=str(user.id),
        message=f"Support view accessed for {user.email}",
    )

    start_30d = datetime.now(UTC).date() - timedelta(days=29)
    run_stmt = (
        select(ApplicationRun.status, func.count())
        .where(
            ApplicationRun.tenant_id == user.tenant_id,
            ApplicationRun.created_at
            >= datetime.combine(start_30d, datetime.min.time(), tzinfo=UTC),
        )
        .group_by(ApplicationRun.status)
    )
    runs_by_status = {
        enum_value(row[0]): int(row[1]) for row in (await session.execute(run_stmt)).all()
    }

    cost_stmt = select(func.coalesce(func.sum(AnalyticsDailyCost.cost_usd), 0.0)).where(
        AnalyticsDailyCost.tenant_id == user.tenant_id,
        AnalyticsDailyCost.day >= start_30d,
    )
    llm_cost_30d = float((await session.execute(cost_stmt)).scalar_one() or 0.0)

    data_requests_stmt = (
        select(AuditLogEntry)
        .where(
            AuditLogEntry.tenant_id == user.tenant_id,
            AuditLogEntry.action.in_([AuditAction.DATA_EXPORT, AuditAction.DATA_DELETE]),
        )
        .order_by(AuditLogEntry.ts.desc())
        .limit(10)
    )
    data_requests = [
        {
            "action": enum_value(row.action),
            "message": row.message,
            "ts": row.ts.isoformat(),
        }
        for row in (await session.execute(data_requests_stmt)).scalars().all()
    ]

    needs_human = runs_by_status.get(RunStatus.NEEDS_HUMAN.value, 0)

    return {
        "user": {
            "id": str(user.id),
            "email": user.email,
            "display_name": user.display_name,
            "role": enum_value(user.role),
            "status": enum_value(user.status),
            "created_at": user.created_at.isoformat(),
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        },
        "tenant": {
            "id": str(tenant.id),
            "name": tenant.name,
            "plan": enum_value(tenant.plan),
        },
        "usage_30d": {
            "runs_by_status": runs_by_status,
            "llm_cost_usd": round(llm_cost_30d, 4),
            "needs_human_runs": needs_human,
        },
        "data_requests": data_requests,
        "privacy_note": (
            "Operational metadata only. Vault, documents, and job content are not included."
        ),
    }
