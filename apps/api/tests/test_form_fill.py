from __future__ import annotations

import os

import pytest
from httpx import ASGITransport, AsyncClient

from jober_api.main import app
from jober_api.models.enums import JobTargetStatus
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.repositories.user_profile import UserProfileRepository
from tests.fixtures.form_pages import load_form_fixture

pytestmark = [
    pytest.mark.skipif(
        os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
        reason="requires Postgres",
    ),
    pytest.mark.skipif(
        os.getenv("SKIP_PLAYWRIGHT") == "1",
        reason="playwright not installed",
    ),
]


@pytest.mark.asyncio
async def test_fill_single_step_fixture(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    jobs = JobTargetRepository(db_session)
    job = await jobs.create(company="Acme", role="Eng", status=JobTargetStatus.NEW)
    profiles = UserProfileRepository(db_session)
    await profiles.create(name="Ada Lovelace", email="ada@example.com", phone="555-0199")
    await db_session.commit()

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            discover = await client.post(
                f"/api/job-targets/{job.id}/discover-form",
                json={"fixture_html": load_form_fixture("single_step"), "platform": "greenhouse"},
            )
            assert discover.status_code == 200

            fill = await client.post(
                f"/api/job-targets/{job.id}/fill-form",
                json={"fixture_html": load_form_fixture("single_step")},
            )
            assert fill.status_code == 200, fill.text
            body = fill.json()
            assert "email" in body["filled"]
            assert "name" in body["filled"]
            assert body.get("fill_diffs")
            assert "email" in body["fill_diffs"]
            assert body["fill_diffs"]["email"]["matched"] is True
            email_row = next(i for i in body["items"] if i["field_key"] == "email")
            assert email_row["status"] == "filled"
            assert isinstance(email_row.get("evidence"), dict)
            assert "fill_diff" in (email_row["evidence"] or {})
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_fill_login_fixture_creates_checkpoint(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module
    from tests.fixtures.ats_pages import load_ats_fixture

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
                json={"fixture_html": load_form_fixture("single_step"), "platform": "greenhouse"},
            )
            assert discover.status_code == 200

            fill = await client.post(
                f"/api/job-targets/{job.id}/fill-form",
                json={"fixture_html": load_ats_fixture("login_gate")},
            )
            assert fill.status_code == 409
            assert fill.json()["detail"]["gate"] == "login"
    finally:
        app.dependency_overrides.clear()
