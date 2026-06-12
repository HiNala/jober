"""Realistic-volume dataset for Mission 23 perf drills and load smoke tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.auth.constants import DEFAULT_DEV_TENANT_ID, DEFAULT_DEV_USER_ID
from jober_api.models.analytics import AnalyticsEvent
from jober_api.models.enums import JobTargetStatus, RunPolicy, RunStatus
from jober_api.repositories.application_run import ApplicationRunRepository
from jober_api.repositories.job_target import JobTargetRepository

DEFAULT_JOB_COUNT = 150
DEFAULT_RUN_COUNT = 50
DEFAULT_EVENT_COUNT = 10_000


async def seed_analytics_events(
    session: AsyncSession,
    *,
    event_count: int,
    tenant_id: uuid.UUID = DEFAULT_DEV_TENANT_ID,
    day: datetime | None = None,
) -> int:
    """Insert analytics events only (for rollup scaling drills)."""
    anchor = day or datetime.now(UTC)
    start = anchor.replace(hour=0, minute=0, second=0, microsecond=0)
    event_names = ("page.view", "feature.use", "signup.start", "run.open")
    pages = ("/", "/pricing", "/queue", "/library")
    for index in range(event_count):
        ts = start + timedelta(seconds=index % 86_400)
        session.add(
            AnalyticsEvent(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                ts=ts,
                session_id=f"perf-session-{index % 120:04d}",
                anon_id=f"perf-anon-{index % 400:04d}",
                user_id=DEFAULT_DEV_USER_ID if index % 5 == 0 else None,
                name=event_names[index % len(event_names)],
                page=pages[index % len(pages)],
                props={"index": index},
                source="client",
                is_bot=False,
                is_internal=False,
            )
        )
    await session.commit()
    return event_count


async def seed_perf_volume(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID = DEFAULT_DEV_TENANT_ID,
    job_count: int = DEFAULT_JOB_COUNT,
    run_count: int = DEFAULT_RUN_COUNT,
    event_count: int = DEFAULT_EVENT_COUNT,
    day: datetime | None = None,
) -> dict[str, Any]:
    """Seed job targets, runs, and analytics events for latency / rollup drills."""
    jobs = JobTargetRepository(session, tenant_id)
    runs = ApplicationRunRepository(session, tenant_id)
    statuses = [
        JobTargetStatus.NEW,
        JobTargetStatus.QUEUED,
        JobTargetStatus.APPLIED,
        JobTargetStatus.SKIPPED,
    ]
    priorities = ("A", "B", "C")

    created_jobs = []
    for index in range(job_count):
        row = await jobs.create(
            company=f"Perf Co {index % 40}",
            role=f"Engineer {index % 12}",
            status=statuses[index % len(statuses)],
            priority=priorities[index % len(priorities)],
            rank=index + 1,
            direct_apply_url=f"https://boards.greenhouse.io/perf-{index % 8}/jobs/{index}",
        )
        created_jobs.append(row)

    created_runs = []
    terminal = {RunStatus.SUCCEEDED, RunStatus.FAILED_FINAL, RunStatus.SKIPPED}
    active = [RunStatus.FILL_FORM, RunStatus.NEEDS_HUMAN, RunStatus.REVIEW_AND_SUBMIT]
    for index in range(min(run_count, len(created_jobs))):
        job = created_jobs[index]
        status = active[index % len(active)] if index % 3 else list(terminal)[index % len(terminal)]
        run = await runs.create(job_target_id=job.id, status=status, policy=RunPolicy.DRY_RUN)
        created_runs.append(run)

    await seed_analytics_events(
        session, event_count=event_count, tenant_id=tenant_id, day=day
    )
    return {
        "job_targets": len(created_jobs),
        "runs": len(created_runs),
        "analytics_events": event_count,
        "tenant_id": str(tenant_id),
    }
