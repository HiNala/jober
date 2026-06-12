from __future__ import annotations

import json
import os

import pytest
from sqlalchemy import text

from jober_api.models.enums import JobTargetStatus, RunStatus
from jober_api.privacy.redaction import register_runtime_secrets, scrub_dict, scrub_text
from jober_api.repositories.application_run import ApplicationRunRepository
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.repositories.run_event import RunEventRepository

pytestmark = [
    pytest.mark.policy,
    pytest.mark.skipif(
        os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
        reason="requires Postgres for event persistence test",
    ),
]


@pytest.fixture(autouse=True)
def _register_test_secrets() -> None:
    register_runtime_secrets(
        "sk-test-secret-key-abcdefghijklmnop",
        "super-secret-password-12345",
        "nalamaui30@gmail.com",
    )


def test_scrub_text_masks_registered_secrets_and_pii() -> None:
    raw = (
        "Contact nalamaui30@gmail.com token=sk-test-secret-key-abcdefghijklmnop "
        "password=super-secret-password-12345"
    )
    scrubbed = scrub_text(raw)
    assert "sk-test-secret-key" not in scrubbed
    assert "super-secret-password" not in scrubbed
    assert "nalamaui30@gmail.com" not in scrubbed
    assert "[REDACTED" in scrubbed


def test_scrub_text_masks_bearer_and_jwt_tokens() -> None:
    jwt = (
        "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0."
        "dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
    )
    scrubbed = scrub_text(f"Authorization: Bearer {jwt}")
    assert jwt not in scrubbed
    assert "Bearer [REDACTED" in scrubbed


def test_scrub_dict_redacts_sensitive_keys() -> None:
    payload = scrub_dict(
        {
            "email": "user@example.com",
            "password": "hunter2",
            "storage_state": {"cookies": [{"name": "session"}]},
            "note": "call me at 555-123-4567",
        }
    )
    assert payload["password"] == "[REDACTED]"
    assert payload["storage_state"] == "[REDACTED]"
    assert "user@example.com" not in json.dumps(payload)


@pytest.mark.asyncio
async def test_run_event_persistence_scrubs_secrets(db_session, truncate_tables) -> None:
    jobs = JobTargetRepository(db_session)
    job = await jobs.create(
        company="Privacy Co",
        role="Eng",
        status=JobTargetStatus.NEW,
        priority="A",
    )
    runs = ApplicationRunRepository(db_session)
    run = await runs.create(job_target_id=job.id, status=RunStatus.QUEUED)
    await db_session.commit()

    repo = RunEventRepository(db_session)
    secret = "sk-test-secret-key-abcdefghijklmnop"
    await repo.append(
        run_id=run.id,
        event_type="test.secret",
        message=f"Bearer {secret} emailed nalamaui30@gmail.com",
        payload={"api_key": secret, "note": "ok"},
    )
    await db_session.commit()

    row = (
        await db_session.execute(
            text("SELECT message, payload::text FROM run_events WHERE run_id = :run_id"),
            {"run_id": run.id},
        )
    ).one()
    stored = f"{row.message} {row[1]}"
    assert secret not in stored
    assert "nalamaui30@gmail.com" not in stored


@pytest.mark.asyncio
async def test_browser_storage_state_encrypted_in_minio() -> None:
    if os.getenv("CI") != "true" and os.getenv("RUN_INTEGRATION") != "1":
        pytest.skip("requires MinIO")

    import uuid

    from jober_api.privacy.browser_state import load_run_storage_state, save_run_storage_state
    from jober_api.storage.keys import run_storage_state_key
    from jober_api.storage.minio_client import ObjectStorage

    run_id = uuid.uuid4()
    state = {"cookies": [{"name": "session", "value": "top-secret-cookie"}]}
    await save_run_storage_state(run_id, state)
    raw = await ObjectStorage().get_bytes(run_storage_state_key(run_id))
    assert b"top-secret-cookie" not in raw
    restored = await load_run_storage_state(run_id)
    assert restored == state
    await ObjectStorage().remove_object(run_storage_state_key(run_id))
