from __future__ import annotations

import os
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from jober_api.auth.constants import DEFAULT_DEV_TENANT_ID, DEFAULT_DEV_USER_ID
from jober_api.main import app
from jober_api.models.company_board import CompanyBoard
from jober_api.models.enums import JobTargetStatus
from jober_api.models.job_list import JobList, JobListItem
from jober_api.models.job_target import JobTarget
from jober_api.repositories.job_list import JobListRepository
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.repositories.resume_asset import ResumeAssetRepository
from jober_api.services.batch.service import preview_batch
from jober_api.services.claims_index import build_claims_index
from tests.fixtures.ats_pages import load_ats_fixture

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres",
)


@pytest.mark.asyncio
async def test_discovery_search_returns_board_candidates(
    db_session,
    truncate_tables,
    auth_headers,
    monkeypatch,
) -> None:
    board_html = load_ats_fixture("board_listing")
    db_session.add(
        CompanyBoard(
            id=uuid.uuid4(),
            tenant_id=DEFAULT_DEV_TENANT_ID,
            company_board="Beacon Labs",
            company_careers_url="https://example.com/careers/beacon",
            stage_signal="Series B",
            representative_roles="Staff Engineer",
        )
    )
    text = "Python TypeScript React FastAPI"
    resumes = ResumeAssetRepository(db_session, DEFAULT_DEV_TENANT_ID)
    await resumes.create(
        object_key="resume-key",
        original_filename="resume.docx",
        extracted_text=text,
        skills_index={
            "skills": ["Python", "TypeScript", "React"],
            "claims_index": build_claims_index(text, {"skills": ["Python", "TypeScript", "React"]}),
        },
        is_active=True,
    )
    await db_session.commit()

    async def _fake_fetch(url: str, *, fixture_html: str | None = None):
        return board_html

    monkeypatch.setattr(
        "jober_api.services.discovery.service.fetch_board_html",
        _fake_fetch,
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/discovery/search",
            headers=auth_headers,
            json={"role": "Engineer", "stack": ["Python"]},
        )
        assert resp.status_code == 200
        candidates = resp.json()["candidates"]
        assert len(candidates) >= 2
        assert any(c["source"] == "board" for c in candidates)
        assert any(c.get("fit_score") is not None for c in candidates)
        with_reasons = [c for c in candidates if c.get("fit_reasons")]
        assert with_reasons, "expected fit_reasons on scored candidates"
        assert all(isinstance(c.get("fit_reasons"), list) for c in candidates)


