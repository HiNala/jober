from __future__ import annotations

import json
import os
import uuid
import zipfile
from io import BytesIO

import pytest
from httpx import ASGITransport, AsyncClient

from jober_api.main import app
from jober_api.models.enums import CheckpointStatus, CheckpointType, JobTargetStatus, RunStatus
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.repositories.run_event import RunEventRepository
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
    job = await jobs.create(company="Giga", role="Founding Eng", status=JobTargetStatus.NEW)
    profiles = UserProfileRepository(db_session)
    await profiles.create(name="Ada Lovelace", email="ada@example.com", phone="555-0199")
    await db_session.commit()
    return job


@pytest.mark.asyncio
async def test_fill_streams_run_events_to_console(db_session, truncate_tables) -> None:
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

            fill = await client.post(
                f"/api/job-targets/{job.id}/fill-form",
                json={"fixture_html": fixture},
            )
            assert fill.status_code == 200, fill.text
            run_id = fill.json()["run_id"]

            console = await client.get(f"/api/application-runs/{run_id}/console")
            assert console.status_code == 200
            body = console.json()
            assert body["company"] == "Giga"
            event_types = {event["event_type"] for event in body["events"]}
            assert "run.started" in event_types
            assert "field.filled" in event_types
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_sse_reconnect_replays_after_seq(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module
    from jober_api.repositories.application_run import ApplicationRunRepository

    job = await _seed_job(db_session)
    runs = ApplicationRunRepository(db_session)
    run = await runs.create(
        job_target_id=job.id,
        status=RunStatus.FILL_FORM,
        current_step=RunStatus.FILL_FORM,
    )
    events = RunEventRepository(db_session)
    await events.append(run_id=run.id, event_type="run.started", message="one")
    await events.append(run_id=run.id, event_type="state.changed", message="two")
    await db_session.commit()

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            snap = await client.get(f"/api/application-runs/{run.id}/console")
            assert snap.json()["last_event_seq"] == 2

            await events.append(run_id=run.id, event_type="field.filled", message="three")
            await db_session.commit()

            res = await client.get(
                f"/api/application-runs/{run.id}/events",
                headers={"Accept": "text/event-stream"},
                params={"after_seq": 2, "poll_once": "1"},
            )
            assert res.status_code == 200
            chunks = res.text
            assert "field.filled" in chunks
            assert "id: 3" in chunks
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_sse_stream_includes_retry_and_caps_burst(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module
    from jober_api.repositories.application_run import ApplicationRunRepository

    job = await _seed_job(db_session)
    runs = ApplicationRunRepository(db_session)
    run = await runs.create(
        job_target_id=job.id,
        status=RunStatus.FILL_FORM,
        current_step=RunStatus.FILL_FORM,
    )
    events = RunEventRepository(db_session)
    for index in range(55):
        await events.append(
            run_id=run.id,
            event_type="field.filled",
            message=f"field {index}",
        )
    await db_session.commit()

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get(
                f"/api/application-runs/{run.id}/events",
                headers={"Accept": "text/event-stream"},
                params={"after_seq": 0, "poll_once": "1"},
            )
            assert res.status_code == 200
            assert "retry: 3000" in res.text
            data_lines = [line for line in res.text.splitlines() if line.startswith("data: ")]
            assert len(data_lines) <= 50
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_checkpoint_resolve_from_api(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module
    from jober_api.models.human_checkpoint import HumanCheckpoint
    from jober_api.repositories.application_run import ApplicationRunRepository

    job = await _seed_job(db_session)
    runs = ApplicationRunRepository(db_session)
    run = await runs.create(
        job_target_id=job.id,
        status=RunStatus.REVIEW_AND_SUBMIT,
        current_step=RunStatus.REVIEW_AND_SUBMIT,
    )
    cp = HumanCheckpoint(
        id=uuid.uuid4(),
        run_id=run.id,
        checkpoint_type=CheckpointType.REVIEW_SUBMIT,
        prompt="Review",
        options={"readiness": {"passed": True, "checks": []}},
        status=CheckpointStatus.OPEN,
    )
    db_session.add(cp)
    await db_session.commit()

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            denied = await client.post(
                f"/api/application-runs/{run.id}/checkpoints/{cp.id}/resolve",
                json={"action": "deny"},
            )
            assert denied.status_code == 200
            assert denied.json()["run_status"] == RunStatus.NEEDS_HUMAN.value

            console = await client.get(f"/api/application-runs/{run.id}/console")
            assert console.status_code == 200
            assert console.json()["open_checkpoint"] is None
            assert console.json()["status"] == RunStatus.NEEDS_HUMAN.value
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_checkpoint_skip_syncs_console_snapshot(db_session, truncate_tables) -> None:
    """Web and TUI share resolve API — skip must clear open_checkpoint in console snapshot."""
    from jober_api.db import session as db_session_module
    from jober_api.models.human_checkpoint import HumanCheckpoint
    from jober_api.repositories.application_run import ApplicationRunRepository

    job = await _seed_job(db_session)
    runs = ApplicationRunRepository(db_session)
    run = await runs.create(
        job_target_id=job.id,
        status=RunStatus.REVIEW_AND_SUBMIT,
        current_step=RunStatus.REVIEW_AND_SUBMIT,
    )
    cp = HumanCheckpoint(
        id=uuid.uuid4(),
        run_id=run.id,
        checkpoint_type=CheckpointType.REVIEW_SUBMIT,
        prompt="Review",
        options={"readiness": {"passed": True, "checks": []}},
        status=CheckpointStatus.OPEN,
    )
    db_session.add(cp)
    await db_session.commit()

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            before = await client.get(f"/api/application-runs/{run.id}/console")
            assert before.json()["open_checkpoint"]["id"] == str(cp.id)

            skipped = await client.post(
                f"/api/application-runs/{run.id}/checkpoints/{cp.id}/resolve",
                json={"action": "skip"},
            )
            assert skipped.status_code == 200
            assert skipped.json()["run_status"] == RunStatus.SKIPPED.value

            after = await client.get(f"/api/application-runs/{run.id}/console")
            assert after.json()["open_checkpoint"] is None
            assert after.json()["status"] == RunStatus.SKIPPED.value
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_recent_events_feed(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module
    from jober_api.repositories.application_run import ApplicationRunRepository
    from jober_api.repositories.run_event import RunEventRepository

    job = await _seed_job(db_session)
    runs = ApplicationRunRepository(db_session)
    run = await runs.create(
        job_target_id=job.id,
        status=RunStatus.FILL_FORM,
        current_step=RunStatus.FILL_FORM,
    )
    events = RunEventRepository(db_session)
    await events.append(run_id=run.id, event_type="run.started", message="started")
    await db_session.commit()

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            recent = await client.get("/api/console/recent-events")
            assert recent.status_code == 200
            items = recent.json()["items"]
            assert any(item["event_type"] == "run.started" for item in items)
            assert items[0]["company"] == "Giga"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_trace_artifact_zip_valid(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module
    from jober_api.repositories.application_run import ApplicationRunRepository
    from jober_api.storage.keys import run_attempt_trace_key
    from jober_api.storage.minio_client import ObjectStorage

    job = await _seed_job(db_session)
    runs = ApplicationRunRepository(db_session)
    run = await runs.create(
        job_target_id=job.id,
        status=RunStatus.FILL_FORM,
        current_step=RunStatus.FILL_FORM,
        attempt_count=1,
    )
    from jober_api.models.application_attempt import ApplicationAttempt
    from jober_api.models.enums import AttemptStatus

    key = run_attempt_trace_key(run.id, 1)
    db_session.add(
        ApplicationAttempt(
            run_id=run.id,
            attempt_index=1,
            status=AttemptStatus.SUCCEEDED,
            trace_object_key=key,
        )
    )
    await db_session.flush()
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("trace.trace", json.dumps({"version": 8}))
    storage = ObjectStorage()
    await storage.put_object(key, buffer.getvalue(), content_type="application/zip")

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            console = await client.get(f"/api/application-runs/{run.id}/console")
            assert console.status_code == 200
            artifacts = console.json()["artifacts"]
            assert artifacts
            trace_url = artifacts[0]["trace_url"]
            assert trace_url
            raw = await storage.get_bytes(key)
            assert zipfile.is_zipfile(BytesIO(raw))
    finally:
        app.dependency_overrides.clear()
