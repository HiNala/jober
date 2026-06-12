from __future__ import annotations

import calendar
from datetime import UTC, date, datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.config import settings
from jober_api.health import readiness_report
from jober_api.models.analytics import AnalyticsDailyActiveUsers, AnalyticsDailyCost
from jober_api.models.application_run import ApplicationRun
from jober_api.models.enums import JobTargetStatus, RunStatus
from jober_api.models.failure_event import FailureEvent
from jober_api.models.job_target import JobTarget
from jober_api.models.user import User
from jober_api.services.admin.ops_metrics import build_ops_attention
from jober_api.services.analytics.dashboard import get_admin_cost, resolve_date_range
from jober_api.services.batch.redis_control import queue_snapshot
from jober_api.services.ops.alerting import (
    RUNBOOK_INFRA_DOWN,
    RUNBOOK_QUEUE_BACKED_UP,
    dispatch_ops_alerts,
)
from jober_api.services.ops.alerting import (
    ops_attention as ops_alert_item,
)


async def get_admin_overview(session: AsyncSession) -> dict[str, Any]:
    """Ops-first snapshot: growth, runs, cost, health, and attention items."""
    today = datetime.now(UTC).date()
    start_30d, end_30d = resolve_date_range(today - timedelta(days=29), today)

    latest_active = (
        await session.execute(
            select(AnalyticsDailyActiveUsers)
            .order_by(AnalyticsDailyActiveUsers.day.desc())
            .limit(1)
        )
    ).scalar_one_or_none()

    signup_counts = await _signup_counts(session, today)
    run_counts = await _run_counts(session, start_30d, end_30d)
    submit_count = await _submit_count(session, start_30d, end_30d)

    cost_stmt = select(func.coalesce(func.sum(AnalyticsDailyCost.cost_usd), 0.0)).where(
        AnalyticsDailyCost.day >= start_30d,
        AnalyticsDailyCost.day <= end_30d,
    )
    cost_30d = float((await session.execute(cost_stmt)).scalar_one() or 0.0)
    _, days_in_month = calendar.monthrange(today.year, today.month)
    forecast_monthly = round((cost_30d / 30) * days_in_month, 2) if cost_30d else 0.0

    health = await readiness_report(settings.database_url, settings.redis_url)
    queue = queue_snapshot(settings.batch_max_concurrency)

    failure_spike = await _recent_failure_spike(session, days=7)
    cost_data = await get_admin_cost(session, start=start_30d, end=end_30d)

    attention: list[dict[str, str]] = []
    if health["status"] != "ready":
        attention.append(
            ops_alert_item(
                "error",
                "One or more infrastructure checks failed.",
                runbook=RUNBOOK_INFRA_DOWN,
            )
        )
    if queue["globally_paused"]:
        attention.append(
            ops_alert_item(
                "warn",
                "Worker queue is globally paused.",
                runbook=RUNBOOK_QUEUE_BACKED_UP,
            )
        )
    if failure_spike:
        attention.append(
            ops_alert_item(
                "warn",
                f"Failure events up {failure_spike['pct']}% vs prior week.",
            )
        )
    for note in cost_data.get("attention", []):
        attention.append(note)
    if run_counts["needs_human"] > 0:
        attention.append(
            ops_alert_item(
                "warn",
                f"{run_counts['needs_human']} run(s) need human intervention.",
            )
        )

    ops_attention, ops = await build_ops_attention(session, queue=queue)
    attention.extend(ops_attention)

    succeeded = int(run_counts.get("succeeded", 0))
    failed = int(run_counts.get("failed", 0))
    recovery_rate = round(succeeded / max(succeeded + failed, 1), 4)
    ops["recovery_rate_30d"] = recovery_rate

    await dispatch_ops_alerts("admin_overview", attention)

    return {
        "as_of": datetime.now(UTC).isoformat(),
        "active_users": {
            "dau": latest_active.dau if latest_active else 0,
            "wau": latest_active.wau if latest_active else 0,
            "mau": latest_active.mau if latest_active else 0,
            "day": latest_active.day.isoformat() if latest_active else None,
        },
        "signups": signup_counts,
        "runs": run_counts,
        "submits_30d": submit_count,
        "cost": {
            "last_30d_usd": round(cost_30d, 4),
            "forecast_monthly_usd": forecast_monthly,
            "reconciled": cost_data.get("reconciled", True),
        },
        "health": {
            "status": health["status"],
            "checks": health["checks"],
            "queue": queue,
        },
        "attention": attention,
        "ops": ops,
    }


