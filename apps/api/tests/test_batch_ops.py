from __future__ import annotations

import os
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from jober_api.config import settings
from jober_api.main import app
from jober_api.models.application_batch import ApplicationBatch
from jober_api.models.batch_item import BatchItem
from jober_api.models.enums import (
    BatchItemStatus,
    BatchStatus,
    JobTargetStatus,
    RunPolicy,
    RunStatus,
)
from jober_api.repositories.application_run import ApplicationRunRepository
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.services.batch import redis_control
from jober_api.services.batch.cost_governor import assert_generation_budget
from jober_api.services.batch.service import preview_batch
from jober_api.services.llm.gateway import BudgetExceededError

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres",
)


@pytest.fixture(autouse=True)
def _clear_redis_batch_keys() -> None:
    client = redis_control._client()
    for key in client.scan_iter("jober:batch:*"):
        client.delete(key)
    yield
    for key in client.scan_iter("jober:batch:*"):
        client.delete(key)


@pytest.mark.asyncio
async def test_preview_excludes_already_applied(db_session, truncate_tables) -> None:
    jobs = JobTargetRepository(db_session)
    await jobs.create(
        company="Done Co",
        role="Eng",
        status=JobTargetStatus.APPLIED,
        priority="A",
        direct_apply_url="http://fixtures.local/behaviors/single-step",
    )
    await jobs.create(
        company="Open Co",
        role="Eng",
        status=JobTargetStatus.NEW,
        priority="A",
        direct_apply_url="http://fixtures.local/behaviors/single-step",
    )
    await db_session.commit()
    preview = await preview_batch(db_session, {"priority": "A"})
    assert len(preview["included"]) == 1
    assert preview["excluded"][0]["reason"] == "already_applied"


@pytest.mark.asyncio
async def test_preview_excludes_prior_successful_run(db_session, truncate_tables) -> None:
    jobs = JobTargetRepository(db_session)
    job = await jobs.create(
        company="Win Co",
        role="Eng",
        status=JobTargetStatus.NEW,
        priority="A",
        direct_apply_url="http://fixtures.local/behaviors/single-step",
    )
    runs = ApplicationRunRepository(db_session)
    await runs.create(job_target_id=job.id, status=RunStatus.SUCCEEDED)
    await db_session.commit()
    preview = await preview_batch(db_session, {"priority": "A"})
    assert preview["included"] == []
    assert preview["excluded"][0]["reason"] == "prior_successful_run"


def test_domain_lock_serializes_same_domain() -> None:
    assert redis_control.try_acquire_domain_lock("boards.greenhouse.io", "item-a")
    assert not redis_control.try_acquire_domain_lock("boards.greenhouse.io", "item-b")
    redis_control.release_domain_lock("boards.greenhouse.io", "item-a")
    assert redis_control.try_acquire_domain_lock("boards.greenhouse.io", "item-b")


@pytest.mark.asyncio
async def test_orchestrator_defers_when_domain_locked(db_session, truncate_tables) -> None:
    pytest.importorskip("jober_worker.batch_orchestrator")
    from jober_worker.batch_orchestrator import run_orchestrator_tick

    jobs = JobTargetRepository(db_session)
    job = await jobs.create(
        company="Lock Co",
        role="Eng",
        status=JobTargetStatus.NEW,
        priority="A",
        direct_apply_url="https://boards.greenhouse.io/acme/jobs/1",
    )
    batch = ApplicationBatch(
        name="domain-lock test",
        status=BatchStatus.RUNNING,
        policy=RunPolicy.DRY_RUN,
        filters={},
    )
    db_session.add(batch)
    await db_session.flush()
    db_session.add(
        BatchItem(
            batch_id=batch.id,
            job_target_id=job.id,
            sort_order=0,
            status=BatchItemStatus.PENDING,
            domain="boards.greenhouse.io",
        )
    )
    await db_session.commit()

    assert redis_control.try_acquire_domain_lock("boards.greenhouse.io", "other-run")
    try:
        result = run_orchestrator_tick()
        assert result["status"] == "domain_locked"
        assert result["domain"] == "boards.greenhouse.io"
        assert result["holder"] == "other-run"
    finally:
        redis_control.release_domain_lock("boards.greenhouse.io", "other-run")


def test_cooldown_records_spacing() -> None:
    redis_control.record_domain_request("lever.co")
    waited = redis_control.wait_for_domain_cooldown("lever.co", cooldown_seconds=0.5)
    assert waited >= 0.0
    redis_control.record_domain_request("lever.co")
    waited_again = redis_control.wait_for_domain_cooldown("lever.co", cooldown_seconds=0.5)
    assert waited_again >= 0.4


@pytest.mark.asyncio
async def test_budget_hard_stop_blocks_generation(db_session, truncate_tables) -> None:
    with (
        patch.object(settings, "llm_monthly_budget_usd", 0.01),
        pytest.raises(BudgetExceededError, match="budget exceeded"),
    ):
        await assert_generation_budget(db_session, projected_cost=0.5)


@pytest.mark.asyncio
async def test_create_and_enqueue_batch(
    db_session, truncate_tables, fixture_server_url: str
) -> None:
    jobs = JobTargetRepository(db_session)
    base = fixture_server_url.rstrip("/")
    await jobs.create(
        company="Fixture Co",
        role="Eng",
        status=JobTargetStatus.NEW,
        priority="A",
        direct_apply_url=f"{base}/behaviors/single-step",
    )
    await db_session.commit()

    async def _override():
        yield db_session

    from jober_api.db import session as db_session_module

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            preview = await client.post(
                "/api/batches/preview",
                json={"filters": {"priority": "A"}},
            )
            assert preview.status_code == 200
            create = await client.post(
                "/api/batches",
                json={
                    "name": "Priority A fixtures",
                    "policy": "dry_run",
                    "filters": {"priority": "A"},
                    "site_cooldown_seconds": 0.1,
                },
            )
            assert create.status_code == 200, create.text
            batch_id = create.json()["id"]
            with patch(
                "jober_api.services.batch.celery_dispatch.dispatch_batch_tick",
                return_value="task-1",
            ):
                enqueue = await client.post(f"/api/batches/{batch_id}/enqueue", json={})
            assert enqueue.status_code == 200
            pause = await client.post("/api/queue/pause-all")
            assert pause.status_code == 200
            assert redis_control.is_globally_paused()
            resume = await client.post("/api/queue/resume-all")
            assert resume.status_code == 200
            assert not redis_control.is_globally_paused()
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_daily_plan_returns_summary(db_session, truncate_tables) -> None:
    jobs = JobTargetRepository(db_session)
    await jobs.create(
        company="Plan Co",
        role="Eng",
        status=JobTargetStatus.NEW,
        priority="A",
        direct_apply_url="http://fixtures.local/behaviors/single-step",
    )
    await db_session.commit()

    async def _override():
        yield db_session

    from jober_api.db import session as db_session_module

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get("/api/batches/daily-plan")
            assert res.status_code == 200
            body = res.json()
            assert "Priority A" in body["summary"]
            assert "domains" in body["summary"]
    finally:
        app.dependency_overrides.clear()
