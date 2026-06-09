from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from jober_api.config import settings
from jober_api.models.analytics import AnalyticsEvent


async def purge_stale_analytics_events(session: AsyncSession) -> dict[str, int]:
    """Delete analytics events older than ANALYTICS_RETENTION_DAYS."""
    cutoff = datetime.now(UTC) - timedelta(days=settings.analytics_retention_days)
    result = await session.execute(delete(AnalyticsEvent).where(AnalyticsEvent.ts < cutoff))
    deleted = int(result.rowcount or 0)
    await session.commit()
    return {"deleted_events": deleted, "retention_days": settings.analytics_retention_days}


def purge_stale_analytics_events_sync(session: Session) -> dict[str, int]:
    cutoff = datetime.now(UTC) - timedelta(days=settings.analytics_retention_days)
    result = session.execute(delete(AnalyticsEvent).where(AnalyticsEvent.ts < cutoff))
    deleted = int(result.rowcount or 0)
    session.commit()
    return {"deleted_events": deleted, "retention_days": settings.analytics_retention_days}
