from __future__ import annotations

import csv
import io
import uuid
from datetime import UTC, date, datetime, timedelta
from typing import Any, cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.analytics import (
    AnalyticsDailyActiveUsers,
    AnalyticsDailyCost,
    AnalyticsDailyFunnel,
    AnalyticsDailyPage,
)
from jober_api.models.application_run import ApplicationRun
from jober_api.models.enums import JobTargetStatus, PlanTier, RunStatus
from jober_api.models.generated_document import GeneratedDocument
from jober_api.models.job_target import JobTarget
from jober_api.models.llm_call import LlmCall
from jober_api.services.analytics.cache import cache_get, cache_key, cache_set
from jober_api.services.analytics.event_registry import FUNNEL_STEPS
from jober_api.services.billing.entitlements import entitlements_for

FUNNEL_ORDER = list(FUNNEL_STEPS.keys())


def resolve_date_range(
    start: date | None,
    end: date | None,
    *,
    default_days: int = 30,
) -> tuple[date, date]:
    end_date = end or datetime.now(UTC).date()
    start_date = start or (end_date - timedelta(days=default_days - 1))
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    return start_date, end_date


def previous_period(start: date, end: date) -> tuple[date, date]:
    span = (end - start).days + 1
    prev_end = start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=span - 1)
    return prev_start, prev_end