async def _signup_counts(session: AsyncSession, today: date) -> dict[str, int]:
    ranges = {
        "today": (today, today + timedelta(days=1)),
        "last_7d": (today - timedelta(days=6), today + timedelta(days=1)),
        "last_30d": (today - timedelta(days=29), today + timedelta(days=1)),
    }
    out: dict[str, int] = {}
    for label, (start, end) in ranges.items():
        start_dt = datetime.combine(start, datetime.min.time(), tzinfo=UTC)
        end_dt = datetime.combine(end, datetime.min.time(), tzinfo=UTC)
        stmt = (
            select(func.count())
            .select_from(User)
            .where(User.created_at >= start_dt, User.created_at < end_dt)
        )
        out[label] = int((await session.execute(stmt)).scalar_one())
    return out


async def _run_counts(session: AsyncSession, start: date, end: date) -> dict[str, Any]:
    start_dt = datetime.combine(start, datetime.min.time(), tzinfo=UTC)
    end_dt = datetime.combine(end + timedelta(days=1), datetime.min.time(), tzinfo=UTC)
    stmt = (
        select(ApplicationRun.status, func.count())
        .where(ApplicationRun.created_at >= start_dt, ApplicationRun.created_at < end_dt)
        .group_by(ApplicationRun.status)
    )
    by_status = {row[0].value: int(row[1]) for row in (await session.execute(stmt)).all()}
    needs_human_stmt = (
        select(func.count())
        .select_from(ApplicationRun)
        .where(ApplicationRun.status == RunStatus.NEEDS_HUMAN)
    )
    return {
        "total": sum(by_status.values()),
        "succeeded": by_status.get(RunStatus.SUCCEEDED.value, 0),
        "failed": by_status.get(RunStatus.FAILED_FINAL.value, 0)
        + by_status.get(RunStatus.FAILED_RETRYABLE.value, 0),
        "needs_human": int((await session.execute(needs_human_stmt)).scalar_one()),
        "by_status": by_status,
    }


async def _submit_count(session: AsyncSession, start: date, end: date) -> int:
    stmt = (
        select(func.count())
        .select_from(JobTarget)
        .where(
            JobTarget.status == JobTargetStatus.APPLIED,
            JobTarget.applied_date >= start,
            JobTarget.applied_date <= end,
        )
    )
    return int((await session.execute(stmt)).scalar_one())


async def _recent_failure_spike(session: AsyncSession, *, days: int) -> dict[str, int] | None:
    now = datetime.now(UTC)
    current_start = now - timedelta(days=days)
    prior_start = now - timedelta(days=days * 2)
    current_stmt = (
        select(func.count())
        .select_from(FailureEvent)
        .where(FailureEvent.created_at >= current_start)
    )
    prior_stmt = (
        select(func.count())
        .select_from(FailureEvent)
        .where(FailureEvent.created_at >= prior_start, FailureEvent.created_at < current_start)
    )
    current = int((await session.execute(current_stmt)).scalar_one())
    prior = int((await session.execute(prior_stmt)).scalar_one())
    if prior == 0 or current <= prior * 1.25:
        return None
    pct = int(round((current - prior) / prior * 100))
    return {"current": current, "prior": prior, "pct": pct}
