from __future__ import annotations

import os

import pytest
from httpx import ASGITransport, AsyncClient

from jober_api.auth.constants import DEFAULT_DEV_USER_ID
from jober_api.config import settings
from jober_api.main import app
from jober_api.models.user_provider_key import UserProviderKey

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres",
)


@pytest.mark.asyncio
async def test_preferences_round_trip(db_session, truncate_tables, auth_headers) -> None:
    del db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        get_resp = await client.get("/api/settings/preferences", headers=auth_headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["preferences"]["appearance"]["theme"] == "dark"

        patch_resp = await client.patch(
            "/api/settings/preferences",
            headers=auth_headers,
            json={"appearance": {"theme": "light", "density": "compact"}},
        )
        assert patch_resp.status_code == 200
        prefs = patch_resp.json()["preferences"]
        assert prefs["appearance"]["theme"] == "light"
        assert prefs["appearance"]["density"] == "compact"
        assert prefs["notifications"]["in_app_run_attention"] is True


@pytest.mark.asyncio
async def test_provider_keys_never_return_full_secret(
    db_session,
    truncate_tables,
    auth_headers,
    vault_key,
    monkeypatch,
) -> None:
    monkeypatch.setattr(settings, "vault_encryption_key", vault_key)
    secret = "sk-test-user-key-abcdef12"
    db_session.add(
        UserProviderKey(
            user_id=DEFAULT_DEV_USER_ID,
            provider="openai",
            encrypted_api_key=secret,
            key_hint="ef12",
        )
    )
    await db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/settings/provider-keys", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["items"]) == 1
        item = body["items"][0]
        assert item["configured"] is True
        assert item["key_hint"] == "ef12"
        assert secret not in resp.text


@pytest.mark.asyncio
async def test_provider_keys_put_never_returns_full_secret(
    db_session,
    truncate_tables,
    auth_headers,
    vault_key,
    monkeypatch,
) -> None:
    del db_session
    monkeypatch.setattr(settings, "vault_encryption_key", vault_key)
    secret = "sk-put-test-key-abcdef12"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.put(
            "/api/settings/provider-keys/openai",
            headers=auth_headers,
            json={"api_key": secret},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["configured"] is True
        assert body["key_hint"] == "ef12"
        assert secret not in resp.text
