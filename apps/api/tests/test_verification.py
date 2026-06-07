from __future__ import annotations

import os
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from jober_api.main import app
from jober_api.models.application_run import ApplicationRun
from jober_api.models.enums import JobTargetStatus, RunStatus
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


async def _seed_job(db_session):
    jobs = JobTargetRepository(db_session)
    job = await jobs.create(company="Acme", role="Engineer", status=JobTargetStatus.NEW)
    profiles = UserProfileRepository(db_session)
    await profiles.create(name="Ada Lovelace", email="ada@example.com", phone="555-0199")
    await db_session.commit()
    return job


@pytest.mark.asyncio
async def test_verify_ready_fails_on_missing_required(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    job = await _seed_job(db_session)

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            discover = await client.post(
                f"/api/job-targets/{job.id}/discover-form",
                json={
                    "fixture_html": load_form_fixture("required_validation"),
                    "platform": "greenhouse",
                },
            )
            assert discover.status_code == 200

            verify = await client.post(
                f"/api/job-targets/{job.id}/verify-ready",
                json={
                    "fixture_html": load_form_fixture("required_validation"),
                    "refilled": False,
                },
            )
            assert verify.status_code == 409
            detail = verify.json()["detail"]
            assert detail["reason"] == "readiness_failed"
            assert detail["readiness"]["passed"] is False
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_verify_and_submit_complete_fixture(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    job = await _seed_job(db_session)
    job_id = job.id
    fixture = load_form_fixture("submit_success")

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            discover = await client.post(
                f"/api/job-targets/{job_id}/discover-form",
                json={"fixture_html": fixture, "platform": "greenhouse"},
            )
            assert discover.status_code == 200

            verify = await client.post(
                f"/api/job-targets/{job_id}/verify-ready",
                json={"fixture_html": fixture},
            )
            assert verify.status_code == 200, verify.text
            body = verify.json()
            assert body["status"] == RunStatus.REVIEW_AND_SUBMIT.value
            assert body["readiness"]["passed"] is True
            assert body["human_summary"]
            run_id = body["run_id"]

            review = await client.get(f"/api/application-runs/{run_id}/review")
            assert review.status_code == 200
            review_body = review.json()
            assert review_body["human_summary"]
            assert review_body["readiness"]["passed"] is True

            submit = await client.post(
                f"/api/application-runs/{run_id}/submit",
                json={"fixture_html": fixture},
            )
            assert submit.status_code == 200, submit.text
            submit_body = submit.json()
            assert submit_body["outcome"] == "success"
            assert submit_body["confirmation_text"]
            assert submit_body["job_target_status"] == JobTargetStatus.APPLIED.value

            db_session.expire_all()
            job_row = await JobTargetRepository(db_session).get(job_id)
            assert job_row is not None
            assert job_row.status == JobTargetStatus.APPLIED
            assert job_row.applied_date is not None
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_already_applied_detected_without_submit(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    job = await _seed_job(db_session)
    fixture = load_form_fixture("already_applied")

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            discover = await client.post(
                f"/api/job-targets/{job.id}/discover-form",
                json={"fixture_html": fixture, "platform": "greenhouse"},
            )
            assert discover.status_code == 200

            verify = await client.post(
                f"/api/job-targets/{job.id}/verify-ready",
                json={"fixture_html": fixture},
            )
            assert verify.status_code == 200
            assert verify.json()["gate"] == "already_applied"
            assert verify.json()["status"] == RunStatus.SKIPPED.value
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_fill_then_verify_reuses_fill_run(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    job = await _seed_job(db_session)
    job_id = job.id
    fixture = load_form_fixture("single_step")

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            discover = await client.post(
                f"/api/job-targets/{job_id}/discover-form",
                json={"fixture_html": fixture, "platform": "greenhouse"},
            )
            assert discover.status_code == 200

            fill = await client.post(
                f"/api/job-targets/{job_id}/fill-form",
                json={"fixture_html": fixture},
            )
            assert fill.status_code == 200
            fill_run_id = fill.json()["run_id"]

            verify = await client.post(
                f"/api/job-targets/{job_id}/verify-ready",
                json={"fixture_html": fixture},
            )
            assert verify.status_code == 200, verify.text
            assert verify.json()["run_id"] == fill_run_id

            review = await client.get(f"/api/application-runs/{fill_run_id}/review")
            assert review.status_code == 200
            diffs = review.json()["fill_diffs"]
            assert any(d["field_key"] == "email" for d in diffs)
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.policy
async def test_auto_submit_requires_explicit_opt_in(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    job = await _seed_job(db_session)

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/job-targets/{job.id}/verify-ready",
                json={
                    "fixture_html": load_form_fixture("submit_success"),
                    "policy": "auto_submit",
                },
            )
            assert response.status_code == 422
            assert "opt-in" in response.json()["detail"].lower()
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_uncertain_submission_needs_human_verification(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    job = await _seed_job(db_session)
    fixture = load_form_fixture("uncertain_confirmation")

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            discover = await client.post(
                f"/api/job-targets/{job.id}/discover-form",
                json={"fixture_html": fixture, "platform": "greenhouse"},
            )
            assert discover.status_code == 200

            verify = await client.post(
                f"/api/job-targets/{job.id}/verify-ready",
                json={"fixture_html": fixture},
            )
            assert verify.status_code == 200
            run_id = verify.json()["run_id"]

            submit = await client.post(
                f"/api/application-runs/{run_id}/submit",
                json={"fixture_html": fixture},
            )
            assert submit.status_code == 200
            assert submit.json()["outcome"] == "uncertain"

            db_session.expire_all()
            run = await db_session.get(ApplicationRun, uuid.UUID(run_id))
            assert run is not None
            assert run.status == RunStatus.VERIFY_SUBMISSION
    finally:
        app.dependency_overrides.clear()
