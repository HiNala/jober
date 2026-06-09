from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.enums import AdminAuditAction, UserRole, UserStatus
from jober_api.models.tenant import Tenant
from jober_api.models.user import User
from jober_api.services.admin.audit import record_admin_audit


def _enum_value(value: UserRole | UserStatus | str) -> str:
    if isinstance(value, (UserRole, UserStatus)):
        return value.value
    return str(value)


async def list_users_for_admin(
    session: AsyncSession,
    *,
    limit: int = 50,
    offset: int = 0,
) -> list[dict[str, object]]:
    """Operational user list — email, role, status only (no vault/profile content)."""
    stmt = (
        select(User, Tenant.plan)
        .join(Tenant, User.tenant_id == Tenant.id)
        .order_by(User.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = (await session.execute(stmt)).all()
    return [
        {
            "id": str(user.id),
            "email": user.email,
            "display_name": user.display_name,
            "role": _enum_value(user.role),
            "status": _enum_value(user.status),
            "tenant_id": str(user.tenant_id),
            "plan": plan.value if hasattr(plan, "value") else str(plan),
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        }
        for user, plan in rows
    ]


async def set_user_status(
    session: AsyncSession,
    *,
    actor_user_id: uuid.UUID,
    target_user_id: uuid.UUID,
    status: UserStatus,
) -> User:
    target = await session.get(User, target_user_id)
    if target is None:
        raise LookupError("User not found")

    if target.id == actor_user_id and status == UserStatus.SUSPENDED:
        raise ValueError("Cannot suspend your own account")

    previous = target.status
    target.status = status
    action = (
        AdminAuditAction.USER_SUSPENDED
        if status == UserStatus.SUSPENDED
        else AdminAuditAction.USER_ACTIVATED
    )
    await record_admin_audit(
        session,
        actor_user_id=actor_user_id,
        target_user_id=target.id,
        action=action,
        message=f"User status changed from {_enum_value(previous)} to {_enum_value(status)}",
        details={
            "previous_status": _enum_value(previous),
            "new_status": _enum_value(status),
        },
    )
    await session.flush()
    return target
