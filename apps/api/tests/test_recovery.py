from __future__ import annotations

import os
import uuid
from datetime import UTC, datetime

import pytest
from httpx import ASGITransport, AsyncClient

from jober_api.main import app
from jober_api.models.enums import JobTargetStatus, RunStatus
from jober_api.models.failure_event import FailureEvent
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
async def test_selector_failure_recovers_on_label_attempt(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    job = await _seed_job(db_session)
    fixture = load_form_fixture("single_step")

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

            result = await client.post(
                f"/api/job-targets/{job.id}/recovery-fill",
                json={"fixture_html": fixture, "platform": "greenhouse"},
            )
            assert result.status_code == 200, result.text
            body = result.json()
            assert body["status"] == "succeeded"
            assert body["attempt_count"] == 2
            assert "email" in body["filled"]

            from jober_api.repositories.field_mapping_memory import FieldMappingMemoryRepository

            memory = FieldMappingMemoryRepository(db_session)
            mapped = await memory.lookup("greenhouse", "Email address")
            assert mapped == "email"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_unrecoverable_failure_produces_report(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    job = await _seed_job(db_session)
    fixture = load_form_fixture("single_step")

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

            result = await client.post(
                f"/api/job-targets/{job.id}/recovery-fill",
                json={"fixture_html": fixture, "platform": "greenhouse", "force_brittle": True},
            )
            assert result.status_code == 200
            body = result.json()
            assert body["status"] == RunStatus.FAILED_FINAL.value
            report = body["failure_report"]
            assert report["failure_class"] == "selector"
            assert report["recommended_manual_action"]
            assert report["attempt_count"] == 4
            assert len(report["self_assessments"]) == 4

            detail = await client.get(f"/api/application-runs/{body['run_id']}/failure-report")
            assert detail.status_code == 200
            assert detail.json()["company"] == "Acme"

            by_job = await client.get(f"/api/job-targets/{job.id}/failure-report")
            assert by_job.status_code == 200
            assert by_job.json()["safe_to_retry"] is True
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_resume_from_checkpoint(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module
    from jober_api.repositories.application_run import ApplicationRunRepository

    job = await _seed_job(db_session)
    runs = ApplicationRunRepository(db_session)
    run = await runs.create(
        job_target_id=job.id,
        status=RunStatus.FILL_FORM,
        current_step=RunStatus.FILL_FORM,
    )
    run.checkpoint_data = {"step": "fill_form", "filled_fields": ["email"]}
    run.attempt_count = 1
    await db_session.commit()

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resume = await client.post(f"/api/application-runs/{run.id}/resume")
            assert resume.status_code == 200
            body = resume.json()
            assert body["attempt_index"] == 2
            assert body["checkpoint"]["filled_fields"] == ["email"]
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_circuit_breaker_trips_in_analytics(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    job = await _seed_job(db_session)
    now = datetime.now(UTC)
    for _ in range(5):
        db_session.add(
            FailureEvent(
                id=uuid.uuid4(),
                job_target_id=job.id,
                run_id=None,
                platform="workday",
                failure_class="selector",
                created_at=now,
            )
        )
    await db_session.commit()

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            analytics = await client.get("/api/recovery/failure-analytics")
            assert analytics.status_code == 200
            body = analytics.json()
            assert any(b["circuit_tripped"] for b in body["buckets"])
            assert body["alerts"]
    finally:
        app.dependency_overrides.clear()
