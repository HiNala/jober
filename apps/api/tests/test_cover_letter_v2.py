from __future__ import annotations

import os
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from jober_api.auth.constants import DEFAULT_DEV_TENANT_ID, DEFAULT_DEV_USER_ID
from jober_api.config import settings
from jober_api.db import session as db_session_module
from jober_api.main import app
from jober_api.models.application_attempt import ApplicationAttempt
from jober_api.models.application_run import ApplicationRun
from jober_api.models.enums import AttemptStatus, FieldObservationStatus, JobTargetStatus, RunStatus
from jober_api.models.form_field_observation import FormFieldObservation
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.repositories.resume_asset import ResumeAssetRepository
from jober_api.repositories.user_preferences import UserPreferencesRepository
from jober_api.repositories.user_profile import UserProfileRepository
from jober_api.services.claims_index import build_claims_index
from jober_api.services.documents.cover_letter_generator import generate_cover_letter
from jober_api.services.documents.letter_editor import merge_paragraphs
from jober_api.services.documents.letter_styles import voice_prompt
from jober_api.services.documents.render_pdf import render_cover_letter_pdf
from jober_api.services.documents.run_documents import should_generate_for_run
from jober_api.services.preferences.defaults import merged_preferences
from jober_api.storage.minio_client import ObjectStorage

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres",
)


def test_voice_presets_are_distinct() -> None:
    direct = voice_prompt("direct")
    founder = voice_prompt("founder_operator")
    assert direct != founder
    assert "founder" in founder.casefold()


def test_merge_paragraphs_preserves_locked() -> None:
    original = ["Opener", "Evidence", "Close"]
    updated = ["New opener", "New evidence", "New close"]
    merged = merge_paragraphs(
        original=original,
        updated=updated,
        locked_indices={1},
    )
    assert merged == ["New opener", "Evidence", "New close"]


@pytest.mark.asyncio
async def test_patch_cover_letter_text_updates_ats_score(
    db_session,
    truncate_tables,
    monkeypatch,
) -> None:
    async def _fake_put(self, key, data, content_type="application/octet-stream", length=None):
        from jober_api.storage.minio_client import StoredObject

        return StoredObject(bucket="test", key=key, etag="1")

    monkeypatch.setattr(ObjectStorage, "put_object", _fake_put)
    monkeypatch.setattr(settings, "llm_provider", "template")

    profiles = UserProfileRepository(db_session, DEFAULT_DEV_TENANT_ID)
    await profiles.get_singleton()
    resumes = ResumeAssetRepository(db_session, DEFAULT_DEV_TENANT_ID)
    text = "Python FastAPI React"
    await resumes.create(
        object_key="resume-key",
        original_filename="resume.docx",
        extracted_text=text,
        skills_index={
            "skills": ["Python", "FastAPI"],
            "claims_index": build_claims_index(text, {"skills": ["Python", "FastAPI"]}),
        },
        is_active=True,
    )
    jobs = JobTargetRepository(db_session, DEFAULT_DEV_TENANT_ID)
    job = await jobs.create(
        company="Acme",
        role="Engineer",
        status=JobTargetStatus.NEW,
        direct_apply_url="https://jobs.lever.co/acme/eng",
        extracted_job_profile={
            "description": "Python FastAPI platform",
            "requirements": ["Python"],
        },
    )
    await db_session.commit()

    generated = await generate_cover_letter(
        db_session,
        ObjectStorage(),
        tenant_id=DEFAULT_DEV_TENANT_ID,
        user_id=DEFAULT_DEV_USER_ID,
        job_target_id=job.id,
        force=True,
    )
    original_score = generated["ats_score"]

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        edited = (
            "Dear team,\n\n"
            "I have delivered Python and FastAPI services in production with measurable impact.\n\n"
            "Thank you for your consideration."
        )
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.patch(
                f"/api/documents/{generated['id']}",
                json={"text": edited},
            )
            assert response.status_code == 200
            body = response.json()
            assert body["text"] == edited
            assert body["ats_score"] is not None
            assert body["keyword_coverage"]["manual_edit"] is True
            assert body["ats_score"] != original_score or body["keyword_coverage"]["present"]
    finally:
        app.dependency_overrides.clear()


def test_template_pdf_still_selectable_text() -> None:
    for template in ("classic", "modern", "compact"):
        pdf = render_cover_letter_pdf(
            body="Hello team.\n\nI build with Python.",
            applicant_name="Alex",
            company="Acme",
            role="Engineer",
            template=template,
        )
        assert pdf.startswith(b"%PDF")


