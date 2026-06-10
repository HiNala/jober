from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.analytics import AnalyticsDailyFunnel, AnalyticsEvent
from jober_api.models.user import User
from jober_api.services.analytics.dashboard import (
    get_admin_funnel,
    get_admin_traffic,
    resolve_date_range,
)


async def get_admin_acquisition(
    session: AsyncSession,
    *,
    start: datetime | None = None,
    end: datetime | None = None,
) -> dict[str, Any]:
    """Acquisition aggregates: funnel, traffic, UTM sources, coarse geo."""
    end_date = (end or datetime.now(UTC)).date()
    start_date = start.date() if start else end_date - timedelta(days=29)
    start_date, end_date = resolve_date_range(start_date, end_date)
    start_dt = datetime.combine(start_date, datetime.min.time(), tzinfo=UTC)
    end_dt = datetime.combine(end_date + timedelta(days=1), datetime.min.time(), tzinfo=UTC)

    funnel = await get_admin_funnel(session, start=start_date, end=end_date)
    traffic = await get_admin_traffic(session, start=start_date, end=end_date)

    utm_stmt = (
        select(
            AnalyticsEvent.utm_source,
            AnalyticsEvent.utm_medium,
            func.count(),
        )
        .where(
            AnalyticsEvent.ts >= start_dt,
            AnalyticsEvent.ts < end_dt,
            AnalyticsEvent.is_bot.is_(False),
            AnalyticsEvent.is_internal.is_(False),
            AnalyticsEvent.utm_source.isnot(None),
        )
        .group_by(AnalyticsEvent.utm_source, AnalyticsEvent.utm_medium)
        .order_by(func.count().desc())
        .limit(25)
    )
    utm_sources = [
        {
            "utm_source": row[0] or "(direct)",
            "utm_medium": row[1],
            "sessions": int(row[2]),
        }
        for row in (await session.execute(utm_stmt)).all()
    ]

    geo_stmt = (
        select(AnalyticsEvent.geo_country, func.count())
        .where(
            AnalyticsEvent.ts >= start_dt,
            AnalyticsEvent.ts < end_dt,
            AnalyticsEvent.is_bot.is_(False),
            AnalyticsEvent.geo_country.isnot(None),
        )
        .group_by(AnalyticsEvent.geo_country)
        .order_by(func.count().desc())
        .limit(20)
    )
    geo = [
        {"country": row[0], "sessions": int(row[1])}
        for row in (await session.execute(geo_stmt)).all()
    ]

    signups_stmt = (
        select(func.count())
        .select_from(User)
        .where(User.created_at >= start_dt, User.created_at < end_dt)
    )
    signups = int((await session.execute(signups_stmt)).scalar_one())

    signup_funnel_stmt = select(func.sum(AnalyticsDailyFunnel.unique_sessions)).where(
        AnalyticsDailyFunnel.day >= start_date,
        AnalyticsDailyFunnel.day <= end_date,
        AnalyticsDailyFunnel.step == "signup_complete",
    )
    funnel_signups = int((await session.execute(signup_funnel_stmt)).scalar_one() or 0)

    return {
        "range": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "signups": signups,
        "funnel_signups": funnel_signups,
        "funnel": funnel,
        "traffic": traffic,
        "utm_sources": utm_sources,
        "geo": geo,
    }
