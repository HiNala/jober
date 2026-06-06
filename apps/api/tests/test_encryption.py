import json
import os

import pytest
from sqlalchemy import text

from jober_api.repositories.user_profile import UserProfileRepository

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres",
)


@pytest.mark.asyncio
async def test_sensitive_field_encrypted_at_rest(
    db_session,
    truncate_tables,
    vault_key: str,
    raw_connection,
) -> None:
    repo = UserProfileRepository(db_session)
    payload = json.dumps({"veteran_status": "prefer_not", "disability": "no"})
    profile = await repo.create(
        name="Vault User",
        sensitive_eeo_answers=payload,
    )
    await db_session.commit()

    loaded = await repo.get(profile.id)
    assert loaded is not None
    assert loaded.sensitive_eeo_answers == payload

    result = await raw_connection.execute(
        text("SELECT sensitive_eeo_answers FROM user_profiles WHERE id = :id"),
        {"id": profile.id},
    )
    raw_bytes = result.scalar_one()
    assert isinstance(raw_bytes, (bytes, memoryview))
    raw = bytes(raw_bytes)
    assert raw != payload.encode("utf-8")
    assert payload not in raw.decode("latin-1", errors="ignore")
