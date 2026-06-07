from __future__ import annotations

import os

import pytest
from httpx import ASGITransport, AsyncClient

from jober_api.main import app
from jober_api.models.enums import JobTargetStatus, RunStatus
from jober_api.repositories.application_run import ApplicationRunRepository
from jober_api.repositories.job_target import JobTargetRepository

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres",
)


@pytest.mark.asyncio
async def test_purge_run_and_export_all(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    jobs = JobTargetRepository(db_session)
    job = await jobs.create(
        company="Retain Co",
        role="Eng",
        status=JobTargetStatus.NEW,
        priority="A",
    )
    runs = ApplicationRunRepository(db_session)
    run = await runs.create(job_target_id=job.id, status=RunStatus.SUCCEEDED)
    await db_session.commit()

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            export_res = await client.get("/api/privacy/export-all")
            assert export_res.status_code == 200
            body = export_res.json()
            assert len(body["job_targets"]) == 1
            assert len(body["application_runs"]) == 1

            purge = await client.post(f"/api/privacy/runs/{run.id}/purge")
            assert purge.status_code == 200
            assert purge.json()["status"] == "purged"

            export_after = await client.get("/api/privacy/export-all")
            assert export_after.json()["application_runs"] == []
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_delete_all_requires_confirmation_phrase(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            bad = await client.request(
                "DELETE",
                "/api/privacy/delete-all",
                json={"confirm": "wrong phrase"},
            )
            assert bad.status_code == 400

            ok = await client.request(
                "DELETE",
                "/api/privacy/delete-all",
                json={"confirm": "DELETE ALL MY DATA"},
            )
            assert ok.status_code == 200
            assert ok.json()["status"] == "deleted"
    finally:
        app.dependency_overrides.clear()
