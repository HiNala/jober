from __future__ import annotations

import os
import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from jober_api.auth.oauth.state_store import StoredOAuthState, consume_oauth_state, save_oauth_state
from jober_api.auth.oauth.types import OAuthIntent, OAuthProfile
from jober_api.auth.password import hash_password
from jober_api.config import settings
from jober_api.main import app
from jober_api.models.enums import AuthProvider, PlanTier, UserStatus
from jober_api.models.tenant import Tenant
from jober_api.models.user import User
from jober_api.repositories.auth_identity import AuthIdentityRepository

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres + Redis",
)

MOCK_PROFILE = OAuthProfile(
    provider_user_id="google-sub-123",
    email="oauth@example.com",
    email_verified=True,
    display_name="OAuth User",
    avatar_url="https://example.com/avatar.png",
)


@pytest.fixture
def google_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "google_client_id", "test-client-id")
    monkeypatch.setattr(settings, "google_client_secret", "test-client-secret")
    monkeypatch.setattr(settings, "google_redirect_uri", "http://test/api/auth/google/callback")
    monkeypatch.setattr(settings, "web_app_url", "http://localhost:3000")
    monkeypatch.setattr(settings, "auth_mode", "native")


@pytest.mark.asyncio
async def test_google_sign_in_creates_user_and_identity(
    db_session, truncate_tables, google_configured, monkeypatch
) -> None:
    from jober_api.db import session as db_session_module

    state = "test-state-signin"
    await save_oauth_state(
        state,
        StoredOAuthState(code_verifier="verifier", intent=OAuthIntent.SIGN_IN),
    )

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override

    with patch(
        "jober_api.auth.oauth.google.GoogleOAuthProvider.exchange_code",
        new=AsyncMock(return_value=MOCK_PROFILE),
    ):
        transport = ASGITransport(app=app)
        try:
            async with AsyncClient(
                transport=transport,
                base_url="http://test",
                follow_redirects=False,
            ) as client:
                res = await client.get(
                    "/api/auth/google/callback",
                    params={"code": "auth-code", "state": state},
                )
                assert res.status_code == 302
                assert res.headers["location"].endswith("/dashboard")
                assert settings.session_cookie_name in res.cookies
        finally:
            app.dependency_overrides.clear()

    repo = AuthIdentityRepository(db_session)
    identity = await repo.find_by_provider_subject(AuthProvider.GOOGLE, "google-sub-123")
    assert identity is not None
    assert identity.provider_email == "oauth@example.com"


@pytest.mark.asyncio
async def test_google_sign_in_requires_confirmation_for_verified_native_email(
    db_session, truncate_tables, google_configured, monkeypatch
) -> None:
    from datetime import UTC, datetime

    from jober_api.db import session as db_session_module

    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    db_session.add(
        Tenant(id=tenant_id, name="Native", plan=PlanTier.FREE, policy={}),
    )
    db_session.add(
        User(
            id=user_id,
            tenant_id=tenant_id,
            email="oauth@example.com",
            password_hash=hash_password("Str0ng!Passw0rd"),
            email_verified_at=datetime.now(UTC),
            status=UserStatus.ACTIVE,
        )
    )
    await db_session.commit()

    state = "test-state-confirm"
    await save_oauth_state(
        state,
        StoredOAuthState(code_verifier="verifier", intent=OAuthIntent.SIGN_IN),
    )

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override

    with patch(
        "jober_api.auth.oauth.google.GoogleOAuthProvider.exchange_code",
        new=AsyncMock(return_value=MOCK_PROFILE),
    ):
        transport = ASGITransport(app=app)
        try:
            async with AsyncClient(
                transport=transport,
                base_url="http://test",
                follow_redirects=False,
            ) as client:
                res = await client.get(
                    "/api/auth/google/callback",
                    params={"code": "auth-code", "state": state},
                )
                assert res.status_code == 302
                assert "/link-google?token=" in res.headers["location"]
                assert settings.session_cookie_name not in res.cookies
        finally:
            app.dependency_overrides.clear()

    repo = AuthIdentityRepository(db_session)
    assert await repo.find_by_provider_subject(AuthProvider.GOOGLE, "google-sub-123") is None


