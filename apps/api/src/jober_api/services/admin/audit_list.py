from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.admin_audit_log import AdminAuditLog
from jober_api.models.audit_log import AuditLogEntry
from jober_api.models.enum_utils import enum_value
from jober_api.models.enums import AuditAction


async def list_admin_audit_log(
    session: AsyncSession,
    *,
    limit: int = 50,
    actor_user_id: uuid.UUID | None = None,
    target_user_id: uuid.UUID | None = None,
    action: str | None = None,
    since: datetime | None = None,
) -> list[dict[str, object]]:
    stmt = select(AdminAuditLog).order_by(AdminAuditLog.created_at.desc()).limit(limit)
    if actor_user_id is not None:
        stmt = stmt.where(AdminAuditLog.actor_user_id == actor_user_id)
    if target_user_id is not None:
        stmt = stmt.where(AdminAuditLog.target_user_id == target_user_id)
    if action:
        stmt = stmt.where(AdminAuditLog.action == action)
    if since is not None:
        stmt = stmt.where(AdminAuditLog.created_at >= since)
    rows = (await session.execute(stmt)).scalars().all()
    return [
        {
            "id": str(row.id),
            "actor_user_id": str(row.actor_user_id),
            "target_user_id": str(row.target_user_id) if row.target_user_id else None,
            "action": enum_value(row.action),
            "resource_type": row.resource_type,
            "resource_id": row.resource_id,
            "message": row.message,
            "created_at": row.created_at.isoformat(),
        }
        for row in rows
    ]


async def list_data_requests(
    session: AsyncSession,
    *,
    limit: int = 50,
) -> list[dict[str, object]]:
    """Privacy export/delete requests across tenants (operational queue)."""
    stmt = (
        select(AuditLogEntry)
        .where(AuditLogEntry.action.in_([AuditAction.DATA_EXPORT, AuditAction.DATA_DELETE]))
        .order_by(AuditLogEntry.ts.desc())
        .limit(limit)
    )
    rows = (await session.execute(stmt)).scalars().all()
    return [
        {
            "id": str(row.id),
            "tenant_id": str(row.tenant_id),
            "user_id": str(row.user_id) if row.user_id else None,
            "action": enum_value(row.action),
            "message": row.message,
            "ts": row.ts.isoformat(),
        }
        for row in rows
    ]
