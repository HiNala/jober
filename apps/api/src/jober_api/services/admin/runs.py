from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.application_run import ApplicationRun
from jober_api.models.enums import RunStatus
from jober_api.models.failure_event import FailureEvent
from jober_api.services.analytics.dashboard import resolve_date_range


async def get_admin_runs_summary(
    session: AsyncSession,
    *,
    start: datetime | None = None,
    end: datetime | None = None,
) -> dict[str, Any]:
    """Product-wide run reliability aggregates — no per-tenant private content."""
    end_date = (end or datetime.now(UTC)).date()
    start_date = (start.date() if start else end_date - timedelta(days=29))
    start_date, end_date = resolve_date_range(start_date, end_date)
    start_dt = datetime.combine(start_date, datetime.min.time(), tzinfo=UTC)
    end_dt = datetime.combine(end_date + timedelta(days=1), datetime.min.time(), tzinfo=UTC)

    status_stmt = (
        select(ApplicationRun.status, func.count())
        .where(ApplicationRun.created_at >= start_dt, ApplicationRun.created_at < end_dt)
        .group_by(ApplicationRun.status)
    )
    by_status = {
        row[0].value if hasattr(row[0], "value") else str(row[0]): int(row[1])
        for row in (await session.execute(status_stmt)).all()
    }

    failure_stmt = (
        select(
            FailureEvent.platform,
            FailureEvent.failure_class,
            func.count(),
        )
        .where(FailureEvent.created_at >= start_dt, FailureEvent.created_at < end_dt)
        .group_by(FailureEvent.platform, FailureEvent.failure_class)
        .order_by(func.count().desc())
        .limit(50)
    )
    failures = [
        {
            "platform": row.platform,
            "failure_class": row.failure_class,
            "count": int(row[2]),
        }
        for row in (await session.execute(failure_stmt)).all()
    ]

    needs_human = int(
        (
            await session.execute(
                select(func.count())
                .select_from(ApplicationRun)
                .where(ApplicationRun.status == RunStatus.NEEDS_HUMAN)
            )
        ).scalar_one()
    )

    total = sum(by_status.values())
    succeeded = by_status.get(RunStatus.SUCCEEDED.value, 0)
    failed = by_status.get(RunStatus.FAILED_FINAL.value, 0) + by_status.get(
        RunStatus.FAILED_RETRYABLE.value, 0
    )
    retryable = by_status.get(RunStatus.FAILED_RETRYABLE.value, 0)
    recovery_rate = round(succeeded / max(succeeded + failed, 1), 4)

    return {
        "range": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "totals": {
            "runs": total,
            "succeeded": succeeded,
            "failed": failed,
            "retryable": retryable,
            "needs_human_backlog": needs_human,
            "recovery_rate": recovery_rate,
        },
        "by_status": by_status,
        "failures_by_platform": failures,
        "attention": _runs_attention(needs_human, failures, recovery_rate),
    }


def _runs_attention(
    needs_human: int,
    failures: list[dict[str, Any]],
    recovery_rate: float,
) -> list[dict[str, str]]:
    notes: list[dict[str, str]] = []
    if needs_human > 0:
        notes.append(
            {
                "level": "warn",
                "message": f"{needs_human} run(s) waiting for human action.",
            }
        )
    if failures:
        top = failures[0]
        notes.append(
            {
                "level": "info",
                "message": (
                    f"Top failure: {top['platform']} / {top['failure_class']} "
                    f"({top['count']} in range)."
                ),
            }
        )
    if recovery_rate < 0.5 and recovery_rate > 0:
        notes.append(
            {
                "level": "warn",
                "message": "Recovery rate below 50% in this period.",
            }
        )
    return notes
