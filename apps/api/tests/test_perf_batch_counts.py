"""Performance regression fixtures for batch queue aggregates."""

from __future__ import annotations

import os

import pytest

from jober_api.auth.constants import DEFAULT_DEV_TENANT_ID
from jober_api.models.application_batch import ApplicationBatch
from jober_api.models.batch_item import BatchItem
from jober_api.models.enums import BatchItemStatus, BatchStatus, JobTargetStatus, RunPolicy
from jober_api.repositories.application_batch import BatchItemRepository
from jober_api.repositories.job_target import JobTargetRepository

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres",
)


@pytest.mark.asyncio
async def test_count_by_status_uses_sql_aggregate(db_session, truncate_tables) -> None:
    jobs = JobTargetRepository(db_session)
    job_a = await jobs.create(
        company="A",
        role="Eng",
        status=JobTargetStatus.NEW,
        direct_apply_url="https://boards.greenhouse.io/a/jobs/1",
    )
    job_b = await jobs.create(
        company="B",
        role="Eng",
        status=JobTargetStatus.NEW,
        direct_apply_url="https://boards.greenhouse.io/b/jobs/2",
    )
    batch = ApplicationBatch(
        tenant_id=DEFAULT_DEV_TENANT_ID,
        name="counts",
        status=BatchStatus.RUNNING,
        policy=RunPolicy.DRY_RUN,
        filters={},
    )
    db_session.add(batch)
    await db_session.flush()
    db_session.add_all(
        [
            BatchItem(
                batch_id=batch.id,
                job_target_id=job_a.id,
                sort_order=0,
                status=BatchItemStatus.PENDING,
                domain="boards.greenhouse.io",
            ),
            BatchItem(
                batch_id=batch.id,
                job_target_id=job_b.id,
                sort_order=1,
                status=BatchItemStatus.SUCCEEDED,
                domain="boards.greenhouse.io",
            ),
        ]
    )
    await db_session.commit()

    counts = await BatchItemRepository(db_session).count_by_status(batch.id)
    assert counts == {"pending": 1, "succeeded": 1}
