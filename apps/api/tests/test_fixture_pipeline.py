from __future__ import annotations

import os

import httpx
import pytest
from httpx import ASGITransport, AsyncClient
from jober_fixtures.outcomes import FIXTURE_OUTCOMES
from jober_forms.scanner import scan_multistep_form

from jober_api.main import app
from jober_api.models.enums import JobTargetStatus
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.repositories.user_profile import UserProfileRepository

pytestmark = [
    pytest.mark.skipif(
        os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
        reason="requires Postgres",
    ),
    pytest.mark.skipif(
        os.getenv("SKIP_PLAYWRIGHT") == "1",
        reason="playwright not installed",
    ),
]

BEHAVIOR_SLUGS = sorted(k for k in FIXTURE_OUTCOMES if k.startswith("behaviors/"))
GATE_SLUGS = sorted(k for k in FIXTURE_OUTCOMES if k.startswith("gates/"))
FILL_SLUGS = sorted(
    k for k, outcome in FIXTURE_OUTCOMES.items() if outcome.expected_fill_status == "succeeded"
)
DISCOVERY_SLUGS = sorted(
    k for k, outcome in FIXTURE_OUTCOMES.items() if outcome.expected_discovery_min_fields > 0
)


async def _seed_job(db_session):
    jobs = JobTargetRepository(db_session)
    job = await jobs.create(company="Fixture Co", role="Engineer", status=JobTargetStatus.NEW)
    profiles = UserProfileRepository(db_session)
    await profiles.create(name="Ada Lovelace", email="ada@example.com", phone="555-0199")
    await db_session.commit()
    return job


def _fetch_html(fixture_server_url: str, slug: str) -> str:
    res = httpx.get(f"{fixture_server_url}/{slug}", timeout=10.0)
    res.raise_for_status()
    return res.text


@pytest.mark.parametrize("slug", DISCOVERY_SLUGS)
def test_behavior_fixture_scanner_meets_minimum(slug: str, fixture_server_url: str) -> None:
    outcome = FIXTURE_OUTCOMES[slug]
    if outcome.expected_discovery_min_fields == 0:
        pytest.skip("no discovery expectation")
    html = _fetch_html(fixture_server_url, slug)
    fields = scan_multistep_form(html)
    assert len(fields) >= outcome.expected_discovery_min_fields


@pytest.mark.asyncio
@pytest.mark.parametrize("slug", DISCOVERY_SLUGS)
async def test_behavior_fixture_api_discover(
    slug: str,
    fixture_server_url: str,
    db_session,
    truncate_tables,
) -> None:
    outcome = FIXTURE_OUTCOMES[slug]
    if outcome.expected_discovery_min_fields == 0:
        pytest.skip("no discovery expectation")
    from jober_api.db import session as db_session_module

    job = await _seed_job(db_session)
    html = _fetch_html(fixture_server_url, slug)

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post(
                f"/api/job-targets/{job.id}/discover-form",
                json={"fixture_html": html, "platform": outcome.platform},
            )
            assert res.status_code == 200, res.text
            body = res.json()
            assert len(body.get("items", [])) >= outcome.expected_discovery_min_fields
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.parametrize("slug", FILL_SLUGS)
async def test_behavior_fixture_fill_pipeline(
    slug: str,
    fixture_server_url: str,
    db_session,
    truncate_tables,
) -> None:
    outcome = FIXTURE_OUTCOMES[slug]
    if outcome.expected_fill_status is None:
        pytest.skip("no fill expectation")
    from jober_api.db import session as db_session_module

    job = await _seed_job(db_session)
    html = _fetch_html(fixture_server_url, slug)

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            discover = await client.post(
                f"/api/job-targets/{job.id}/discover-form",
                json={"fixture_html": html, "platform": outcome.platform},
            )
            assert discover.status_code == 200

            fill = await client.post(
                f"/api/job-targets/{job.id}/fill-form",
                json={"fixture_html": html},
            )
            assert fill.status_code == 200, fill.text
            assert fill.json().get("status") == outcome.expected_fill_status
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.policy
@pytest.mark.parametrize("slug", GATE_SLUGS)
async def test_gate_fixture_raises_checkpoint_not_bypass(
    slug: str,
    fixture_server_url: str,
    db_session,
    truncate_tables,
) -> None:
    outcome = FIXTURE_OUTCOMES[slug]
    from jober_api.db import session as db_session_module

    job = await _seed_job(db_session)
    html = _fetch_html(fixture_server_url, slug)
    bootstrap_html = _fetch_html(fixture_server_url, "behaviors/single-step")

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            discover = await client.post(
                f"/api/job-targets/{job.id}/discover-form",
                json={"fixture_html": bootstrap_html, "platform": "greenhouse"},
            )
            assert discover.status_code == 200

            fill = await client.post(
                f"/api/job-targets/{job.id}/fill-form",
                json={"fixture_html": html},
            )
            assert fill.status_code == 409
            body = fill.json()
            assert body["detail"]["gate"] == outcome.expected_gate
    finally:
        app.dependency_overrides.clear()
