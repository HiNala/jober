from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, time, timedelta
from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from jober_api.models.analytics import (
    AnalyticsDailyActiveUsers,
    AnalyticsDailyCost,
    AnalyticsDailyFunnel,
    AnalyticsDailyPage,
    AnalyticsEvent,
)
from jober_api.models.application_run import ApplicationRun
from jober_api.models.llm_call import LlmCall
from jober_api.services.analytics.sessionization import (
    _actor_key,
    compute_active_users,
    compute_funnel_metrics,
    compute_page_metrics,
)


def _day_bounds(day: date) -> tuple[datetime, datetime]:
    start = datetime.combine(day, time.min, tzinfo=UTC)
    return start, start + timedelta(days=1)


def _rows_to_dicts(rows: list[AnalyticsEvent]) -> list[dict[str, Any]]:
    return [
        {
            "ts": row.ts,
            "name": row.name,
            "session_id": row.session_id,
            "user_id": str(row.user_id) if row.user_id else None,
            "anon_id": row.anon_id,
            "page": row.page,
            "is_bot": row.is_bot,
            "is_internal": row.is_internal,
        }
        for row in rows
    ]


async def _fetch_events(
    session: AsyncSession,
    start: datetime,
    end: datetime,
) -> list[dict[str, Any]]:
    stmt = (
        select(AnalyticsEvent)
        .where(AnalyticsEvent.ts >= start, AnalyticsEvent.ts < end)
        .order_by(AnalyticsEvent.ts.asc())
    )
    rows = list((await session.execute(stmt)).scalars().all())
    return _rows_to_dicts(rows)


def _fetch_events_sync(session: Session, start: datetime, end: datetime) -> list[dict[str, Any]]:
    stmt = (
        select(AnalyticsEvent)
        .where(AnalyticsEvent.ts >= start, AnalyticsEvent.ts < end)
        .order_by(AnalyticsEvent.ts.asc())
    )
    rows = list(session.execute(stmt).scalars().all())
    return _rows_to_dicts(rows)


async def _distinct_actors(session: AsyncSession, start: datetime, end: datetime) -> int:
    stmt = select(AnalyticsEvent).where(
        AnalyticsEvent.ts >= start,
        AnalyticsEvent.ts < end,
        AnalyticsEvent.is_bot.is_(False),
        AnalyticsEvent.is_internal.is_(False),
    )
    rows = list((await session.execute(stmt)).scalars().all())
    return len({_actor_key(_rows_to_dicts([row])[0]) for row in rows})


def _distinct_actors_sync(session: Session, start: datetime, end: datetime) -> int:
    stmt = select(AnalyticsEvent).where(
        AnalyticsEvent.ts >= start,
        AnalyticsEvent.ts < end,
        AnalyticsEvent.is_bot.is_(False),
        AnalyticsEvent.is_internal.is_(False),
    )
    rows = list(session.execute(stmt).scalars().all())
    return len({_actor_key(_rows_to_dicts([row])[0]) for row in rows})


async def _rollup_llm_costs(session: AsyncSession, day: date) -> None:
    start, end = _day_bounds(day)
    await session.execute(delete(AnalyticsDailyCost).where(AnalyticsDailyCost.day == day))

    stmt = (
        select(
            ApplicationRun.tenant_id,
            LlmCall.agent_role,
            LlmCall.model,
            func.coalesce(func.sum(LlmCall.prompt_tokens), 0),
            func.coalesce(func.sum(LlmCall.completion_tokens), 0),
            func.coalesce(func.sum(LlmCall.cost_usd), 0.0),
            func.count(LlmCall.id),
        )
        .join(ApplicationRun, ApplicationRun.id == LlmCall.run_id)
        .where(LlmCall.created_at >= start, LlmCall.created_at < end)
        .group_by(ApplicationRun.tenant_id, LlmCall.agent_role, LlmCall.model)
    )
    for tenant_id, agent_role, model, prompt_t, completion_t, cost, count in (
        await session.execute(stmt)
    ).all():
        session.add(
            AnalyticsDailyCost(
                day=day,
                tenant_id=tenant_id,
                agent_role=agent_role or "unknown",
                model=model or "unknown",
                prompt_tokens=int(prompt_t or 0),
                completion_tokens=int(completion_t or 0),
                cost_usd=float(cost or 0.0),
                llm_call_count=int(count or 0),
            )
        )


