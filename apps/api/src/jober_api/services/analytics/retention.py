from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from jober_api.config import settings
from jober_api.models.analytics import AnalyticsEvent


def _stale_cutoff() -> datetime:
    return datetime.now(UTC) - timedelta(days=settings.analytics_retention_days)


async def purge_stale_analytics_events(session: AsyncSession) -> dict[str, int]:
    """Delete analytics events older than ANALYTICS_RETENTION_DAYS."""
    cutoff = _stale_cutoff()
    stale_filter = AnalyticsEvent.ts < cutoff
    deleted = int(
        await session.scalar(select(func.count()).select_from(AnalyticsEvent).where(stale_filter))
        or 0
    )
    if deleted:
        await session.execute(delete(AnalyticsEvent).where(stale_filter))
    await session.commit()
    return {"deleted_events": deleted, "retention_days": settings.analytics_retention_days}


def purge_stale_analytics_events_sync(session: Session) -> dict[str, int]:
    cutoff = _stale_cutoff()
    stale_filter = AnalyticsEvent.ts < cutoff
    deleted = int(
        session.scalar(select(func.count()).select_from(AnalyticsEvent).where(stale_filter)) or 0
    )
    if deleted:
        session.execute(delete(AnalyticsEvent).where(stale_filter))
    session.commit()
    return {"deleted_events": deleted, "retention_days": settings.analytics_retention_days}
