from __future__ import annotations

import os
import uuid
from datetime import UTC, date, datetime, time, timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from jober_schemas.analytics import AnalyticsBatchRequest, AnalyticsEventInput
from sqlalchemy import func, select

from jober_api.auth.constants import DEFAULT_DEV_TENANT_ID, DEFAULT_DEV_USER_ID
from jober_api.main import app
from jober_api.models.analytics import (
    AnalyticsDailyActiveUsers,
    AnalyticsDailyFunnel,
    AnalyticsDailyPage,
    AnalyticsEvent,
)
from jober_api.services.analytics.collector import emit_server_event, ingest_client_batch
from jober_api.services.analytics.consent import CONSENT_COOKIE
from jober_api.services.analytics.retention import purge_stale_analytics_events
from jober_api.services.analytics.rollups import (
    MIN_ANALYTICS_SESSION_ID_LEN,
    rollup_analytics_day,
    server_session_id,
)
from jober_api.services.analytics.sessionization import compute_page_metrics

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres",
)


def _event(
    *,
    session_id: str,
    name: str = "page.view",
    page: str = "/",
    ts: datetime,
    anon_id: str = "anon-1",
    user_id: str | None = None,
) -> dict:
    return {
        "ts": ts,
        "name": name,
        "session_id": session_id,
        "anon_id": anon_id,
        "user_id": user_id,
        "page": page,
        "is_bot": False,
        "is_internal": False,
    }


def test_server_session_id_fallback_meets_schema_min_length() -> None:
    fallback = server_session_id()
    assert len(fallback) >= MIN_ANALYTICS_SESSION_ID_LEN


@pytest.mark.asyncio
async def test_consent_opt_out_suppresses_tracking(db_session, truncate_tables) -> None:
    transport = ASGITransport(app=app)
    body = AnalyticsBatchRequest(
        events=[
            AnalyticsEventInput(
                name="page.view",
                session_id="sess-opt-out",
                anon_id="anon-opt-out",
                page="/",
                props={"path": "/"},
            )
        ]
    )
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/events",
            json=body.model_dump(mode="json"),
            cookies={CONSENT_COOKIE: "0"},
            headers={"User-Agent": "Mozilla/5.0"},
        )
    assert response.status_code == 204
    count = await db_session.scalar(select(func.count()).select_from(AnalyticsEvent))
    assert count == 0


@pytest.mark.asyncio
async def test_purge_stale_analytics_events(db_session, truncate_tables) -> None:
    old = datetime(2020, 1, 1, tzinfo=UTC)
    recent = datetime.now(UTC)
    db_session.add_all(
        [
            AnalyticsEvent(
                id=uuid.uuid4(),
                ts=old,
                session_id="sess-old",
                name="page.view",
                props={"path": "/"},
                source="client",
            ),
            AnalyticsEvent(
                id=uuid.uuid4(),
                ts=recent,
                session_id="sess-recent",
                name="page.view",
                props={"path": "/dashboard"},
                source="client",
            ),
        ]
    )
    await db_session.commit()

    result = await purge_stale_analytics_events(db_session)
    assert result["deleted_events"] == 1

    remaining = (
        await db_session.execute(select(AnalyticsEvent.session_id))
    ).scalars().all()
    assert remaining == ["sess-recent"]


def test_sessionization_time_on_page_and_bounce() -> None:
    base = datetime(2026, 6, 1, 12, 0, tzinfo=UTC)
    events = [
        _event(session_id="s1", page="/", ts=base),
        _event(session_id="s1", page="/pricing", ts=base + timedelta(seconds=90)),
        _event(session_id="s2", page="/docs", ts=base),
    ]
    metrics = {m.page: m for m in compute_page_metrics(events)}
    assert metrics["/"].page_views == 1
    assert metrics["/"].bounces == 0
    assert metrics["/"].total_time_on_page_sec == pytest.approx(90.0)
    assert metrics["/docs"].bounces == 1


@pytest.mark.asyncio
async def test_collector_stores_page_view(db_session, truncate_tables) -> None:
    transport = ASGITransport(app=app)
    body = AnalyticsBatchRequest(
        events=[
            AnalyticsEventInput(
                name="page.view",
                session_id="sess-collector-1",
                anon_id="anon-collector-1",
                page="/",
                props={"path": "/", "title": "Home"},
            )
        ]
    )
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/events",
            json=body.model_dump(mode="json"),
            cookies={CONSENT_COOKIE: "1"},
            headers={"User-Agent": "Mozilla/5.0 Chrome/120"},
        )
    assert response.status_code == 204

    count = await db_session.scalar(select(func.count()).select_from(AnalyticsEvent))
    assert count == 1
    row = (await db_session.execute(select(AnalyticsEvent))).scalar_one()
    assert row.name == "page.view"
    assert row.geo_country is not None
    assert "ip" not in row.props
    assert row.props.get("path") == "/"


