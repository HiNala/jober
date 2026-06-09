from __future__ import annotations

import os
import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from jober_api.auth.constants import DEFAULT_DEV_TENANT_ID, DEFAULT_DEV_USER_ID
from jober_api.main import app
from jober_api.models.admin_audit_log import AdminAuditLog
from jober_api.models.enum_utils import enum_value
from jober_api.models.enums import AdminAuditAction, PlanTier, UserRole, UserStatus
from jober_api.models.tenant import Tenant
from jober_api.models.user import User

requires_postgres = pytest.mark.skipif(
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


@requires_postgres
@pytest.mark.asyncio
async def test_user_blocked_from_admin_overview(db_session, truncate_tables, auth_headers) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/admin/overview", headers=auth_headers)
    assert response.status_code == 403


@requires_postgres
@pytest.mark.asyncio
async def test_admin_overview_returns_attention_shape(
    db_session, truncate_tables, admin_user, auth_headers
) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/admin/overview", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert "active_users" in body
    assert "signups" in body
    assert "attention" in body
    assert "health" in body


@requires_postgres
@pytest.mark.asyncio
async def test_admin_runs_summary_forbidden_for_user(
    db_session, truncate_tables, auth_headers
) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/admin/runs", headers=auth_headers)
    assert response.status_code == 403


@requires_postgres
@pytest.mark.asyncio
async def test_support_view_audited(
    db_session, truncate_tables, admin_user, auth_headers
) -> None:
    other = User(
        id=uuid.uuid4(),
        tenant_id=DEFAULT_DEV_TENANT_ID,
        email="support@test.local",
        status=UserStatus.ACTIVE,
        role=UserRole.USER,
    )
    db_session.add(other)
    await db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            f"/api/admin/users/{other.id}/operational",
            headers=auth_headers,
        )
    assert response.status_code == 200
    assert "privacy_note" in response.json()
    row = (
        await db_session.execute(
            select(AdminAuditLog).where(
                AdminAuditLog.target_user_id == other.id,
                AdminAuditLog.action == AdminAuditAction.SUPPORT_VIEW_ACCESSED,
            )
        )
    ).scalar_one()
    assert enum_value(row.action) == AdminAuditAction.SUPPORT_VIEW_ACCESSED.value


@requires_postgres
@pytest.mark.asyncio
async def test_admin_config_update_audited(
    db_session, truncate_tables, admin_user, auth_headers
) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.patch(
            "/api/admin/config/feature_flags",
            headers=auth_headers,
            json={"value": {"discovery_enabled": False}},
        )
    assert response.status_code == 200
    row = (
        await db_session.execute(
            select(AdminAuditLog).where(AdminAuditLog.action == AdminAuditAction.CONFIG_CHANGED)
        )
    ).scalar_one()
    assert row.resource_id == "feature_flags"


@requires_postgres
@pytest.mark.asyncio
async def test_admin_user_search(
    db_session, truncate_tables, admin_user, auth_headers
) -> None:
    other_tenant = Tenant(id=uuid.uuid4(), name="SearchCo", plan=PlanTier.FREE, policy={})
    other = User(
        id=uuid.uuid4(),
        tenant_id=other_tenant.id,
        email="findme@searchco.local",
        status=UserStatus.ACTIVE,
        role=UserRole.USER,
    )
    db_session.add_all([other_tenant, other])
    await db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/admin/users",
            headers=auth_headers,
            params={"q": "findme"},
        )
    assert response.status_code == 200
    emails = [row["email"] for row in response.json()["items"]]
    assert "findme@searchco.local" in emails