@pytest.mark.asyncio
async def test_should_skip_when_global_toggle_off(db_session, truncate_tables) -> None:
    prefs = UserPreferencesRepository(db_session)
    row = await prefs.get_or_create(DEFAULT_DEV_USER_ID)
    row.prefs = merged_preferences(
        {
            "application_defaults": {
                "generate_cover_letter_per_run": False,
            }
        }
    )
    jobs = JobTargetRepository(db_session, DEFAULT_DEV_TENANT_ID)
    job = await jobs.create(
        company="Co",
        role="Eng",
        status=JobTargetStatus.NEW,
        direct_apply_url="https://jobs.lever.co/co/eng",
    )
    await db_session.commit()
    should, _ = await should_generate_for_run(
        db_session,
        tenant_id=DEFAULT_DEV_TENANT_ID,
        user_id=DEFAULT_DEV_USER_ID,
        batch_filters=None,
        run_checkpoint=None,
        job_target_id=job.id,
    )
    assert should is False


@pytest.mark.asyncio
async def test_should_skip_when_form_has_no_cover_letter_field(
    db_session,
    truncate_tables,
) -> None:
    jobs = JobTargetRepository(db_session, DEFAULT_DEV_TENANT_ID)
    job = await jobs.create(
        company="Co",
        role="Eng",
        status=JobTargetStatus.NEW,
        direct_apply_url="https://jobs.lever.co/co/eng",
    )
    run = ApplicationRun(
        id=uuid.uuid4(),
        tenant_id=DEFAULT_DEV_TENANT_ID,
        job_target_id=job.id,
        status=RunStatus.QUEUED,
    )
    attempt = ApplicationAttempt(
        id=uuid.uuid4(),
        run_id=run.id,
        attempt_index=0,
        status=AttemptStatus.SUCCEEDED,
    )
    observation = FormFieldObservation(
        id=uuid.uuid4(),
        attempt_id=attempt.id,
        field_key="email",
        label="Email",
        field_type="text",
        status=FieldObservationStatus.SKIPPED,
    )
    db_session.add_all([run, attempt, observation])
    await db_session.commit()
    should, _ = await should_generate_for_run(
        db_session,
        tenant_id=DEFAULT_DEV_TENANT_ID,
        user_id=DEFAULT_DEV_USER_ID,
        batch_filters=None,
        run_checkpoint=None,
        job_target_id=job.id,
        observations_attempt_id=attempt.id,
    )
    assert should is False


@pytest.mark.asyncio
async def test_generate_stores_template_voice_and_run_id(
    db_session,
    truncate_tables,
    monkeypatch,
) -> None:
    async def _fake_put(self, key, data, content_type="application/octet-stream", length=None):
        from jober_api.storage.minio_client import StoredObject

        return StoredObject(bucket="test", key=key, etag="1")

    monkeypatch.setattr(ObjectStorage, "put_object", _fake_put)
    monkeypatch.setattr(settings, "llm_provider", "template")

    profiles = UserProfileRepository(db_session, DEFAULT_DEV_TENANT_ID)
    await profiles.get_singleton()
    resumes = ResumeAssetRepository(db_session, DEFAULT_DEV_TENANT_ID)
    text = "Python FastAPI React Docker"
    await resumes.create(
        object_key="resume-key",
        original_filename="resume.docx",
        extracted_text=text,
        skills_index={
            "skills": ["Python", "FastAPI"],
            "claims_index": build_claims_index(text, {"skills": ["Python", "FastAPI"]}),
        },
        is_active=True,
    )
    jobs = JobTargetRepository(db_session, DEFAULT_DEV_TENANT_ID)
    job = await jobs.create(
        company="Beacon",
        role="Staff Engineer",
        status=JobTargetStatus.NEW,
        direct_apply_url="https://jobs.lever.co/beacon/staff",
        cover_letter_hook="AI platform",
        extracted_job_profile={
            "description": "Build AI platform",
            "company_product_summary": "Beacon builds recruiting AI",
            "requirements": ["Python", "FastAPI"],
        },
    )
    run_id = uuid.uuid4()
    db_session.add(
        ApplicationRun(
            id=run_id,
            tenant_id=DEFAULT_DEV_TENANT_ID,
            job_target_id=job.id,
            status=RunStatus.GENERATE_DOCUMENTS,
        )
    )
    await db_session.commit()

    result = await generate_cover_letter(
        db_session,
        ObjectStorage(),
        tenant_id=DEFAULT_DEV_TENANT_ID,
        user_id=DEFAULT_DEV_USER_ID,
        job_target_id=job.id,
        force=True,
        run_id=run_id,
        template_style="modern",
        voice_preset="founder_operator",
    )
    assert result["template_style"] == "modern"
    assert result["voice_preset"] == "founder_operator"
    assert result["run_id"] == str(run_id)
    meta = result["keyword_coverage"]
    assert meta["ab_tracking"]["template_style"] == "modern"
    assert meta["ab_tracking"]["voice_preset"] == "founder_operator"