@pytest.mark.asyncio
async def test_discovery_accept_dedupes_and_adds_to_list(
    db_session,
    truncate_tables,
    auth_headers,
    monkeypatch,
) -> None:
    async def _noop_enrich(*_args, **_kwargs):
        return None

    monkeypatch.setattr(
        "jober_api.services.discovery.service.enrich_job_target_inline",
        _noop_enrich,
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        list_resp = await client.post(
            "/api/job-lists",
            headers=auth_headers,
            json={"name": "Priority A"},
        )
        list_id = list_resp.json()["id"]
        candidate = {
            "candidate_key": "acme|staff engineer|https://jobs.lever.co/acme/staff",
            "company": "Acme",
            "role": "Staff Engineer",
            "direct_apply_url": "https://jobs.lever.co/acme/staff",
            "company_careers_url": None,
            "source": "board",
            "source_label": "Acme board",
            "stage_signal": None,
            "location_work_style": None,
            "fit_score": 80.0,
            "existing_job_target_id": None,
        }
        accept = await client.post(
            "/api/discovery/accept",
            headers=auth_headers,
            json={"list_id": list_id, "candidates": [candidate, candidate]},
        )
        assert accept.status_code == 200
        body = accept.json()
        assert body["accepted"] == 1
        assert body.get("skipped_duplicates") == 1

        repo = JobListRepository(db_session, DEFAULT_DEV_TENANT_ID)
        loaded = await repo.get(uuid.UUID(list_id))
        assert loaded is not None
        assert len(loaded.items) == 1


@pytest.mark.asyncio
async def test_discovery_refresh_returns_only_new_candidates(
    db_session,
    truncate_tables,
    auth_headers,
    monkeypatch,
) -> None:
    board_html = load_ats_fixture("board_listing")
    db_session.add(
        CompanyBoard(
            id=uuid.uuid4(),
            tenant_id=DEFAULT_DEV_TENANT_ID,
            company_board="Beacon Labs",
            company_careers_url="https://example.com/careers/beacon",
            stage_signal="Series B",
            representative_roles="Staff Engineer",
        )
    )
    await db_session.commit()

    async def _fake_fetch(url: str, *, fixture_html: str | None = None):
        return board_html

    monkeypatch.setattr(
        "jober_api.services.discovery.service.fetch_board_html",
        _fake_fetch,
    )

    async def _noop_enrich(*_args, **_kwargs):
        return None

    monkeypatch.setattr(
        "jober_api.services.discovery.service.enrich_job_target_inline",
        _noop_enrich,
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        list_resp = await client.post(
            "/api/job-lists",
            headers=auth_headers,
            json={"name": "Refresh target"},
        )
        list_id = list_resp.json()["id"]
        search = await client.post(
            "/api/discovery/search",
            headers=auth_headers,
            json={"role": "Engineer"},
        )
        candidates = search.json()["candidates"]
        assert len(candidates) >= 2
        accept = await client.post(
            "/api/discovery/accept",
            headers=auth_headers,
            json={"list_id": list_id, "candidates": [candidates[0]]},
        )
        assert accept.status_code == 200

        refresh = await client.post(
            f"/api/discovery/lists/{list_id}/refresh",
            headers=auth_headers,
        )
        assert refresh.status_code == 200
        refreshed = refresh.json()["candidates"]
        accepted_key = candidates[0]["candidate_key"]
        assert all(row["candidate_key"] != accepted_key for row in refreshed)
        assert len(refreshed) >= 1


@pytest.mark.asyncio
async def test_discovery_saved_search_linked_to_list_refresh(
    db_session,
    truncate_tables,
    auth_headers,
    monkeypatch,
) -> None:
    board_html = load_ats_fixture("board_listing")
    db_session.add(
        CompanyBoard(
            id=uuid.uuid4(),
            tenant_id=DEFAULT_DEV_TENANT_ID,
            company_board="Beacon Labs",
            company_careers_url="https://example.com/careers/beacon",
            representative_roles="Staff Engineer",
        )
    )
    await db_session.commit()

    async def _fake_fetch(url: str, *, fixture_html: str | None = None):
        return board_html

    monkeypatch.setattr(
        "jober_api.services.discovery.service.fetch_board_html",
        _fake_fetch,
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        saved = await client.post(
            "/api/discovery/saved-searches",
            headers=auth_headers,
            json={"name": "Beacon eng", "query": {"role": "Engineer"}},
        )
        assert saved.status_code == 200
        saved_id = saved.json()["id"]

        listed = await client.get("/api/discovery/saved-searches", headers=auth_headers)
        assert listed.status_code == 200
        assert any(row["id"] == saved_id for row in listed.json()["items"])

        list_resp = await client.post(
            "/api/job-lists",
            headers=auth_headers,
            json={"name": "Saved search list"},
        )
        list_id = list_resp.json()["id"]
        link = await client.patch(
            f"/api/discovery/lists/{list_id}/saved-search",
            headers=auth_headers,
            json={"saved_search_id": saved_id},
        )
        assert link.status_code == 200

        refresh = await client.post(
            f"/api/discovery/lists/{list_id}/refresh",
            headers=auth_headers,
        )
        assert refresh.status_code == 200
        assert len(refresh.json()["candidates"]) >= 1


@pytest.mark.asyncio
async def test_discovery_attach_import_to_list(
    db_session,
    truncate_tables,
    auth_headers,
) -> None:
    import_id = "import-m23-test"
    job_a = JobTarget(
        id=uuid.uuid4(),
        tenant_id=DEFAULT_DEV_TENANT_ID,
        company="Import Co",
        role="Backend Engineer",
        direct_apply_url="https://jobs.lever.co/import/backend",
        status=JobTargetStatus.NEW,
        import_id=import_id,
    )
    job_b = JobTarget(
        id=uuid.uuid4(),
        tenant_id=DEFAULT_DEV_TENANT_ID,
        company="Import Co",
        role="Platform Engineer",
        direct_apply_url="https://jobs.lever.co/import/platform",
        status=JobTargetStatus.NEW,
        import_id=import_id,
    )
    db_session.add_all([job_a, job_b])
    await db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        list_resp = await client.post(
            "/api/job-lists",
            headers=auth_headers,
            json={"name": "Import list"},
        )
        list_id = list_resp.json()["id"]
        attach = await client.post(
            f"/api/discovery/lists/{list_id}/attach-import",
            headers=auth_headers,
            params={"import_id": import_id},
        )
        assert attach.status_code == 200
        assert attach.json()["attached"] == 2

        repo = JobListRepository(db_session, DEFAULT_DEV_TENANT_ID)
        loaded = await repo.get(uuid.UUID(list_id))
        assert loaded is not None
        assert len(loaded.items) == 2


@pytest.mark.asyncio
async def test_batch_preview_filters_by_job_list_id(
    db_session,
    truncate_tables,
) -> None:
    jobs = JobTargetRepository(db_session, DEFAULT_DEV_TENANT_ID)
    in_list = await jobs.create(
        company="Listed Co",
        role="Eng",
        status=JobTargetStatus.NEW,
        priority="A",
        direct_apply_url="https://jobs.lever.co/listed/eng",
    )
    await jobs.create(
        company="Other Co",
        role="Eng",
        status=JobTargetStatus.NEW,
        priority="A",
        direct_apply_url="https://jobs.lever.co/other/eng",
    )
    list_id = uuid.uuid4()
    db_session.add(
        JobList(
            id=list_id,
            tenant_id=DEFAULT_DEV_TENANT_ID,
            user_id=DEFAULT_DEV_USER_ID,
            name="Batch filter list",
        )
    )
    db_session.add(
        JobListItem(
            id=uuid.uuid4(),
            job_list_id=list_id,
            job_target_id=in_list.id,
            sort_order=0,
        )
    )
    await db_session.commit()

    preview = await preview_batch(
        db_session,
        {"job_list_id": str(list_id), "status": "new", "limit": 50},
        DEFAULT_DEV_TENANT_ID,
    )
    assert len(preview["included"]) == 1
    assert preview["included"][0]["company"] == "Listed Co"
