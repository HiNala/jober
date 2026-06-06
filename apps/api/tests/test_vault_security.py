from __future__ import annotations

import json
import os

import pytest
from sqlalchemy import text

from jober_api.models.user_profile import UserProfile
from jober_api.repositories.user_profile import UserProfileRepository
from jober_api.vault.fill_policy import FillOutcome, resolve_field_fill
from jober_api.vault.sensitive_store import merge_sensitive_answers

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres",
)


def test_plaintext_work_authorization_column_is_never_autofilled() -> None:
    """Legacy plaintext column must not bypass encrypted vault + consent rules."""
    profile = UserProfile(
        work_authorization="Authorized to work in the US",
        field_consent={"work_authorization": {"consent": True, "never_autofill": False}},
    )
    resolution = resolve_field_fill(profile, "work_authorization")
    assert resolution.outcome == FillOutcome.NEEDS_HUMAN


@pytest.mark.asyncio
async def test_vault_merge_writes_ciphertext_at_rest(
    db_session,
    truncate_tables,
    raw_connection,
) -> None:
    repo = UserProfileRepository(db_session)
    profile = await repo.create(name="Vault User")
    merge_sensitive_answers(
        profile,
        {"disability": "prefer_not_to_answer"},
    )
    profile.field_consent = {
        "disability": {"consent": True, "never_autofill": False, "consented_at": "2026-01-01"},
    }
    await db_session.commit()

    loaded = await repo.get(profile.id)
    assert loaded is not None
    assert json.loads(loaded.sensitive_eeo_answers or "{}")["disability"] == "prefer_not_to_answer"

    result = await raw_connection.execute(
        text("SELECT sensitive_eeo_answers FROM user_profiles WHERE id = :id"),
        {"id": profile.id},
    )
    raw_bytes = result.scalar_one()
    raw = bytes(raw_bytes)
    assert b"prefer_not_to_answer" not in raw
