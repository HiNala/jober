"""Hot-path index presence and planner hints (Mission 20)."""

from __future__ import annotations

import os

import pytest
from sqlalchemy import text

from jober_api.auth.constants import DEFAULT_DEV_TENANT_ID
from jober_api.models.enums import JobTargetStatus, RunStatus
from jober_api.repositories.application_run import ApplicationRunRepository
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.repositories.run_event import RunEventRepository

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres with migrations applied",
)

_EXPECTED_INDEXES = (
    ("job_targets", "ix_job_targets_tenant_status"),
    ("application_runs", "ix_application_runs_tenant_status"),
    ("run_events", "ix_run_events_run_id_seq"),
    ("analytics_events", "ix_analytics_events_tenant_ts"),
    ("batch_items", "ix_batch_items_batch_status"),
)


@pytest.mark.asyncio
@pytest.mark.parametrize("table,index_name", _EXPECTED_INDEXES)
async def test_hot_path_index_exists(raw_connection, table: str, index_name: str) -> None:
    result = await raw_connection.execute(
        text(
            "SELECT 1 FROM pg_indexes "
            "WHERE schemaname = 'public' AND tablename = :table AND indexname = :index"
        ),
        {"table": table, "index": index_name},
    )
    assert result.scalar() == 1


@pytest.mark.asyncio
async def test_job_targets_tenant_status_uses_index_scan(
    db_session,
    truncate_tables,
    raw_connection,
) -> None:
    """Composite index should plan once tenant cardinality exceeds a trivial single row."""
    jobs = JobTargetRepository(db_session, DEFAULT_DEV_TENANT_ID)
    for i in range(40):
        await jobs.create(
            company=f"Noise {i}",
            role="Eng",
            status=JobTargetStatus.APPLIED,
        )
    await jobs.create(company="Idx Co", role="Eng", status=JobTargetStatus.NEW)
    await db_session.commit()
    await raw_connection.execute(text("ANALYZE job_targets"))

    tenant_id = DEFAULT_DEV_TENANT_ID
    status = JobTargetStatus.NEW.value
    await raw_connection.execute(text("SET LOCAL enable_seqscan = off"))
    plan = await raw_connection.execute(
        text(
            "EXPLAIN SELECT id FROM job_targets "
            "WHERE tenant_id = :tenant_id AND status = :status LIMIT 50"
        ),
        {"tenant_id": str(tenant_id), "status": status},
    )
    lines = "\n".join(row[0] for row in plan.fetchall())
    assert "Index Scan" in lines or "Bitmap Index Scan" in lines
    assert "Seq Scan" not in lines
    assert (
        "ix_job_targets_tenant_status" in lines
        or "ix_job_targets_tenant_id" in lines
    )


@pytest.mark.asyncio
async def test_run_events_seq_lookup_uses_index(
    db_session,
    truncate_tables,
    raw_connection,
) -> None:
    jobs = JobTargetRepository(db_session)
    job = await jobs.create(company="SSE Co", role="Eng")
    runs = ApplicationRunRepository(db_session)
    run = await runs.create(job_target_id=job.id, status=RunStatus.FILL_FORM)
    events = RunEventRepository(db_session)
    await events.append(run_id=run.id, event_type="run.started", message="ok")
    await db_session.commit()

    await raw_connection.execute(text("SET LOCAL enable_seqscan = off"))
    plan = await raw_connection.execute(
        text(
            "EXPLAIN SELECT id FROM run_events WHERE run_id = :run_id AND seq > 0 ORDER BY seq"
        ),
        {"run_id": str(run.id)},
    )
    lines = "\n".join(row[0] for row in plan.fetchall())
    assert "ix_run_events_run_id_seq" in lines