@pytest.mark.asyncio
async def test_confirm_link_merges_google_identity(
    db_session, truncate_tables, google_configured, monkeypatch
) -> None:
    from datetime import UTC, datetime

    from jober_api.auth.oauth.state_store import PendingOAuthLink, save_pending_link
    from jober_api.db import session as db_session_module

    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    db_session.add(
        Tenant(id=tenant_id, name="Native", plan=PlanTier.FREE, policy={}),
    )
    db_session.add(
        User(
            id=user_id,
            tenant_id=tenant_id,
            email="oauth@example.com",
            password_hash=hash_password("Str0ng!Passw0rd"),
            email_verified_at=datetime.now(UTC),
            status=UserStatus.ACTIVE,
        )
    )
    await db_session.commit()

    token = "link-token-abc"
    await save_pending_link(
        token,
        PendingOAuthLink(
            provider=AuthProvider.GOOGLE.value,
            provider_user_id="google-sub-123",
            provider_email="oauth@example.com",
            display_name="OAuth User",
            avatar_url=None,
            existing_user_id=str(user_id),
        ),
    )

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            bad = await client.post(
                "/api/auth/google/confirm-link",
                json={"token": token, "password": "wrong-password"},
            )
            assert bad.status_code == 401

            ok = await client.post(
                "/api/auth/google/confirm-link",
                json={"token": token, "password": "Str0ng!Passw0rd"},
            )
            assert ok.status_code == 200
            assert ok.json()["email"] == "oauth@example.com"
            assert settings.session_cookie_name in ok.cookies
    finally:
        app.dependency_overrides.clear()

    repo = AuthIdentityRepository(db_session)
    identity = await repo.find_by_provider_subject(AuthProvider.GOOGLE, "google-sub-123")
    assert identity is not None
    assert identity.user_id == user_id


@pytest.mark.asyncio
async def test_cannot_unlink_only_google_credential(
    db_session, truncate_tables, google_configured, monkeypatch
) -> None:
    from datetime import UTC, datetime

    from jober_api.auth.sessions import create_session
    from jober_api.db import session as db_session_module
    from jober_api.models.auth_identity import AuthIdentity

    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    db_session.add(
        Tenant(id=tenant_id, name="OAuth Only", plan=PlanTier.FREE, policy={}),
    )
    db_session.add(
        User(
            id=user_id,
            tenant_id=tenant_id,
            email="oauth-only@example.com",
            password_hash=None,
            email_verified_at=datetime.now(UTC),
            status=UserStatus.ACTIVE,
        )
    )
    db_session.add(
        AuthIdentity(
            id=uuid.uuid4(),
            user_id=user_id,
            provider=AuthProvider.GOOGLE,
            provider_user_id="google-only",
            provider_email="oauth-only@example.com",
        )
    )
    await db_session.commit()

    session_id, refresh_id, csrf = await create_session(user_id, tenant_id)
    cookies = {
        settings.session_cookie_name: session_id,
        settings.refresh_cookie_name: refresh_id,
        settings.csrf_cookie_name: csrf,
    }
    headers = {"X-CSRF-Token": csrf}

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.delete(
                "/api/auth/identities/google",
                cookies=cookies,
                headers=headers,
            )
            assert res.status_code == 400
            assert "only sign-in" in res.json()["detail"].lower()
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_oauth_state_is_single_use(google_configured) -> None:
    state = "one-time-state"
    await save_oauth_state(
        state,
        StoredOAuthState(code_verifier="v", intent=OAuthIntent.SIGN_IN),
    )
    first = await consume_oauth_state(state)
    assert first is not None
    second = await consume_oauth_state(state)
    assert second is None
