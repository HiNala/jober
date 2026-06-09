from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import Request
from jober_schemas.analytics import AnalyticsBatchRequest, AnalyticsEventInput
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.auth.context import AuthContext
from jober_api.config import settings
from jober_api.models.analytics import AnalyticsEvent
from jober_api.privacy.redaction import scrub_dict
from jober_api.services.analytics.bot_filter import mark_bot_and_internal, should_drop_event
from jober_api.services.analytics.consent import tracking_suppressed
from jober_api.services.analytics.event_registry import sanitize_props, validate_event
from jober_api.services.analytics.geo import coarse_geo_from_ip
from jober_api.services.analytics.user_agent import user_agent_family


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client is not None:
        return request.client.host
    return ""


def _clamp_client_ts(ts: datetime | None) -> datetime:
    now = datetime.now(UTC)
    if ts is None:
        return now
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=UTC)
    if ts > now + timedelta(minutes=5):
        return now
    if ts < now - timedelta(days=7):
        return now
    return ts


async def ingest_client_batch(
    session: AsyncSession,
    request: Request,
    body: AnalyticsBatchRequest,
    auth: AuthContext | None,
) -> int:
    if not settings.analytics_enabled:
        return 0
    if tracking_suppressed(request):
        return 0

    user_agent = request.headers.get("User-Agent")
    if should_drop_event(user_agent=user_agent):
        return 0

    is_bot, is_internal = mark_bot_and_internal(auth=auth, user_agent=user_agent)
    geo_country, geo_region = coarse_geo_from_ip(_client_ip(request))
    ua_family = user_agent_family(user_agent)

    stored = 0
    for event in body.events:
        if _persist_event(
            session,
            event=event,
            auth=auth,
            source="client",
            geo_country=geo_country,
            geo_region=geo_region,
            user_agent_family=ua_family,
            is_bot=is_bot,
            is_internal=is_internal,
        ):
            stored += 1
    if stored:
        await session.commit()
    return stored


def _persist_event(
    session: AsyncSession,
    *,
    event: AnalyticsEventInput,
    auth: AuthContext | None,
    source: str,
    geo_country: str | None = None,
    geo_region: str | None = None,
    user_agent_family: str | None = None,
    is_bot: bool = False,
    is_internal: bool = False,
    user_id: uuid.UUID | None = None,
    tenant_id: uuid.UUID | None = None,
) -> bool:
    props = scrub_dict(event.props or {})
    try:
        validate_event(event.name, props, source=source)
    except ValueError:
        return False

    clean_props = sanitize_props(event.name, props)
    resolved_user = user_id or (auth.user_id if auth else None)
    resolved_tenant = tenant_id or (auth.tenant_id if auth else None)

    row = AnalyticsEvent(
        id=uuid.uuid4(),
        ts=_clamp_client_ts(event.ts),
        user_id=resolved_user,
        tenant_id=resolved_tenant,
        anon_id=event.anon_id,
        session_id=event.session_id,
        name=event.name,
        props=clean_props,
        page=event.page,
        referrer=event.referrer,
        utm_source=event.utm_source,
        utm_medium=event.utm_medium,
        utm_campaign=event.utm_campaign,
        utm_term=event.utm_term,
        utm_content=event.utm_content,
        geo_country=geo_country,
        geo_region=geo_region,
        user_agent_family=user_agent_family,
        source=source,
        is_bot=is_bot,
        is_internal=is_internal,
    )
    session.add(row)
    return True


async def emit_server_event(
    session: AsyncSession,
    *,
    name: str,
    session_id: str,
    props: dict | None = None,
    user_id: uuid.UUID | None = None,
    tenant_id: uuid.UUID | None = None,
    page: str | None = None,
    anon_id: str | None = None,
) -> bool:
    if not settings.analytics_enabled:
        return False

    event = AnalyticsEventInput(
        name=name,
        session_id=session_id,
        props=props or {},
        page=page,
        anon_id=anon_id,
    )
    stored = _persist_event(
        session,
        event=event,
        auth=None,
        source="server",
        user_id=user_id,
        tenant_id=tenant_id,
        is_internal=False,
        is_bot=False,
    )
    if stored:
        await session.flush()
    return stored