async def get_user_analytics(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    plan: PlanTier,
    start: date | None = None,
    end: date | None = None,
    compare_previous: bool = False,
) -> dict[str, Any]:
    start_date, end_date = resolve_date_range(start, end)
    key = cache_key("user", tenant_id, start_date, end_date, compare_previous)
    cached = cache_get(key)
    if cached is not None:
        return cast(dict[str, Any], cached)

    ents = entitlements_for(plan)
    applied_stmt = (
        select(func.count())
        .select_from(JobTarget)
        .where(
            JobTarget.tenant_id == tenant_id,
            JobTarget.status == JobTargetStatus.APPLIED,
            JobTarget.applied_date >= start_date,
            JobTarget.applied_date <= end_date,
        )
    )
    applications_sent = int((await session.execute(applied_stmt)).scalar_one())

    outcomes_stmt = (
        select(JobTarget.status, func.count())
        .where(
            JobTarget.tenant_id == tenant_id,
            JobTarget.updated_at >= datetime.combine(start_date, datetime.min.time(), tzinfo=UTC),
            JobTarget.updated_at
            < datetime.combine(end_date + timedelta(days=1), datetime.min.time(), tzinfo=UTC),
            JobTarget.status.in_([JobTargetStatus.APPLIED, JobTargetStatus.REJECTED]),
        )
        .group_by(JobTarget.status)
    )
    outcomes = {row[0].value: int(row[1]) for row in (await session.execute(outcomes_stmt)).all()}
    responses = outcomes.get(JobTargetStatus.APPLIED.value, 0) + outcomes.get(
        JobTargetStatus.REJECTED.value, 0
    )

    letters_stmt = (
        select(func.count())
        .select_from(GeneratedDocument)
        .join(JobTarget, GeneratedDocument.job_target_id == JobTarget.id)
        .where(
            JobTarget.tenant_id == tenant_id,
            GeneratedDocument.created_at
            >= datetime.combine(start_date, datetime.min.time(), tzinfo=UTC),
            GeneratedDocument.created_at
            < datetime.combine(end_date + timedelta(days=1), datetime.min.time(), tzinfo=UTC),
        )
    )
    letters_generated = int((await session.execute(letters_stmt)).scalar_one())

    cost_stmt = select(
        func.coalesce(func.sum(AnalyticsDailyCost.cost_usd), 0.0),
        func.coalesce(func.sum(AnalyticsDailyCost.prompt_tokens), 0),
        func.coalesce(func.sum(AnalyticsDailyCost.completion_tokens), 0),
    ).where(
        AnalyticsDailyCost.tenant_id == tenant_id,
        AnalyticsDailyCost.day >= start_date,
        AnalyticsDailyCost.day <= end_date,
    )
    cost_row = (await session.execute(cost_stmt)).one()
    llm_cost_usd = float(cost_row[0] or 0.0)

    activity_stmt = (
        select(
            func.date_trunc("day", ApplicationRun.created_at).label("day"),
            func.count(),
        )
        .where(
            ApplicationRun.tenant_id == tenant_id,
            ApplicationRun.created_at
            >= datetime.combine(start_date, datetime.min.time(), tzinfo=UTC),
            ApplicationRun.created_at
            < datetime.combine(end_date + timedelta(days=1), datetime.min.time(), tzinfo=UTC),
            ApplicationRun.status.notin_([RunStatus.SKIPPED]),
        )
        .group_by("day")
        .order_by("day")
    )
    activity = [
        {"day": row.day.date().isoformat(), "runs": int(row[1])}
        for row in (await session.execute(activity_stmt)).all()
    ]

    cost_daily_stmt = (
        select(
            AnalyticsDailyCost.day,
            func.sum(AnalyticsDailyCost.cost_usd),
        )
        .where(
            AnalyticsDailyCost.tenant_id == tenant_id,
            AnalyticsDailyCost.day >= start_date,
            AnalyticsDailyCost.day <= end_date,
        )
        .group_by(AnalyticsDailyCost.day)
        .order_by(AnalyticsDailyCost.day)
    )
    cost_series = [
        {"day": row.day.isoformat(), "cost_usd": round(float(row[1] or 0.0), 4)}
        for row in (await session.execute(cost_daily_stmt)).all()
    ]

    payload: dict[str, Any] = {
        "range": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "summary": {
            "applications_sent": applications_sent,
            "responses_tracked": responses,
            "letters_generated": letters_generated,
            "llm_cost_usd": round(llm_cost_usd, 4),
            "llm_budget_usd": ents.max_llm_budget_usd,
            "budget_used_ratio": round(llm_cost_usd / ents.max_llm_budget_usd, 4)
            if ents.max_llm_budget_usd
            else 0.0,
        },
        "activity": activity,
        "cost_series": cost_series,
        "attention": _user_attention(
            llm_cost_usd, ents.max_llm_budget_usd, applications_sent, letters_generated
        ),
    }

    if compare_previous:
        prev_start, prev_end = previous_period(start_date, end_date)
        prev = await get_user_analytics(
            session,
            tenant_id=tenant_id,
            plan=plan,
            start=prev_start,
            end=prev_end,
            compare_previous=False,
        )
        payload["previous"] = prev["summary"]

    cache_set(key, payload)
    return payload


def _user_attention(
    cost: float,
    budget: float,
    applications: int,
    letters: int,
) -> list[dict[str, str]]:
    notes: list[dict[str, str]] = []
    if budget > 0 and cost / budget >= 0.8:
        notes.append(
            {
                "level": "warn",
                "message": "LLM spend is above 80% of your monthly budget.",
            }
        )
    if applications == 0 and letters > 0:
        notes.append(
            {
                "level": "info",
                "message": "Letters generated but no applications marked sent in this range.",
            }
        )
    return notes


