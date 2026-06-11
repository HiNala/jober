"""Privacy purge must remove object-storage keys, not only DB rows."""

from __future__ import annotations

import os

import pytest

from jober_api.models.application_run import ApplicationRun
from jober_api.models.enums import RunStatus
from jober_api.repositories.application_run import ApplicationRunRepository
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.services.privacy.retention import purge_run

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres",
)


@pytest.mark.asyncio
async def test_purge_run_removes_object_storage_prefix(
    db_session,
    truncate_tables,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    removed_prefixes: list[str] = []

    class FakeStorage:
        async def remove_prefix(self, prefix: str) -> int:
            removed_prefixes.append(prefix)
            return 2

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

    jobs = JobTargetRepository(db_session)
    job = await jobs.create(company="Store Co", role="Eng")
    runs = ApplicationRunRepository(db_session)
    run = await runs.create(job_target_id=job.id, status=RunStatus.SUCCEEDED)
    await db_session.commit()

    result = await purge_run(db_session, run.id, tenant_id=run.tenant_id)

    assert result["status"] == "purged"
    assert result["removed_objects"] == 2
    assert len(removed_prefixes) == 1
    assert str(run.id) in removed_prefixes[0]
    assert await db_session.get(ApplicationRun, run.id) is None
