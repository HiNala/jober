from __future__ import annotations

import os
import uuid
from datetime import UTC, date, datetime, time, timedelta

import pytest
from httpx import ASGITransport, AsyncClient

from jober_api.auth.constants import DEFAULT_DEV_TENANT_ID, DEFAULT_DEV_USER_ID
from jober_api.main import app
from jober_api.models.analytics import AnalyticsDailyCost
from jober_api.models.enums import JobTargetStatus, UserRole
from jober_api.models.job_target import JobTarget
from jober_api.models.llm_call import LlmCall
from jober_api.models.user import User
from jober_api.services.analytics.rollups import rollup_analytics_day

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres",
)


@pytest.fixture
async def admin_user(db_session) -> User:
    user = await db_session.get(User, DEFAULT_DEV_USER_ID)
    assert user is not None
    user.role = UserRole.ADMIN
    await db_session.commit()
    return user


@pytest.mark.asyncio
async def test_admin_funnel_matches_seeded_rollups(
    db_session, truncate_tables, admin_user, auth_headers
) -> None:
    day = date(2026, 6, 10)
    start = datetime.combine(day, time.min, tzinfo=UTC)
    from jober_api.models.analytics import AnalyticsEvent

    db_session.add_all(
        [
            AnalyticsEvent(
                id=uuid.uuid4(),
                ts=start + timedelta(hours=1),
                session_id="funnel-s1",
                anon_id="a1",
                name="page.view",
                props={"path": "/"},
                page="/",
                source="client",
            ),
            AnalyticsEvent(
                id=uuid.uuid4(),
                ts=start + timedelta(hours=2),
                session_id="funnel-s1",
                anon_id="a1",
                name="signup.start",
                props={},
                source="client",
            ),
            AnalyticsEvent(
                id=uuid.uuid4(),
                ts=start + timedelta(hours=3),
                session_id="funnel-s1",
                anon_id="a1",
                name="signup.complete",
                props={"method": "password"},
                source="server",
                user_id=DEFAULT_DEV_USER_ID,
                tenant_id=DEFAULT_DEV_TENANT_ID,
            ),
        ]
    )
    await db_session.commit()
    await rollup_analytics_day(db_session, day)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/analytics/admin/funnel",
            params={"start": day.isoformat(), "end": day.isoformat()},
            headers=auth_headers,
        )
    assert response.status_code == 200
    body = response.json()
    steps = {row["step"]: row for row in body["steps"]}
    assert steps["landing"]["event_count"] == 1
    assert steps["signup_start"]["event_count"] == 1
    assert steps["signup_complete"]["event_count"] == 1
    assert steps["signup_start"]["drop_off_sessions"] == 0


@pytest.mark.asyncio
async def test_admin_funnel_forbidden_for_non_admin(
    db_session, truncate_tables, auth_headers
) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/analytics/admin/funnel", headers=auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_user_analytics_scoped_to_tenant(db_session, truncate_tables, auth_headers) -> None:
    day = date.today()
    db_session.add(
        JobTarget(
            id=uuid.uuid4(),
            tenant_id=DEFAULT_DEV_TENANT_ID,
            company="Acme",
            role="Engineer",
            status=JobTargetStatus.APPLIED,
            applied_date=day,
        )
    )
    await db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/analytics/me",
            params={"start": (day - timedelta(days=7)).isoformat(), "end": day.isoformat()},
            headers=auth_headers,
        )
    assert response.status_code == 200
    assert response.json()["summary"]["applications_sent"] == 1


@pytest.mark.asyncio
async def test_admin_cost_reconciles_with_llm_calls(
    db_session, truncate_tables, admin_user, auth_headers
) -> None:
    from jober_api.models.application_run import ApplicationRun
    from jober_api.models.enums import RunStatus

    day = date(2026, 6, 11)
    job = JobTarget(
        id=uuid.uuid4(),
        tenant_id=DEFAULT_DEV_TENANT_ID,
        company="CostCo",
        role="Engineer",
        status=JobTargetStatus.QUEUED,
    )
    db_session.add(job)
    await db_session.flush()
    run = ApplicationRun(
        id=uuid.uuid4(),
        tenant_id=DEFAULT_DEV_TENANT_ID,
        job_target_id=job.id,
        status=RunStatus.QUEUED,
    )
    db_session.add(run)
    await db_session.flush()
    ts = datetime.combine(day, time(hour=12), tzinfo=UTC)
    db_session.add(
        LlmCall(
            id=uuid.uuid4(),
            run_id=run.id,
            agent_role="cover_letter",
            provider="openai",
            model="gpt-4o-mini",
            prompt_tokens=100,
            completion_tokens=50,
            cost_usd=0.02,
            created_at=ts,
        )
    )
    db_session.add(
        AnalyticsDailyCost(
            day=day,
            tenant_id=DEFAULT_DEV_TENANT_ID,
            agent_role="cover_letter",
            model="gpt-4o-mini",
            prompt_tokens=100,
            completion_tokens=50,
            cost_usd=0.02,
            llm_call_count=1,
        )
    )
    await db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/analytics/admin/cost",
            params={"start": day.isoformat(), "end": day.isoformat()},
            headers=auth_headers,
        )
    assert response.status_code == 200
    body = response.json()
    assert body["reconciled"] is True
    assert body["rollup_total_usd"] == pytest.approx(0.02)
