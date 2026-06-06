import os

import pytest

from jober_api.models.enums import JobTargetStatus, RunPolicy, RunStatus
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.repositories.user_profile import UserProfileRepository

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres",
)


@pytest.mark.asyncio
async def test_job_target_round_trip(db_session, truncate_tables) -> None:
    repo = JobTargetRepository(db_session)
    created = await repo.create(
        company="TestCo",
        role="Engineer",
        priority="A",
        status=JobTargetStatus.QUEUED,
    )
    await db_session.commit()

    loaded = await repo.get(created.id)
    assert loaded is not None
    assert loaded.company == "TestCo"
    assert loaded.status == JobTargetStatus.QUEUED


@pytest.mark.asyncio
async def test_application_run_defaults(db_session, truncate_tables) -> None:
    jobs = JobTargetRepository(db_session)
    job = await jobs.create(company="RunCo", role="SWE")
    await db_session.flush()

    from jober_api.models.application_run import ApplicationRun

    run = ApplicationRun(job_target_id=job.id)
    db_session.add(run)
    await db_session.commit()
    await db_session.refresh(run)

    assert run.status == RunStatus.QUEUED
    assert run.policy == RunPolicy.REVIEW_BEFORE_SUBMIT
    assert run.attempt_count == 0


@pytest.mark.asyncio
async def test_user_profile_list(db_session, truncate_tables) -> None:
    repo = UserProfileRepository(db_session)
    await repo.create(name="Ada", email="ada@example.com")
    await db_session.commit()

    rows = await repo.list_all()
    assert len(rows) == 1
    assert rows[0].name == "Ada"
