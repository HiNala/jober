from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.admin_audit_log import AdminAuditLog
from jober_api.models.enums import AdminAuditAction


async def record_admin_audit(
    session: AsyncSession,
    *,
    actor_user_id: uuid.UUID,
    action: AdminAuditAction,
    message: str,
    target_user_id: uuid.UUID | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> AdminAuditLog:
    entry = AdminAuditLog(
        actor_user_id=actor_user_id,
        target_user_id=target_user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        message=message,
        details=details,
        created_at=datetime.now(UTC),
    )
    session.add(entry)
    await session.flush()
    return entry
