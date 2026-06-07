from __future__ import annotations

import os

import pytest
from httpx import ASGITransport, AsyncClient

from jober_api.main import app
from jober_api.models.enums import JobTargetStatus
from jober_api.repositories.job_target import JobTargetRepository
from tests.fixtures.form_pages import load_form_fixture

pytestmark = [
    pytest.mark.policy,
    pytest.mark.skipif(
        os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
        reason="requires Postgres",
    ),
]


@pytest.mark.asyncio
async def test_fill_sensitive_eeo_fixture_needs_human(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    jobs = JobTargetRepository(db_session)
    job = await jobs.create(company="Acme", role="Eng", status=JobTargetStatus.NEW)
    await db_session.commit()

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            discover = await client.post(
                f"/api/job-targets/{job.id}/discover-form",
                json={"fixture_html": load_form_fixture("sensitive_eeo"), "platform": "greenhouse"},
            )
            assert discover.status_code == 200

            fill = await client.post(
                f"/api/job-targets/{job.id}/fill-form",
                json={"fixture_html": load_form_fixture("sensitive_eeo")},
            )
            assert fill.status_code == 409
            assert fill.json()["detail"]["gate"] == "sensitive_field"
    finally:
        app.dependency_overrides.clear()