def _rollup_llm_costs_sync(session: Session, day: date) -> None:
    start, end = _day_bounds(day)
    session.execute(delete(AnalyticsDailyCost).where(AnalyticsDailyCost.day == day))

    stmt = (
        select(
            ApplicationRun.tenant_id,
            LlmCall.agent_role,
            LlmCall.model,
            func.coalesce(func.sum(LlmCall.prompt_tokens), 0),
            func.coalesce(func.sum(LlmCall.completion_tokens), 0),
            func.coalesce(func.sum(LlmCall.cost_usd), 0.0),
            func.count(LlmCall.id),
        )
        .join(ApplicationRun, ApplicationRun.id == LlmCall.run_id)
        .where(LlmCall.created_at >= start, LlmCall.created_at < end)
        .group_by(ApplicationRun.tenant_id, LlmCall.agent_role, LlmCall.model)
    )
    rows = session.execute(stmt).all()
    for tenant_id, agent_role, model, prompt_t, completion_t, cost, count in rows:
        session.add(
            AnalyticsDailyCost(
                day=day,
                tenant_id=tenant_id,
                agent_role=agent_role or "unknown",
                model=model or "unknown",
                prompt_tokens=int(prompt_t or 0),
                completion_tokens=int(completion_t or 0),
                cost_usd=float(cost or 0.0),
                llm_call_count=int(count or 0),
            )
        )


async def _upsert_product_rollups(
    session: AsyncSession,
    day: date,
    events: list[dict[str, Any]],
) -> None:
    await session.execute(
        delete(AnalyticsDailyFunnel).where(AnalyticsDailyFunnel.day == day)
    )
    await session.execute(delete(AnalyticsDailyPage).where(AnalyticsDailyPage.day == day))
    await session.execute(
        delete(AnalyticsDailyActiveUsers).where(AnalyticsDailyActiveUsers.day == day)
    )

    for metric in compute_funnel_metrics(events):
        session.add(
            AnalyticsDailyFunnel(
                day=day,
                step=metric.step,
                event_count=metric.event_count,
                unique_users=metric.unique_users,
                unique_sessions=metric.unique_sessions,
            )
        )

    for metric in compute_page_metrics(events):
        session.add(
            AnalyticsDailyPage(
                day=day,
                page=metric.page,
                page_views=metric.page_views,
                unique_sessions=metric.unique_sessions,
                total_time_on_page_sec=metric.total_time_on_page_sec,
                bounces=metric.bounces,
            )
        )

    start, _ = _day_bounds(day)
    wau_start = start - timedelta(days=6)
    mau_start = start - timedelta(days=29)
    _, end = _day_bounds(day)
    dau, _, _ = compute_active_users(events, day=day)
    wau = await _distinct_actors(session, wau_start, end)
    mau = await _distinct_actors(session, mau_start, end)
    session.add(AnalyticsDailyActiveUsers(day=day, dau=dau, wau=wau, mau=mau))


def _upsert_product_rollups_sync(session: Session, day: date, events: list[dict[str, Any]]) -> None:
    session.execute(delete(AnalyticsDailyFunnel).where(AnalyticsDailyFunnel.day == day))
    session.execute(delete(AnalyticsDailyPage).where(AnalyticsDailyPage.day == day))
    session.execute(delete(AnalyticsDailyActiveUsers).where(AnalyticsDailyActiveUsers.day == day))

    for metric in compute_funnel_metrics(events):
        session.add(
            AnalyticsDailyFunnel(
                day=day,
                step=metric.step,
                event_count=metric.event_count,
                unique_users=metric.unique_users,
                unique_sessions=metric.unique_sessions,
            )
        )

    for metric in compute_page_metrics(events):
        session.add(
            AnalyticsDailyPage(
                day=day,
                page=metric.page,
                page_views=metric.page_views,
                unique_sessions=metric.unique_sessions,
                total_time_on_page_sec=metric.total_time_on_page_sec,
                bounces=metric.bounces,
            )
        )

    start, end = _day_bounds(day)
    wau_start = start - timedelta(days=6)
    mau_start = start - timedelta(days=29)
    dau, _, _ = compute_active_users(events, day=day)
    wau = _distinct_actors_sync(session, wau_start, end)
    mau = _distinct_actors_sync(session, mau_start, end)
    session.add(AnalyticsDailyActiveUsers(day=day, dau=dau, wau=wau, mau=mau))


async def rollup_analytics_day(session: AsyncSession, day: date) -> dict[str, int]:
    start, end = _day_bounds(day)
    events = await _fetch_events(session, start, end)
    await _upsert_product_rollups(session, day, events)
    await _rollup_llm_costs(session, day)
    await session.commit()
    return {"events_processed": len(events), "day": day.isoformat()}


def rollup_analytics_day_sync(session: Session, day: date) -> dict[str, int]:
    start, end = _day_bounds(day)
    events = _fetch_events_sync(session, start, end)
    _upsert_product_rollups_sync(session, day, events)
    _rollup_llm_costs_sync(session, day)
    session.commit()
    return {"events_processed": len(events), "day": day.isoformat()}


def server_session_id(
    *,
    user_id: uuid.UUID | None = None,
    run_id: uuid.UUID | None = None,
) -> str:
    if run_id is not None:
        return f"run-{run_id}"
    if user_id is not None:
        return f"user-{user_id}"
    return "server"
