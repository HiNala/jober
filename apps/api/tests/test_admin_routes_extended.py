"""Admin dashboard routes not covered in test_admin_dashboard.py."""

from __future__ import annotations

import os

import pytest
from httpx import ASGITransport, AsyncClient

from jober_api.main import app
from jober_api.models.enums import UserRole
from jober_api.models.user import User

requires_postgres = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres",
)


@pytest.fixture
async def admin_user(db_session) -> User:
    from jober_api.auth.constants import DEFAULT_DEV_USER_ID

    user = await db_session.get(User, DEFAULT_DEV_USER_ID)
    assert user is not None
    user.role = UserRole.ADMIN
    await db_session.commit()
    return user


@requires_postgres
@pytest.mark.asyncio
async def test_admin_acquisition_forbidden_for_user(
    db_session, truncate_tables, auth_headers
) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/admin/acquisition", headers=auth_headers)
    assert response.status_code == 403


@requires_postgres
@pytest.mark.asyncio
async def test_admin_acquisition_shape(
    db_session, truncate_tables, admin_user, auth_headers
) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/admin/acquisition", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert "funnel" in body
    assert "traffic" in body


@requires_postgres
@pytest.mark.asyncio
async def test_admin_cost_forbidden_for_user(
    db_session, truncate_tables, auth_headers
) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/admin/cost", headers=auth_headers)
    assert response.status_code == 403


@requires_postgres
@pytest.mark.asyncio
async def test_admin_cost_shape(
    db_session, truncate_tables, admin_user, auth_headers
) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/admin/cost", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert "rollup_total_usd" in body
    assert "reconciled" in body


@requires_postgres
@pytest.mark.asyncio
async def test_admin_system_shape(
    db_session, truncate_tables, admin_user, auth_headers
) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/admin/system", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert "health" in body


@requires_postgres
@pytest.mark.asyncio
async def test_admin_data_requests_list(
    db_session, truncate_tables, admin_user, auth_headers
) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/admin/data-requests", headers=auth_headers)
    assert response.status_code == 200
    assert "items" in response.json()
