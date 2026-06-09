from __future__ import annotations

import os
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from jober_api.auth.constants import DEFAULT_DEV_TENANT_ID
from jober_api.main import app
from jober_api.models.application_run import ApplicationRun
from jober_api.models.enums import JobTargetStatus, RunStatus
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.services.console.service import get_console_snapshot, patch_run_options

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres",
)


@pytest.mark.asyncio
async def test_patch_run_options_stores_generate_cover_letter(
    db_session,
    truncate_tables,
) -> None:
    jobs = JobTargetRepository(db_session, DEFAULT_DEV_TENANT_ID)
    job = await jobs.create(
        company="Co",
        role="Eng",
        status=JobTargetStatus.NEW,
        direct_apply_url="https://jobs.lever.co/co/eng",
    )
    run = ApplicationRun(
        id=uuid.uuid4(),
        tenant_id=DEFAULT_DEV_TENANT_ID,
        job_target_id=job.id,
        status=RunStatus.QUEUED,
    )
    db_session.add(run)
    await db_session.commit()

    result = await patch_run_options(
        db_session,
        run.id,
        DEFAULT_DEV_TENANT_ID,
        generate_cover_letter=False,
    )
    assert result["generate_cover_letter"] is False

    snapshot = await get_console_snapshot(db_session, run.id, DEFAULT_DEV_TENANT_ID)
    assert snapshot["run_options"]["generate_cover_letter"] is False


@pytest.mark.asyncio
async def test_run_options_api(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    jobs = JobTargetRepository(db_session, DEFAULT_DEV_TENANT_ID)
    job = await jobs.create(
        company="Co",
        role="Eng",
        status=JobTargetStatus.NEW,
    )
    run = ApplicationRun(
        id=uuid.uuid4(),
        tenant_id=DEFAULT_DEV_TENANT_ID,
        job_target_id=job.id,
        status=RunStatus.QUEUED,
    )
    db_session.add(run)
    await db_session.commit()

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.patch(
                f"/api/application-runs/{run.id}/run-options",
                json={"generate_cover_letter": True},
            )
            assert response.status_code == 200
            assert response.json()["generate_cover_letter"] is True
    finally:
        app.dependency_overrides.clear()
