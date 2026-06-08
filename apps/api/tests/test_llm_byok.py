from __future__ import annotations

import os

import pytest

from jober_api.auth.constants import DEFAULT_DEV_USER_ID
from jober_api.config import settings
from jober_api.models.user_provider_key import UserProviderKey
from jober_api.services.llm.gateway import HttpLlmProvider, resolve_llm_runtime

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres",
)


@pytest.mark.asyncio
async def test_resolve_llm_runtime_prefers_user_byok(
    db_session,
    truncate_tables,
    vault_key,
    monkeypatch,
) -> None:
    monkeypatch.setattr(settings, "vault_encryption_key", vault_key)
    monkeypatch.setattr(settings, "llm_provider", "openai")
    monkeypatch.setattr(settings, "llm_api_key", "")

    db_session.add(
        UserProviderKey(
            user_id=DEFAULT_DEV_USER_ID,
            provider="openai",
            encrypted_api_key="sk-byok-test-key-12345678",
            key_hint="5678",
        )
    )
    await db_session.commit()

    provider, runtime = await resolve_llm_runtime(db_session, DEFAULT_DEV_USER_ID)
    assert runtime.using_byok is True
    assert isinstance(provider, HttpLlmProvider)
