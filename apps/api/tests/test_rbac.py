from __future__ import annotations

import os
import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from jober_api.auth.constants import DEFAULT_DEV_TENANT_ID, DEFAULT_DEV_USER_ID
from jober_api.auth.context import AuthContext
from jober_api.auth.permissions import Permission, can
from jober_api.main import app
from jober_api.models.admin_audit_log import AdminAuditLog
from jober_api.models.enums import PlanTier, UserRole, UserStatus
from jober_api.models.tenant import Tenant
from jober_api.models.user import User
from jober_api.services.admin.bootstrap import BootstrapError, bootstrap_first_admin

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres",
)


@pytest.fixture
async def admin_user(db_session) -> User:
    user = await db_session.get(User, DEFAULT_DEV_USER_ID)
    assert user is not None
    user.role = UserRole.ADMIN
    await db_session.commit()
    return user


def test_can_default_deny_unknown_permission() -> None:
    actor = AuthContext(
        user_id=DEFAULT_DEV_USER_ID,
        tenant_id=DEFAULT_DEV_TENANT_ID,
        email="u@test.local",
        plan=PlanTier.PRO,
        role=UserRole.USER,
    )
    assert can(actor, Permission.AUTHENTICATED) is True
    assert can(actor, Permission.ADMIN_USERS_MANAGE) is False


@pytest.mark.asyncio
async def test_user_blocked_from_admin_routes(db_session, truncate_tables, auth_headers) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        funnel = await client.get("/api/analytics/admin/funnel", headers=auth_headers)
        users = await client.get("/api/admin/users", headers=auth_headers)
    assert funnel.status_code == 403
    assert users.status_code == 403


@pytest.mark.asyncio
async def test_admin_reaches_admin_routes(
    db_session, truncate_tables, admin_user, auth_headers
) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/admin/users", headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_privilege_escalation_via_api_forbidden(
    db_session, truncate_tables, auth_headers
) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.patch(
            f"/api/admin/users/{DEFAULT_DEV_USER_ID}/role",
            headers=auth_headers,
            json={"role": "admin"},
        )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_promote_writes_audit_log(
    db_session, truncate_tables, admin_user, auth_headers
) -> None:
    other = User(
        id=uuid.uuid4(),
        tenant_id=DEFAULT_DEV_TENANT_ID,
        email="other@test.local",
        status=UserStatus.ACTIVE,
        role=UserRole.USER,
    )
    db_session.add(other)
    await db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.patch(
            f"/api/admin/users/{other.id}/role",
            headers=auth_headers,
            json={"role": "admin"},
        )
    assert response.status_code == 200
    row = (
        await db_session.execute(
            select(AdminAuditLog).where(AdminAuditLog.target_user_id == other.id)
        )
    ).scalar_one()
    assert row.action.value == "role_changed"


@pytest.mark.asyncio
async def test_bootstrap_first_admin_requires_secret(
    db_session, truncate_tables, monkeypatch
) -> None:
    monkeypatch.setattr(
        "jober_api.services.admin.bootstrap.settings.admin_bootstrap_secret", "test-secret"
    )
    user = await db_session.get(User, DEFAULT_DEV_USER_ID)
    assert user is not None
    with pytest.raises(BootstrapError):
        await bootstrap_first_admin(db_session, email=user.email, secret="wrong")


@pytest.mark.asyncio
async def test_bootstrap_first_admin_promotes_once(
    db_session, truncate_tables, monkeypatch
) -> None:
    monkeypatch.setattr(
        "jober_api.services.admin.bootstrap.settings.admin_bootstrap_secret", "test-secret"
    )
    user = await db_session.get(User, DEFAULT_DEV_USER_ID)
    assert user is not None
    promoted = await bootstrap_first_admin(db_session, email=user.email, secret="test-secret")
    assert promoted.role == UserRole.ADMIN
    with pytest.raises(BootstrapError, match="already exists"):
        await bootstrap_first_admin(db_session, email=user.email, secret="test-secret")


@pytest.mark.asyncio
async def test_cross_tenant_user_list_does_not_expose_vault(
    db_session, truncate_tables, admin_user, auth_headers
) -> None:
    other_tenant = Tenant(id=uuid.uuid4(), name="Other", plan=PlanTier.FREE, policy={})
    other_user = User(
        id=uuid.uuid4(),
        tenant_id=other_tenant.id,
        email="isolated@test.local",
        status=UserStatus.ACTIVE,
        role=UserRole.USER,
    )
    db_session.add_all([other_tenant, other_user])
    await db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/admin/users", headers=auth_headers)
    assert response.status_code == 200
    emails = {row["email"] for row in response.json()["items"]}
    assert "isolated@test.local" in emails
    for row in response.json()["items"]:
        assert "password_hash" not in row
        assert "vault" not in row
