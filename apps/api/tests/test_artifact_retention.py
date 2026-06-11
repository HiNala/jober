"""Run artifact retention purge — storage growth guard."""

from __future__ import annotations

import os
import uuid
from datetime import UTC, datetime, timedelta

import pytest

from jober_api.auth.constants import DEFAULT_DEV_TENANT_ID
from jober_api.config import settings
from jober_api.models.application_run import ApplicationRun
from jober_api.models.enums import RunStatus
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.services.privacy.artifact_retention import purge_stale_run_artifacts

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres",
)


@pytest.mark.asyncio
async def test_purge_stale_terminal_runs_respects_retention(
    db_session, truncate_tables, monkeypatch: pytest.MonkeyPatch
) -> None:
    class FakeStorage:
        async def remove_prefix(self, prefix: str) -> int:
            return 0

    monkeypatch.setattr(
        "jober_api.services.privacy.retention.ObjectStorage",
        FakeStorage,
    )
    async def _noop_storage_state(_run_id: object) -> None:
        return None

    monkeypatch.setattr(
        "jober_api.services.privacy.retention.delete_run_storage_state",
        _noop_storage_state,
    )
    monkeypatch.setattr(settings, "run_artifact_retention_days", 30)
    jobs = JobTargetRepository(db_session)
    job = await jobs.create(company="Old Co", role="Eng")
    stale = ApplicationRun(
        id=uuid.uuid4(),
        tenant_id=DEFAULT_DEV_TENANT_ID,
        job_target_id=job.id,
        status=RunStatus.SUCCEEDED,
        created_at=datetime.now(UTC) - timedelta(days=60),
    )
    db_session.add(stale)
    await db_session.commit()

    result = await purge_stale_run_artifacts(db_session)

    assert result["purged_runs"] >= 1
    remaining = await db_session.get(ApplicationRun, stale.id)
    assert remaining is None
