#!/usr/bin/env python3
"""Ops-only admin provisioning: create or update a verified admin user with password."""

from __future__ import annotations

import argparse
import asyncio
import getpass
import sys
import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select

from jober_api.auth.password import hash_password
from jober_api.config import settings
from jober_api.db.session import async_session_factory
from jober_api.models.enums import AdminAuditAction, PlanTier, UserRole, UserStatus
from jober_api.models.tenant import Tenant
from jober_api.models.user import User
from jober_api.services.admin.audit import record_admin_audit
from jober_api.services.admin.bootstrap import BootstrapError


async def provision_admin(
    *,
    email: str,
    password: str,
    secret: str,
    display_name: str | None = None,
) -> User:
    expected = settings.admin_bootstrap_secret.strip()
    if not expected:
        raise BootstrapError("ADMIN_BOOTSTRAP_SECRET is not configured")
    if secret != expected:
        raise BootstrapError("Invalid bootstrap secret")

    normalized = email.strip().lower()
    if len(password) < 10:
        raise BootstrapError("Password must be at least 10 characters")

    async with async_session_factory() as session:
        user = (
            await session.execute(select(User).where(func.lower(User.email) == normalized))
        ).scalar_one_or_none()

        created = user is None
        if created:
            tenant = Tenant(
                id=uuid.uuid4(),
                name=display_name or normalized.split("@")[0],
                plan=PlanTier.FREE,
                policy={"default_run_policy": "review_before_submit", "auto_submit_opt_in": False},
            )
            user = User(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                email=normalized,
                display_name=display_name or normalized.split("@")[0],
                password_hash=hash_password(password),
                email_verified_at=datetime.now(UTC),
                status=UserStatus.ACTIVE,
                role=UserRole.ADMIN,
            )
            session.add(tenant)
            session.add(user)
            action = AdminAuditAction.BOOTSTRAP_ADMIN
            message = f"Provisioned new admin {normalized}"
        else:
            user.password_hash = hash_password(password)
            user.email_verified_at = datetime.now(UTC)
            user.status = UserStatus.ACTIVE
            user.role = UserRole.ADMIN
            if display_name:
                user.display_name = display_name
            action = AdminAuditAction.ROLE_CHANGED
            message = f"Updated admin credentials for {normalized}"

        await record_admin_audit(
            session,
            actor_user_id=user.id,
            target_user_id=user.id,
            action=action,
            message=message,
            details={"email": normalized, "created": created},
        )
        await session.commit()
        await session.refresh(user)
        return user


async def _run(email: str, password: str, secret: str, display_name: str | None) -> None:
    try:
        user = await provision_admin(
            email=email,
            password=password,
            secret=secret,
            display_name=display_name,
        )
    except BootstrapError as exc:
        print(f"Provision failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    role = user.role.value if hasattr(user.role, "value") else user.role
    print(f"Admin provisioned for {user.email} ({user.id}) role={role}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or update a Jober admin user (ops only)")
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", help="Admin password (prompted if omitted)")
    parser.add_argument("--display-name", default=None)
    parser.add_argument("--secret", help="ADMIN_BOOTSTRAP_SECRET (prompted if omitted)")
    args = parser.parse_args()
    password = args.password or getpass.getpass("Admin password: ")
    secret = args.secret or getpass.getpass("ADMIN_BOOTSTRAP_SECRET: ")
    asyncio.run(_run(args.email, password, secret, args.display_name))


if __name__ == "__main__":
    main()
