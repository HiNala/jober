"""Golden-path integration — fixture discover/fill → verify → analytics → acquisition."""

from __future__ import annotations

import os
import uuid
from datetime import UTC, date, datetime, time

import httpx
import pytest
from httpx import ASGITransport, AsyncClient
from jober_schemas.analytics import AnalyticsBatchRequest, AnalyticsEventInput
from sqlalchemy import select

from jober_api.auth.constants import DEFAULT_DEV_TENANT_ID, DEFAULT_DEV_USER_ID
from jober_api.main import app
from jober_api.models.analytics import AnalyticsDailyFunnel, AnalyticsEvent
from jober_api.models.enums import RunStatus, UserRole
from jober_api.models.tenant import Tenant
from jober_api.models.user import User
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.repositories.user_profile import UserProfileRepository
from jober_api.services.analytics.consent import CONSENT_COOKIE
from jober_api.services.analytics.rollups import rollup_analytics_day
from tests.fixtures.form_pages import load_form_fixture

pytestmark = [
    pytest.mark.skipif(
        os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
        reason="requires Postgres",
    ),
    pytest.mark.skipif(
        os.getenv("SKIP_FIXTURE_SERVER") == "1",
        reason="fixture server disabled",
    ),
]


async def _seed_job(db_session):
    jobs = JobTargetRepository(db_session)
    job = await jobs.create(company="Golden Co", role="Staff Engineer")
    profiles = UserProfileRepository(db_session)
    await profiles.create(name="Ada Lovelace", email="ada@example.com", phone="555-0199")
    await db_session.commit()
    return job


def _fetch_html(fixture_server_url: str, slug: str) -> str:
    res = httpx.get(f"{fixture_server_url}/{slug}", timeout=10.0)
    res.raise_for_status()
    return res.text


@pytest.mark.asyncio
@pytest.mark.policy
async def test_golden_path_fixture_fill_verify_analytics_admin(
    fixture_server_url: str,
    db_session,
    truncate_tables,
    auth_headers,
) -> None:
    from jober_api.db import session as db_session_module

    job = await _seed_job(db_session)
    ats_html = _fetch_html(fixture_server_url, "behaviors/single-step")
    submit_fixture = load_form_fixture("submit_success")

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            discover = await client.post(
                f"/api/job-targets/{job.id}/discover-form",
                json={"fixture_html": ats_html, "platform": "greenhouse"},
            )
            assert discover.status_code == 200, discover.text

            fill = await client.post(
                f"/api/job-targets/{job.id}/fill-form",
                json={"fixture_html": ats_html},
            )
            assert fill.status_code == 200, fill.text
            assert fill.json().get("status") == "succeeded"

            verify = await client.post(
                f"/api/job-targets/{job.id}/verify-ready",
                json={"fixture_html": submit_fixture},
            )
            assert verify.status_code == 200, verify.text
            verify_body = verify.json()
            assert verify_body["status"] == RunStatus.REVIEW_AND_SUBMIT.value
            assert verify_body["readiness"]["passed"] is True
            run_id = verify_body["run_id"]

            review = await client.get(f"/api/application-runs/{run_id}/review")
            assert review.status_code == 200
            assert review.json()["readiness"]["passed"] is True

            analytics_body = AnalyticsBatchRequest(
                events=[
                    AnalyticsEventInput(
                        name="page.view",
                        session_id="golden-path-session",
                        anon_id="golden-anon",
                        page="/",
                        props={"path": "/", "title": "Home"},
                    ),
                    AnalyticsEventInput(
                        name="feature.use",
                        session_id="golden-path-session",
                        anon_id="golden-anon",
                        props={"feature": "landing_hero_signup"},
                    ),
                    AnalyticsEventInput(
                        name="signup.start",
                        session_id="golden-path-session",
                        anon_id="golden-anon",
                    ),
                ]
            )
            events_res = await client.post(
                "/api/events",
                json=analytics_body.model_dump(mode="json"),
                cookies={CONSENT_COOKIE: "1"},
                headers={"User-Agent": "Mozilla/5.0 Chrome/120"},
            )
            assert events_res.status_code == 204

            user = await db_session.get(User, DEFAULT_DEV_USER_ID)
            assert user is not None
            user.role = UserRole.ADMIN
            await db_session.commit()

            day = date.today()
            rollup = await rollup_analytics_day(db_session, day)
            assert rollup["events_processed"] >= 3

            acquisition = await client.get("/api/admin/acquisition", headers=auth_headers)
            assert acquisition.status_code == 200
            assert "funnel" in acquisition.json()

            tenant = await db_session.get(Tenant, DEFAULT_DEV_TENANT_ID)
            assert tenant is not None
            assert tenant.policy.get("auto_submit_opt_in") is False
            assert tenant.policy.get("default_run_policy") == "review_before_submit"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_golden_path_analytics_events_persist_before_rollup(
    db_session, truncate_tables
) -> None:
    day = date(2026, 6, 3)
    start = datetime.combine(day, time(hour=10), tzinfo=UTC)
    db_session.add(
        AnalyticsEvent(
            id=uuid.uuid4(),
            ts=start,
            session_id="gp-sess",
            anon_id="gp-anon",
            name="feature.use",
            props={"feature": "pricing_free_signup"},
            source="client",
        )
    )
    await db_session.commit()

    result = await rollup_analytics_day(db_session, day)
    assert result["events_processed"] == 1

    funnel = (
        (
            await db_session.execute(
                select(AnalyticsDailyFunnel).where(AnalyticsDailyFunnel.day == day)
            )
        )
        .scalars()
        .all()
    )
    assert funnel  # rollup produced at least one funnel row
