from __future__ import annotations

import os

import pytest
from httpx import ASGITransport, AsyncClient

from jober_api.config import settings
from jober_api.main import app
from jober_api.models.enums import JobTargetStatus
from jober_api.models.llm_call import LlmCall
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.repositories.resume_asset import ResumeAssetRepository
from jober_api.repositories.user_profile import UserProfileRepository
from jober_api.services.claims_index import build_claims_index
from jober_api.storage.minio_client import ObjectStorage

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres",
)


@pytest.mark.asyncio
async def test_generate_cover_letter_endpoint_returns_pdf_path(
    db_session,
    truncate_tables,
    monkeypatch,
) -> None:
    from jober_api.db import session as db_session_module

    stored: dict[str, bytes] = {}

    async def _fake_put(self, key, data, content_type="application/octet-stream", length=None):
        stored[key] = bytes(data)
        from jober_api.storage.minio_client import StoredObject

        return StoredObject(bucket="test", key=key, etag="1")

    async def _fake_get(self, key):
        return stored[key]

    monkeypatch.setattr(ObjectStorage, "put_object", _fake_put)
    monkeypatch.setattr(ObjectStorage, "get_bytes", _fake_get)
    monkeypatch.setattr(settings, "llm_provider", "template")
    monkeypatch.setattr(settings, "llm_monthly_budget_usd", 100.0)

    profiles = UserProfileRepository(db_session)
    await profiles.create(name="Brian Permut", email="brian@example.com")
    jobs = JobTargetRepository(db_session)
    job = await jobs.create(
        company="Acme AI",
        role="Staff Engineer",
        fit_lane="AI platform",
        cover_letter_hook="Built agent stack end-to-end",
        status=JobTargetStatus.NEW,
    )
    resumes = ResumeAssetRepository(db_session)
    text = "Brian built Python FastAPI systems with RAG and Docker."
    await resumes.create(
        object_key="resumes/test/resume.docx",
        original_filename="resume.docx",
        extracted_text=text,
        skills_index={
            "skills": ["Python", "FastAPI", "RAG", "Docker"],
            "claims_index": build_claims_index(
                text,
                {"skills": ["Python", "FastAPI", "RAG", "Docker"]},
            ),
        },
        is_active=True,
    )
    await db_session.commit()

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/documents/generate-cover-letter",
                json={"job_target_id": str(job.id), "force": True},
            )
            assert response.status_code == 200, response.text
            body = response.json()
            assert body["document_type"] == "cover_letter"
            assert body["pdf_download_path"].startswith("/api/documents/")
            assert body["keyword_coverage"]["explain"]

            pdf = await client.get(body["pdf_download_path"])
            assert pdf.status_code == 200
            assert pdf.content.startswith(b"%PDF")
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_generate_cover_letter_budget_exceeded_returns_402(
    db_session,
    truncate_tables,
    monkeypatch,
) -> None:
    from jober_api.db import session as db_session_module

    monkeypatch.setattr(settings, "llm_provider", "template")
    monkeypatch.setattr(settings, "llm_monthly_budget_usd", 0.01)
    db_session.add(
        LlmCall(
            agent_role="prior",
            provider="template",
            model="test",
            cost_usd=0.02,
        )
    )

    profiles = UserProfileRepository(db_session)
    await profiles.create(name="Brian", email="brian@example.com")
    jobs = JobTargetRepository(db_session)
    job = await jobs.create(company="Acme", role="Eng", status=JobTargetStatus.NEW)
    resumes = ResumeAssetRepository(db_session)
    text = "Python developer"
    await resumes.create(
        object_key="k",
        original_filename="r.docx",
        extracted_text=text,
        skills_index={
            "skills": ["Python"],
            "claims_index": build_claims_index(text, {"skills": ["Python"]}),
        },
        is_active=True,
    )
    await db_session.commit()

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/documents/generate-cover-letter",
                json={"job_target_id": str(job.id), "force": True},
            )
            assert response.status_code == 402, response.text
            body = response.json()
            assert body.get("code") == "llm_budget_exceeded"
            detail = body["detail"]
            message = detail["message"] if isinstance(detail, dict) else detail
            assert "budget" in str(message).casefold()
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_letter_options_lists_templates_and_voices(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/documents/letter-options")
            assert response.status_code == 200
            body = response.json()
            assert "classic" in body["templates"]
            assert "direct" in body["voice_presets"]
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_generate_cover_letter_without_resume_returns_422(
    db_session,
    truncate_tables,
) -> None:
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
                "/api/documents/generate-cover-letter",
                json={"job_target_id": str(job.id)},
            )
            assert response.status_code == 422
            assert "resume" in response.json()["detail"].casefold()
    finally:
        app.dependency_overrides.clear()
