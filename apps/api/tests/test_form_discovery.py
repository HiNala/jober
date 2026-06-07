from __future__ import annotations

import os

import pytest
from httpx import ASGITransport, AsyncClient
from jober_forms.scanner import scan_multistep_form

from jober_api.main import app
from jober_api.models.enums import JobTargetStatus
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.repositories.user_profile import UserProfileRepository
from tests.fixtures.form_pages import load_form_fixture

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres",
)


def test_scanner_finds_upload_controls() -> None:
    html = load_form_fixture("dropzone")
    fields = scan_multistep_form(html)
    uploads = [f for f in fields if f.is_upload]
    assert len(uploads) >= 2
    assert any("resume" in (f.label or "").casefold() for f in uploads)


def test_scanner_marks_required_fields() -> None:
    html = load_form_fixture("required_validation")
    fields = scan_multistep_form(html)
    email = next(f for f in fields if f.field_key == "email")
    role = next(f for f in fields if f.field_key == "role")
    assert email.required is True
    assert role.required is False


def test_scanner_detects_combobox_role() -> None:
    html = load_form_fixture("combobox")
    fields = scan_multistep_form(html)
    combobox = next(f for f in fields if f.field_type == "combobox")
    assert combobox.label == "Department"


@pytest.mark.asyncio
async def test_low_confidence_field_needs_review(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    jobs = JobTargetRepository(db_session)
    job = await jobs.create(company="Acme", role="Eng", status=JobTargetStatus.NEW)
    await db_session.commit()

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        html = """
        <form>
          <label for="q1">Tell us something unique about your favorite color</label>
          <input id="q1" name="q1" type="text" />
        </form>
        """
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/job-targets/{job.id}/discover-form",
                json={"fixture_html": html, "platform": "generic"},
            )
            assert response.status_code == 200
            item = response.json()["items"][0]
            assert item["status"] == "needs_review"
            assert (item["confidence"] or 0) < 0.82
    finally:
        app.dependency_overrides.clear()


def test_multistep_scanner_assigns_steps() -> None:
    html = load_form_fixture("multi_step")
    fields = scan_multistep_form(html)
    steps = {f.step_index for f in fields}
    assert len(steps) >= 1
    assert len(fields) >= 2


@pytest.mark.asyncio
async def test_discover_form_requires_fixture_html(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    jobs = JobTargetRepository(db_session)
    job = await jobs.create(company="Acme", role="Eng", status=JobTargetStatus.NEW)
    await db_session.commit()

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(f"/api/job-targets/{job.id}/discover-form", json={})
            assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_discover_single_step_form(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    jobs = JobTargetRepository(db_session)
    job = await jobs.create(company="Acme", role="Eng", status=JobTargetStatus.NEW)
    profiles = UserProfileRepository(db_session)
    await profiles.create(name="Brian", email="brian@example.com", phone="555-0100")
    await db_session.commit()

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/job-targets/{job.id}/discover-form",
                json={"fixture_html": load_form_fixture("single_step"), "platform": "greenhouse"},
            )
            assert response.status_code == 200, response.text
            body = response.json()
            assert len(body["items"]) >= 3
            email = next(i for i in body["items"] if i["mapped_profile_field"] == "email")
            assert email["confidence"] >= 0.8
            assert email["proposed_value_redacted"]
            assert "@" in email["proposed_value_redacted"]
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_sensitive_fields_need_review_even_with_profile(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    jobs = JobTargetRepository(db_session)
    job = await jobs.create(company="Acme", role="Eng", status=JobTargetStatus.NEW)
    await db_session.commit()

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/job-targets/{job.id}/discover-form",
                json={"fixture_html": load_form_fixture("sensitive_eeo"), "platform": "greenhouse"},
            )
            assert response.status_code == 200
            items = response.json()["items"]
            veteran = next(i for i in items if i["mapped_profile_field"] == "veteran_status")
            assert veteran["status"] == "needs_review"
            salary = next(i for i in items if i["mapped_profile_field"] == "salary_prefs")
            assert salary["status"] == "needs_review"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_mapping_memory_boosts_confidence(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module
    from jober_api.repositories.field_mapping_memory import FieldMappingMemoryRepository

    jobs = JobTargetRepository(db_session)
    job = await jobs.create(company="Acme", role="Eng", status=JobTargetStatus.NEW)
    memory = FieldMappingMemoryRepository(db_session)
    await memory.remember("greenhouse", "Custom employee ID", "name")
    await db_session.commit()

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        html = """
        <form><label for="emp">Custom employee ID</label>
        <input id="emp" name="emp" type="text" /></form>
        """
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/job-targets/{job.id}/discover-form",
                json={"fixture_html": html, "platform": "greenhouse"},
            )
            assert response.status_code == 200
            item = response.json()["items"][0]
            assert item["mapped_profile_field"] == "name"
            assert item["confidence"] >= 0.9
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_patch_observation_remember_mapping(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    jobs = JobTargetRepository(db_session)
    job = await jobs.create(company="Acme", role="Eng", status=JobTargetStatus.NEW)
    await db_session.commit()

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            discover = await client.post(
                f"/api/job-targets/{job.id}/discover-form",
                json={"fixture_html": load_form_fixture("single_step"), "platform": "lever"},
            )
            obs_id = discover.json()["items"][0]["id"]
            patched = await client.patch(
                f"/api/job-targets/field-observations/{obs_id}",
                json={
                    "mapped_profile_field": "email",
                    "status": "needs_review",
                    "remember": True,
                    "platform": "lever",
                },
            )
            assert patched.status_code == 200
    finally:
        app.dependency_overrides.clear()
