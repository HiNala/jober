from __future__ import annotations

import os

import pytest

from jober_api.models.enums import CheckpointStatus, CheckpointType, JobTargetStatus, RunStatus
from jober_api.models.human_checkpoint import HumanCheckpoint
from jober_api.repositories.application_run import ApplicationRunRepository
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.services.console.service import resolve_checkpoint

pytestmark = [
    pytest.mark.policy,
    pytest.mark.skipif(
        os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
        reason="requires Postgres",
    ),
]


@pytest.mark.asyncio
async def test_checkpoint_resolved_value_scrubbed(db_session, truncate_tables) -> None:
    jobs = JobTargetRepository(db_session)
    job = await jobs.create(
        company="Gate Co",
        role="Eng",
        status=JobTargetStatus.NEW,
        priority="A",
    )
    runs = ApplicationRunRepository(db_session)
    run = await runs.create(job_target_id=job.id, status=RunStatus.NEEDS_HUMAN)
    cp = HumanCheckpoint(
        run_id=run.id,
        checkpoint_type=CheckpointType.LOGIN,
        prompt="Please log in",
        status=CheckpointStatus.OPEN,
    )
    db_session.add(cp)
    await db_session.commit()
    await db_session.refresh(cp)

    secret = "sk-test-secret-key-abcdefghijklmnop"
    await resolve_checkpoint(
        db_session,
        run_id=run.id,
        checkpoint_id=cp.id,
        action="approve",
        value=f"notes with {secret} and nalamaui30@gmail.com",
    )

    await db_session.refresh(cp)
    assert cp.resolved_value is not None
    assert secret not in cp.resolved_value
    assert "nalamaui30@gmail.com" not in cp.resolved_value