@pytest.mark.asyncio
async def test_dnt_suppresses_tracking(db_session, truncate_tables) -> None:
    transport = ASGITransport(app=app)
    body = AnalyticsBatchRequest(
        events=[
            AnalyticsEventInput(
                name="page.view",
                session_id="sess-dnt",
                anon_id="anon-dnt",
                page="/",
                props={"path": "/"},
            )
        ]
    )
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/events",
            json=body.model_dump(mode="json"),
            headers={"DNT": "1", "User-Agent": "Mozilla/5.0"},
        )
    assert response.status_code == 204
    count = await db_session.scalar(select(func.count()).select_from(AnalyticsEvent))
    assert count == 0


@pytest.mark.asyncio
async def test_pii_props_rejected(db_session, truncate_tables) -> None:
    from fastapi import Request
    from starlette.datastructures import Headers

    scope = {
        "type": "http",
        "headers": Headers({"user-agent": "Mozilla/5.0"}).raw,
        "client": ("127.0.0.1", 0),
    }
    request = Request(scope)
    request._cookies = {CONSENT_COOKIE: "1"}  # noqa: SLF001
    body = AnalyticsBatchRequest(
        events=[
            AnalyticsEventInput(
                name="feature.use",
                session_id="sess-pii",
                props={"feature": "vault", "email": "secret@example.com"},
            )
        ]
    )
    stored = await ingest_client_batch(db_session, request, body, auth=None)
    assert stored == 0


@pytest.mark.asyncio
async def test_rollup_daily_summaries(db_session, truncate_tables) -> None:
    day = date(2026, 6, 2)
    start = datetime.combine(day, time.min, tzinfo=UTC)
    session_id = "rollup-session"
    rows = [
        AnalyticsEvent(
            id=uuid.uuid4(),
            ts=start + timedelta(hours=1),
            session_id=session_id,
            anon_id="anon-rollup",
            name="page.view",
            props={"path": "/"},
            page="/",
            source="client",
        ),
        AnalyticsEvent(
            id=uuid.uuid4(),
            ts=start + timedelta(hours=1, seconds=30),
            session_id=session_id,
            anon_id="anon-rollup",
            name="signup.start",
            props={},
            source="client",
        ),
        AnalyticsEvent(
            id=uuid.uuid4(),
            ts=start + timedelta(hours=2),
            session_id=session_id,
            anon_id="anon-rollup",
            name="signup.complete",
            props={"method": "password"},
            source="server",
            user_id=DEFAULT_DEV_USER_ID,
            tenant_id=DEFAULT_DEV_TENANT_ID,
        ),
    ]
    db_session.add_all(rows)
    await db_session.commit()

    result = await rollup_analytics_day(db_session, day)
    assert result["events_processed"] == 3

    funnel = (
        await db_session.execute(
            select(AnalyticsDailyFunnel).where(AnalyticsDailyFunnel.day == day)
        )
    ).scalars().all()
    assert {row.step for row in funnel} >= {"landing", "signup_start", "signup_complete"}

    pages = (
        await db_session.execute(select(AnalyticsDailyPage).where(AnalyticsDailyPage.day == day))
    ).scalars().all()
    assert any(row.page == "/" and row.page_views == 1 for row in pages)

    active = await db_session.get(AnalyticsDailyActiveUsers, day)
    assert active is not None
    assert active.dau >= 1


@pytest.mark.asyncio
async def test_server_emit_signup_complete(db_session, truncate_tables) -> None:
    ok = await emit_server_event(
        db_session,
        name="signup.complete",
        session_id=server_session_id(user_id=DEFAULT_DEV_USER_ID),
        user_id=DEFAULT_DEV_USER_ID,
        tenant_id=DEFAULT_DEV_TENANT_ID,
        props={"method": "password"},
    )
    assert ok
    await db_session.commit()
    row = (await db_session.execute(select(AnalyticsEvent))).scalar_one()
    assert row.source == "server"
    assert row.name == "signup.complete"
