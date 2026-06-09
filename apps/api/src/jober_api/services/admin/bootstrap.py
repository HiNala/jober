from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.config import settings
from jober_api.models.enum_utils import enum_value
from jober_api.models.enums import AdminAuditAction, UserRole
from jober_api.models.user import User
from jober_api.services.admin.audit import record_admin_audit


class BootstrapError(Exception):
    pass


async def bootstrap_first_admin(
    session: AsyncSession,
    *,
    email: str,
    secret: str,
) -> User:
    """Promote a user to admin via one-time env-gated bootstrap (not a public API)."""
    expected = settings.admin_bootstrap_secret.strip()
    if not expected:
        raise BootstrapError("ADMIN_BOOTSTRAP_SECRET is not configured")
    if secret != expected:
        raise BootstrapError("Invalid bootstrap secret")

    admin_count = int(
        (
            await session.execute(
                select(func.count()).select_from(User).where(User.role == UserRole.ADMIN)
            )
        ).scalar_one()
    )
    if admin_count > 0:
        raise BootstrapError("An admin already exists; use admin promotion instead")

    stmt = select(User).where(func.lower(User.email) == email.strip().lower())
    user = (await session.execute(stmt)).scalar_one_or_none()
    if user is None:
        raise BootstrapError(f"No user found for email {email}")

    if user.role == UserRole.ADMIN:
        return user

    user.role = UserRole.ADMIN
    await record_admin_audit(
        session,
        actor_user_id=user.id,
        target_user_id=user.id,
        action=AdminAuditAction.BOOTSTRAP_ADMIN,
        message=f"Bootstrap promoted {email} to admin",
        details={"email": email},
    )
    await session.commit()
    await session.refresh(user)
    return user


async def promote_user_to_admin(
    session: AsyncSession,
    *,
    actor_user_id: uuid.UUID,
    target_user_id: uuid.UUID,
    role: UserRole,
) -> User:
    if role not in (UserRole.USER, UserRole.ADMIN):
        raise ValueError("Invalid role")

    target = await session.get(User, target_user_id)
    if target is None:
        raise LookupError("User not found")

    previous = target.role
    if previous == role:
        return target

    # Prevent demoting the last admin.
    if previous == UserRole.ADMIN and role == UserRole.USER:
        admin_count = int(
            (
                await session.execute(
                    select(func.count()).select_from(User).where(User.role == UserRole.ADMIN)
                )
            ).scalar_one()
        )
        if admin_count <= 1:
            raise BootstrapError("Cannot demote the last admin")

    target.role = role
    await record_admin_audit(
        session,
        actor_user_id=actor_user_id,
        target_user_id=target.id,
        action=AdminAuditAction.ROLE_CHANGED,
        message=f"Role changed from {enum_value(previous)} to {enum_value(role)}",
        details={"previous_role": enum_value(previous), "new_role": enum_value(role)},
    )
    await session.flush()
    return target
