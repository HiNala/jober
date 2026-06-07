from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.audit_log import AuditLogEntry
from jober_api.models.enums import AuditAction


async def record_audit(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID | None,
    action: AuditAction,
    message: str,
    details: dict[str, Any] | None = None,
) -> AuditLogEntry:
    entry = AuditLogEntry(
        tenant_id=tenant_id,
        user_id=user_id,
        action=action,
        message=message,
        details=details,
        ts=datetime.now(UTC),
    )
    session.add(entry)
    await session.flush()
    return entry
