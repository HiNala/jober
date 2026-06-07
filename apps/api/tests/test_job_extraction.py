from __future__ import annotations

import os
import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from jober_extraction.a11y import extract_visible_text_from_html
from jober_extraction.gates import GateKind, detect_access_gates
from jober_extraction.intelligence import SYSTEM_INSTRUCTIONS, build_job_profile
from jober_extraction.platform import detect_platform
from sqlalchemy import select

from jober_api.main import app
from jober_api.models.enums import CheckpointStatus, JobTargetStatus, RunStatus
from jober_api.models.human_checkpoint import HumanCheckpoint
from jober_api.repositories.job_target import JobTargetRepository
from tests.fixtures.ats_pages import load_ats_fixture

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres",
)


@pytest.mark.policy
def test_injection_fixture_does_not_produce_false_credential() -> None:
    html = load_ats_fixture("injection")
    visible = extract_visible_text_from_html(html)
    profile = build_job_profile(
        html=html,
        visible_text=visible,
        accessibility_tree=None,
        company_hint="Acme",
    )
    structured = " ".join(profile.requirements + profile.keywords).casefold()
    assert "cka" not in structured
    assert "certified kubernetes" not in structured
    assert any("python" in r.casefold() for r in profile.requirements)


@pytest.mark.policy
def test_system_prompt_marks_page_text_untrusted() -> None:
    lower = SYSTEM_INSTRUCTIONS.casefold()
    assert "untrusted" in lower
    assert "never follow" in lower or "do not" in lower


@pytest.mark.policy
def test_login_gate_detected() -> None:
    html = load_ats_fixture("login_gate")
    gates = detect_access_gates(html, "Sign in to continue")
    assert GateKind.LOGIN in gates


@pytest.mark.policy
def test_captcha_gate_detected() -> None:
    html = load_ats_fixture("captcha_gate")
    gates = detect_access_gates(html, "verify you are human")
    assert GateKind.CAPTCHA in gates


def test_greenhouse_fixture_produces_valid_job_profile() -> None:
    html = load_ats_fixture("greenhouse")
    url = "https://boards.greenhouse.io/acme/jobs/1"
    platform = detect_platform(url, html)
    visible = extract_visible_text_from_html(html)
    profile = build_job_profile(
        html=html,
        visible_text=visible,
        accessibility_tree=None,
        company_hint="Acme AI",
        resume_skills=["Python", "TypeScript", "React"],
    )
    assert platform.platform == "greenhouse"
    assert profile.title
    assert profile.company == "Acme AI"
    assert profile.description
    assert profile.keywords
    assert profile.company_product_summary
    assert profile.fit_score is not None


@pytest.mark.asyncio
async def test_extract_fixture_persists_profile(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    jobs = JobTargetRepository(db_session)
    job = await jobs.create(
        company="Acme AI",
        role="Senior Engineer",
        direct_apply_url="https://boards.greenhouse.io/acme/jobs/1",
        status=JobTargetStatus.NEW,
    )
    await db_session.commit()

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/job-targets/{job.id}/extract",
                json={
                    "fixture_html": load_ats_fixture("greenhouse"),
                    "fixture_url": "https://boards.greenhouse.io/acme/jobs/1",
                    "force": True,
                },
            )
            assert response.status_code == 200, response.text
            body = response.json()
            assert body["job_profile"]["title"]
            assert body["platform_detection"]["platform"] == "greenhouse"
            assert body["cached"] is False

            cached = await client.get(f"/api/job-targets/{job.id}/job-profile")
            assert cached.status_code == 200
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.policy
async def test_login_fixture_creates_human_checkpoint(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module
    from jober_api.models.application_run import ApplicationRun

    jobs = JobTargetRepository(db_session)
    job = await jobs.create(
        company="Gated Co",
        role="Engineer",
        status=JobTargetStatus.NEW,
    )
    await db_session.commit()

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/job-targets/{job.id}/extract",
                json={
                    "fixture_html": load_ats_fixture("login_gate"),
                    "fixture_url": "https://example.com/login",
                    "force": True,
                },
            )
            assert response.status_code == 409, response.text
            detail = response.json()["detail"]
            assert detail["gate"] == "login"
            run_id = detail["run_id"]

            run = await db_session.get(ApplicationRun, uuid.UUID(run_id))
            assert run is not None
            assert run.status == RunStatus.NEEDS_HUMAN

            checkpoints = (
                await db_session.execute(
                    select(HumanCheckpoint).where(HumanCheckpoint.run_id == run.id)
                )
            ).scalars().all()
            assert len(checkpoints) == 1
            assert checkpoints[0].status == CheckpointStatus.OPEN
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.policy
async def test_captcha_fixture_creates_human_checkpoint(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    jobs = JobTargetRepository(db_session)
    job = await jobs.create(
        company="Bot Check Co",
        role="Engineer",
        status=JobTargetStatus.NEW,
    )
    await db_session.commit()

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/job-targets/{job.id}/extract",
                json={
                    "fixture_html": load_ats_fixture("captcha_gate"),
                    "fixture_url": "https://example.com/apply",
                    "force": True,
                },
            )
            assert response.status_code == 409, response.text
            assert response.json()["detail"]["gate"] == "captcha"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_extract_without_apply_url_returns_422(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    jobs = JobTargetRepository(db_session)
    job = await jobs.create(company="No URL Co", role="Eng", status=JobTargetStatus.NEW)
    await db_session.commit()

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(f"/api/job-targets/{job.id}/extract", json={})
            assert response.status_code == 422
            assert "apply url" in response.json()["detail"].casefold()
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_extract_force_bypasses_daily_cache(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    jobs = JobTargetRepository(db_session)
    job = await jobs.create(company="Acme", role="Eng", status=JobTargetStatus.NEW)
    await db_session.commit()
    base_payload = {
        "fixture_html": load_ats_fixture("greenhouse"),
        "fixture_url": "https://boards.greenhouse.io/acme/jobs/1",
    }

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            first = await client.post(f"/api/job-targets/{job.id}/extract", json=base_payload)
            assert first.status_code == 200
            assert first.json()["cached"] is False
            forced = await client.post(
                f"/api/job-targets/{job.id}/extract",
                json={**base_payload, "force": True},
            )
            assert forced.status_code == 200
            assert forced.json()["cached"] is False
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_extract_cache_skips_regeneration(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    jobs = JobTargetRepository(db_session)
    job = await jobs.create(
        company="Acme",
        role="Eng",
        status=JobTargetStatus.NEW,
    )
    await db_session.commit()
    payload = {
        "fixture_html": load_ats_fixture("greenhouse"),
        "fixture_url": "https://boards.greenhouse.io/acme/jobs/1",
    }

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            first = await client.post(f"/api/job-targets/{job.id}/extract", json=payload)
            assert first.status_code == 200
            second = await client.post(f"/api/job-targets/{job.id}/extract", json=payload)
            assert second.status_code == 200
            assert second.json()["cached"] is True
    finally:
        app.dependency_overrides.clear()