async def get_admin_funnel(
    session: AsyncSession,
    *,
    start: date | None = None,
    end: date | None = None,
    compare_previous: bool = False,
) -> dict[str, Any]:
    start_date, end_date = resolve_date_range(start, end)
    key = cache_key("admin_funnel", start_date, end_date, compare_previous)
    cached = cache_get(key)
    if cached is not None:
        return cast(dict[str, Any], cached)

    stmt = (
        select(
            AnalyticsDailyFunnel.step,
            func.sum(AnalyticsDailyFunnel.event_count),
            func.sum(AnalyticsDailyFunnel.unique_sessions),
        )
        .where(
            AnalyticsDailyFunnel.day >= start_date,
            AnalyticsDailyFunnel.day <= end_date,
        )
        .group_by(AnalyticsDailyFunnel.step)
    )
    rows = {
        row.step: (int(row[1] or 0), int(row[2] or 0))
        for row in (await session.execute(stmt)).all()
    }

    steps: list[dict[str, Any]] = []
    prev_sessions = 0
    for step in FUNNEL_ORDER:
        event_count, sessions = rows.get(step, (0, 0))
        drop_off = max(0, prev_sessions - sessions) if prev_sessions else 0
        drop_off_rate = round(drop_off / prev_sessions, 4) if prev_sessions else 0.0
        steps.append(
            {
                "step": step,
                "event_name": FUNNEL_STEPS[step],
                "event_count": event_count,
                "unique_sessions": sessions,
                "drop_off_sessions": drop_off,
                "drop_off_rate": drop_off_rate,
            }
        )
        prev_sessions = sessions

    payload: dict[str, Any] = {
        "range": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "steps": steps,
    }

    if compare_previous:
        prev_start, prev_end = previous_period(start_date, end_date)
        prev = await get_admin_funnel(
            session, start=prev_start, end=prev_end, compare_previous=False
        )
        payload["previous_steps"] = prev["steps"]

    cache_set(key, payload)
    return payload


async def get_admin_traffic(
    session: AsyncSession,
    *,
    start: date | None = None,
    end: date | None = None,
) -> dict[str, Any]:
    start_date, end_date = resolve_date_range(start, end)
    key = cache_key("admin_traffic", start_date, end_date)
    cached = cache_get(key)
    if cached is not None:
        return cast(dict[str, Any], cached)

    page_stmt = (
        select(
            AnalyticsDailyPage.page,
            func.sum(AnalyticsDailyPage.page_views),
            func.sum(AnalyticsDailyPage.unique_sessions),
            func.sum(AnalyticsDailyPage.total_time_on_page_sec),
            func.sum(AnalyticsDailyPage.bounces),
        )
        .where(
            AnalyticsDailyPage.day >= start_date,
            AnalyticsDailyPage.day <= end_date,
        )
        .group_by(AnalyticsDailyPage.page)
        .order_by(func.sum(AnalyticsDailyPage.page_views).desc())
        .limit(25)
    )
    pages = [
        {
            "page": row.page,
            "page_views": int(row[1] or 0),
            "unique_sessions": int(row[2] or 0),
            "avg_time_on_page_sec": round(float(row[3] or 0) / max(int(row[1] or 0), 1), 1),
            "bounce_rate": round(int(row[4] or 0) / max(int(row[2] or 0), 1), 4),
        }
        for row in (await session.execute(page_stmt)).all()
    ]

    dau_stmt = (
        select(
            AnalyticsDailyActiveUsers.day,
            AnalyticsDailyActiveUsers.dau,
            AnalyticsDailyActiveUsers.wau,
            AnalyticsDailyActiveUsers.mau,
        )
        .where(
            AnalyticsDailyActiveUsers.day >= start_date,
            AnalyticsDailyActiveUsers.day <= end_date,
        )
        .order_by(AnalyticsDailyActiveUsers.day)
    )
    active_series = [
        {
            "day": row.day.isoformat(),
            "dau": row.dau,
            "wau": row.wau,
            "mau": row.mau,
        }
        for row in (await session.execute(dau_stmt)).all()
    ]

    payload = {
        "range": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "pages": pages,
        "active_users": active_series,
        "totals": {
            "page_views": sum(p["page_views"] for p in pages),
            "sessions": sum(p["unique_sessions"] for p in pages),
        },
    }
    cache_set(key, payload)
    return payload


