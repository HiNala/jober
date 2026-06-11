from __future__ import annotations

import os
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from jober_api.auth.password import hash_password
from jober_api.config import settings
from jober_api.main import app
from jober_api.models.enums import PlanTier, UserStatus
from jober_api.models.tenant import Tenant
from jober_api.models.user import User

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres + Redis",
)


@pytest.mark.asyncio
async def test_register_verify_login_reset_cycle(db_session, truncate_tables, monkeypatch) -> None:
    from jober_api.db import session as db_session_module

    monkeypatch.setattr(settings, "auth_mode", "native")
    monkeypatch.setattr(settings, "jober_env", "development")

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            reg = await client.post(
                "/api/auth/register",
                json={
                    "email": "newuser@example.com",
                    "password": "Str0ng!Passw0rd",
                    "display_name": "New User",
                },
            )
            assert reg.status_code == 200
            verify_token = reg.headers.get("X-Jober-Verify-Token")
            assert verify_token

            verify = await client.post("/api/auth/verify-email", json={"token": verify_token})
            assert verify.status_code == 200
            assert verify.json()["email_verified"] is True

            cookies = reg.cookies
            me = await client.get("/api/auth/me", cookies=cookies)
            assert me.status_code == 200

            forgot = await client.post(
                "/api/auth/forgot-password",
                json={"email": "newuser@example.com"},
            )
            reset_token = forgot.headers.get("X-Jober-Reset-Token")
            assert reset_token

            reset = await client.post(
                "/api/auth/reset-password",
                json={"token": reset_token, "new_password": "N3wStr0ng!Pass"},
            )
            assert reset.status_code == 200

            logout = await client.post(
                "/api/auth/logout",
                cookies=cookies,
                headers={"X-CSRF-Token": cookies.get(settings.csrf_cookie_name, "")},
            )
            assert logout.status_code == 200

            login = await client.post(
                "/api/auth/login",
                json={"email": "newuser@example.com", "password": "N3wStr0ng!Pass"},
            )
            assert login.status_code == 200
            assert login.json()["email"] == "newuser@example.com"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_cross_account_cookie_session_blocked(
    db_session, truncate_tables, monkeypatch
) -> None:
    from jober_api.auth.constants import DEFAULT_DEV_TENANT_ID
    from jober_api.auth.sessions import create_session
    from jober_api.db import session as db_session_module
    from jober_api.models.enums import JobTargetStatus
    from jober_api.repositories.job_target import JobTargetRepository

    monkeypatch.setattr(settings, "auth_mode", "native")

    tenant_b = uuid.UUID("00000000-0000-4000-8000-000000000099")
    user_b = uuid.UUID("00000000-0000-4000-8000-00000000009b")
    db_session.add(
        Tenant(
            id=tenant_b,
            name="Tenant B",
            plan=PlanTier.FREE,
            policy={"default_run_policy": "review_before_submit"},
        )
    )
    db_session.add(
        User(
            id=user_b,
            tenant_id=tenant_b,
            email="b@example.com",
            display_name="B",
            password_hash=hash_password("Str0ng!Passw0rd"),
            status=UserStatus.ACTIVE,
        )
    )
    jobs_a = JobTargetRepository(db_session, DEFAULT_DEV_TENANT_ID)
    job_a = await jobs_a.create(company="Secret Co", role="Eng", status=JobTargetStatus.NEW)
    await db_session.commit()

    session_id, refresh_id, csrf = await create_session(user_b, tenant_b)
    cookies = {
        settings.session_cookie_name: session_id,
        settings.refresh_cookie_name: refresh_id,
        settings.csrf_cookie_name: csrf,
    }

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            listing = await client.get("/api/job-targets", cookies=cookies)
            assert listing.status_code == 200
            items = listing.json()["items"]
            assert all(item["company"] != "Secret Co" for item in items)
            missing = await client.get(f"/api/job-targets/{job_a.id}", cookies=cookies)
            assert missing.status_code == 404
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_lockout_after_failed_logins(db_session, truncate_tables, monkeypatch) -> None:
    from jober_api.db import session as db_session_module

    monkeypatch.setattr(settings, "auth_mode", "native")
    monkeypatch.setattr(settings, "auth_lockout_threshold", 3)

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            await client.post(
                "/api/auth/register",
                json={"email": "lock@example.com", "password": "Str0ng!Passw0rd"},
            )
            for _ in range(3):
                bad = await client.post(
                    "/api/auth/login",
                    json={"email": "lock@example.com", "password": "wrong-password"},
                )
                assert bad.status_code == 401
            locked = await client.post(
                "/api/auth/login",
                json={"email": "lock@example.com", "password": "Str0ng!Passw0rd"},
            )
            assert locked.status_code == 429
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_passwords_stored_as_argon2_hash(db_session, truncate_tables, monkeypatch) -> None:
    from jober_api.db import session as db_session_module

    monkeypatch.setattr(settings, "auth_mode", "native")
    monkeypatch.setattr(settings, "jober_env", "development")

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            await client.post(
                "/api/auth/register",
                json={"email": "hash@example.com", "password": "Str0ng!Passw0rd"},
            )
        from sqlalchemy import select

        stmt = select(User).where(User.email == "hash@example.com")
        user = (await db_session.execute(stmt)).scalar_one()
        assert user.password_hash is not None
        assert user.password_hash.startswith("$argon2")
        assert "Str0ng" not in user.password_hash
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_logout_invalidates_session_server_side(
    db_session, truncate_tables, monkeypatch
) -> None:
    from jober_api.auth.sessions import load_session
    from jober_api.db import session as db_session_module

    monkeypatch.setattr(settings, "auth_mode", "native")
    monkeypatch.setattr(settings, "jober_env", "development")

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            reg = await client.post(
                "/api/auth/register",
                json={
                    "email": "logout-invalidate@example.com",
                    "password": "Str0ng!Passw0rd",
                    "display_name": "Logout Test",
                },
            )
            assert reg.status_code == 200
            cookies = reg.cookies
            session_id = cookies.get(settings.session_cookie_name)
            assert session_id
            assert await load_session(session_id) is not None

            csrf = cookies.get(settings.csrf_cookie_name, "")
            logout = await client.post(
                "/api/auth/logout",
                cookies=cookies,
                headers={"X-CSRF-Token": csrf},
            )
            assert logout.status_code == 200
            assert await load_session(session_id) is None

            me = await client.get("/api/auth/me", cookies=cookies)
            assert me.status_code == 401
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_password_change_revokes_other_sessions(
    db_session, truncate_tables, monkeypatch
) -> None:
    from jober_api.auth.constants import DEFAULT_DEV_TENANT_ID, DEFAULT_DEV_USER_ID
    from jober_api.auth.password import hash_password
    from jober_api.auth.sessions import create_session, load_session
    from jober_api.db import session as db_session_module
    from jober_api.models.user import User

    monkeypatch.setattr(settings, "auth_mode", "native")

    user_id = DEFAULT_DEV_USER_ID
    user = await db_session.get(User, user_id)
    assert user is not None
    user.password_hash = hash_password("Str0ng!Passw0rd")
    await db_session.commit()

    session_a, refresh_a, csrf_a = await create_session(user_id, DEFAULT_DEV_TENANT_ID)
    session_b, refresh_b, csrf_b = await create_session(user_id, DEFAULT_DEV_TENANT_ID)

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    transport = ASGITransport(app=app)
    cookies_a = {
        settings.session_cookie_name: session_a,
        settings.refresh_cookie_name: refresh_a,
        settings.csrf_cookie_name: csrf_a,
    }
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            changed = await client.post(
                "/api/auth/change-password",
                cookies=cookies_a,
                headers={"X-CSRF-Token": csrf_a},
                json={
                    "current_password": "Str0ng!Passw0rd",
                    "new_password": "N3wStr0ng!Passw0rd",
                },
            )
            assert changed.status_code == 200
        assert await load_session(session_a) is not None
        assert await load_session(session_b) is None
    finally:
        app.dependency_overrides.clear()


def test_dev_auth_bypass_forbidden_in_production(monkeypatch) -> None:
    monkeypatch.setattr(settings, "jober_env", "production")
    monkeypatch.setattr(settings, "dev_auth_bypass", True)
    from jober_api.privacy.secrets_check import validate_startup_secrets

    with pytest.raises(RuntimeError, match="DEV_AUTH_BYPASS"):
        validate_startup_secrets()
