"""Lightweight concurrent load smoke — hot read paths under parallel traffic."""

from __future__ import annotations

import asyncio
import os
import re
import time
import uuid
from datetime import UTC, date, datetime
from datetime import time as dt_time

import pytest
from httpx import ASGITransport, AsyncClient

from jober_api.main import app
from jober_api.models.enums import JobTargetStatus, RunStatus
from jober_api.repositories.application_run import ApplicationRunRepository
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.repositories.run_event import RunEventRepository
from jober_api.services.analytics.rollups import rollup_analytics_day
from jober_api.services.console.service import stream_run_events
from jober_api.services.dev.perf_volume import seed_analytics_events, seed_perf_volume

pytestmark = [
    pytest.mark.load,
    pytest.mark.skipif(
        os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
        reason="requires Postgres",
    ),
]

_LIST_P95_SEC = 0.3
_DASHBOARD_P95_SEC = 0.5
_ROLLUP_10K_MAX_SEC = 8.0
_ROLLUP_2K_MAX_SEC = 2.0


def _percentile(samples: list[float], pct: float) -> float:
    if not samples:
        return 0.0
    ordered = sorted(samples)
    index = min(len(ordered) - 1, int(len(ordered) * pct))
    return ordered[index]


async def _timed_get(client: AsyncClient, path: str, **kwargs: object) -> float:
    start = time.perf_counter()
    response = await client.get(path, **kwargs)
    elapsed = time.perf_counter() - start
    assert response.status_code == 200, response.text
    return elapsed


def _session_override(db_session):
    from jober_api.db import session as db_session_module

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override


def _clear_overrides() -> None:
    app.dependency_overrides.clear()


def _parse_sse_seqs(chunks: list[str]) -> set[int]:
    body = "".join(chunks)
    return {int(match) for match in re.findall(r'"seq":\s*(\d+)', body)}


@pytest.mark.asyncio
async def test_hot_read_paths_under_concurrent_load(
    db_session, truncate_tables, auth_headers
) -> None:
    _session_override(db_session)
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            health_elapsed = await asyncio.gather(
                *[_timed_get(client, "/healthz") for _ in range(20)]
            )
            dash_elapsed = await _timed_get(
                client, "/api/dashboard/summary", headers=auth_headers
            )
            analytics_elapsed = await _timed_get(
                client, "/api/analytics/me", headers=auth_headers
            )
            elapsed = [*health_elapsed, dash_elapsed, analytics_elapsed]
        assert max(elapsed) < 3.0, f"slowest request {max(elapsed):.2f}s"
    finally:
        _clear_overrides()


@pytest.mark.asyncio
async def test_hot_paths_at_perf_volume(
    db_session, truncate_tables, auth_headers
) -> None:
    stats = await seed_perf_volume(db_session)
    assert stats["job_targets"] >= 150
    assert stats["analytics_events"] >= 10_000

    _session_override(db_session)
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            list_samples = [
                await _timed_get(
                    client,
                    "/api/job-targets?priority=A&limit=100",
                    headers=auth_headers,
                )
                for _ in range(5)
            ]
            dash_samples = [
                await _timed_get(client, "/api/dashboard/summary", headers=auth_headers)
                for _ in range(5)
            ]
            jobs = JobTargetRepository(db_session)
            job = (await jobs.list_filtered(limit=1))[0]
            runs = ApplicationRunRepository(db_session)
            run = await runs.create(job_target_id=job.id, status=RunStatus.FILL_FORM)
            await db_session.commit()
            console_samples = [
                await _timed_get(
                    client,
                    f"/api/application-runs/{run.id}/console",
                    headers=auth_headers,
                )
                for _ in range(3)
            ]
            preview_samples: list[float] = []
            for _ in range(3):
                start = time.perf_counter()
                preview = await client.post(
                    "/api/batches/preview",
                    json={"filters": {"priority": "A"}},
                    headers=auth_headers,
                )
                preview_samples.append(time.perf_counter() - start)
                assert preview.status_code == 200
            preview_p95 = _percentile(preview_samples, 0.95)
            assert preview_p95 < _LIST_P95_SEC * 2

        list_p95 = _percentile(list_samples, 0.95)
        dash_p95 = _percentile(dash_samples, 0.95)
        console_p95 = _percentile(console_samples, 0.95)
        assert list_p95 < _LIST_P95_SEC, f"job-targets p95 {list_p95:.3f}s"
        assert dash_p95 < _DASHBOARD_P95_SEC, f"dashboard p95 {dash_p95:.3f}s"
        assert console_p95 < _LIST_P95_SEC, f"console p95 {console_p95:.3f}s"
    finally:
        _clear_overrides()


