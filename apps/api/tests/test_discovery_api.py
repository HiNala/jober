from __future__ import annotations

import os
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from jober_api.auth.constants import DEFAULT_DEV_TENANT_ID
from jober_api.main import app
from jober_api.models.company_board import CompanyBoard
from jober_api.repositories.job_list import JobListRepository
from jober_api.repositories.resume_asset import ResumeAssetRepository
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
        assert accept.json()["accepted"] == 2

        repo = JobListRepository(db_session, DEFAULT_DEV_TENANT_ID)
        loaded = await repo.get(uuid.UUID(list_id))
        assert loaded is not None
        assert len(loaded.items) == 1