async def get_admin_cost(
    session: AsyncSession,
    *,
    start: date | None = None,
    end: date | None = None,
) -> dict[str, Any]:
    start_date, end_date = resolve_date_range(start, end)
    key = cache_key("admin_cost", start_date, end_date)
    cached = cache_get(key)
    if cached is not None:
        return cast(dict[str, Any], cached)

    rollup_stmt = (
        select(
            AnalyticsDailyCost.day,
            AnalyticsDailyCost.tenant_id,
            AnalyticsDailyCost.agent_role,
            AnalyticsDailyCost.model,
            AnalyticsDailyCost.prompt_tokens,
            AnalyticsDailyCost.completion_tokens,
            AnalyticsDailyCost.cost_usd,
            AnalyticsDailyCost.llm_call_count,
        )
        .where(
            AnalyticsDailyCost.day >= start_date,
            AnalyticsDailyCost.day <= end_date,
        )
        .order_by(AnalyticsDailyCost.day.desc(), AnalyticsDailyCost.cost_usd.desc())
    )
    rollup_rows = (await session.execute(rollup_stmt)).all()

    start_dt = datetime.combine(start_date, datetime.min.time(), tzinfo=UTC)
    end_dt = datetime.combine(end_date + timedelta(days=1), datetime.min.time(), tzinfo=UTC)
    llm_stmt = select(
        func.coalesce(func.sum(LlmCall.cost_usd), 0.0),
        func.coalesce(func.sum(LlmCall.prompt_tokens), 0),
        func.coalesce(func.sum(LlmCall.completion_tokens), 0),
        func.count(LlmCall.id),
    ).where(LlmCall.created_at >= start_dt, LlmCall.created_at < end_dt)
    llm_totals = (await session.execute(llm_stmt)).one()

    by_day: dict[str, float] = {}
    by_model: dict[str, float] = {}
    by_agent: dict[str, float] = {}
    rows_out: list[dict[str, Any]] = []
    for row in rollup_rows:
        rows_out.append(
            {
                "day": row.day.isoformat(),
                "tenant_id": str(row.tenant_id),
                "agent_role": row.agent_role,
                "model": row.model,
                "prompt_tokens": row.prompt_tokens,
                "completion_tokens": row.completion_tokens,
                "cost_usd": round(float(row.cost_usd or 0.0), 4),
                "llm_call_count": row.llm_call_count,
            }
        )
        by_day[row.day.isoformat()] = by_day.get(row.day.isoformat(), 0.0) + float(
            row.cost_usd or 0
        )
        by_model[row.model] = by_model.get(row.model, 0.0) + float(row.cost_usd or 0)
        by_agent[row.agent_role] = by_agent.get(row.agent_role, 0.0) + float(row.cost_usd or 0)

    rollup_total = sum(by_day.values())
    llm_total = float(llm_totals[0] or 0.0)
    anomalies = [
        {"day": day, "cost_usd": round(cost, 4)}
        for day, cost in by_day.items()
        if cost > (rollup_total / max(len(by_day), 1)) * 2
    ]

    attention: list[dict[str, str]] = []
    if not abs(rollup_total - llm_total) < 0.05:
        attention.append(
            {
                "level": "warn",
                "message": "Cost rollup does not reconcile with LlmCall totals.",
            }
        )
    if anomalies:
        attention.append(
            {
                "level": "warn",
                "message": f"{len(anomalies)} day(s) with unusually high LLM spend.",
            }
        )

    payload = {
        "range": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "rollup_total_usd": round(rollup_total, 4),
        "llm_call_total_usd": round(llm_total, 4),
        "reconciled": abs(rollup_total - llm_total) < 0.05,
        "by_day": [{"day": d, "cost_usd": round(c, 4)} for d, c in sorted(by_day.items())],
        "by_model": [
            {"model": m, "cost_usd": round(c, 4)}
            for m, c in sorted(by_model.items(), key=lambda x: x[1], reverse=True)
        ],
        "by_agent": [
            {"agent_role": a, "cost_usd": round(c, 4)}
            for a, c in sorted(by_agent.items(), key=lambda x: x[1], reverse=True)
        ],
        "rows": rows_out[:100],
        "anomalies": anomalies,
        "attention": attention,
    }
    cache_set(key, payload)
    return payload


def rows_to_csv(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()