@pytest.mark.asyncio
async def test_dashboard_queue_depth_uses_sql_count(
    db_session, truncate_tables, auth_headers
) -> None:
    jobs = JobTargetRepository(db_session)
    for index in range(30):
        await jobs.create(
            company=f"Dash {index}",
            role="Eng",
            priority="A",
            status=JobTargetStatus.NEW,
        )
    await db_session.commit()

    _session_override(db_session)
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/dashboard/summary", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["queue_depth_priority_a"] == 30
    finally:
        _clear_overrides()


@pytest.mark.asyncio
async def test_analytics_rollup_scales_linearly(db_session, truncate_tables) -> None:
    small_day = date(2026, 6, 1)
    large_day = date(2026, 6, 2)
    await seed_analytics_events(
        db_session,
        event_count=2_000,
        day=datetime.combine(small_day, dt_time.min, tzinfo=UTC),
    )
    start = time.perf_counter()
    small = await rollup_analytics_day(db_session, small_day)
    small_elapsed = time.perf_counter() - start
    assert small["events_processed"] == 2_000

    await seed_analytics_events(
        db_session,
        event_count=10_000,
        day=datetime.combine(large_day, dt_time.min, tzinfo=UTC),
    )
    start = time.perf_counter()
    large = await rollup_analytics_day(db_session, large_day)
    large_elapsed = time.perf_counter() - start
    assert large["events_processed"] == 10_000

    assert small_elapsed < _ROLLUP_2K_MAX_SEC
    assert large_elapsed < _ROLLUP_10K_MAX_SEC
    ratio = large_elapsed / max(small_elapsed, 0.001)
    assert ratio < 8.0, f"rollup super-linear ratio {ratio:.1f}x"


@pytest.mark.asyncio
async def test_sse_fanout_no_event_loss(db_session, truncate_tables) -> None:
    from contextlib import asynccontextmanager

    jobs = JobTargetRepository(db_session)
    job = await jobs.create(company="SSE Co", role="Eng")
    runs = ApplicationRunRepository(db_session)
    run = await runs.create(job_target_id=job.id, status=RunStatus.FILL_FORM)
    events = RunEventRepository(db_session)
    for index in range(30):
        await events.append(
            run_id=run.id,
            event_type="field.filled",
            message=f"field {index}",
        )
    await db_session.commit()

    def session_factory():
        @asynccontextmanager
        async def _provide():
            yield db_session

        return _provide()

    async def _consume() -> set[int]:
        chunks: list[str] = []
        async for chunk in stream_run_events(
            session_factory, run.id, after_seq=0, poll_once=True
        ):
            chunks.append(chunk)
        return _parse_sse_seqs(chunks)

    results = await asyncio.gather(*[_consume() for _ in range(10)])
    expected = set(range(1, 31))
    for index, seqs in enumerate(results):
        assert seqs == expected, f"consumer {index} lost events: {expected - seqs}"


@pytest.mark.asyncio
async def test_domain_lock_serializes_same_host(db_session, truncate_tables) -> None:
    from jober_api.services.batch import redis_control

    domain = f"perf-lock-{uuid.uuid4().hex[:8]}.greenhouse.io"
    assert redis_control.try_acquire_domain_lock(domain, "holder-a")
    try:
        assert not redis_control.try_acquire_domain_lock(domain, "holder-b")
    finally:
        redis_control.release_domain_lock(domain, "holder-a")
    assert redis_control.try_acquire_domain_lock(domain, "holder-b")
