"""Mission 21 security probes — regression tests for documented controls."""

from __future__ import annotations

import asyncio
import os
import uuid
from datetime import timedelta

import httpx
import pytest
from httpx import ASGITransport, AsyncClient

from jober_api.auth.constants import DEFAULT_DEV_TENANT_ID
from jober_api.main import app
from jober_api.models.enums import JobTargetStatus, PlanTier
from jober_api.models.tenant import Tenant
from jober_api.models.user import User
from jober_api.models.user_profile import UserProfile
from jober_api.privacy.redaction import scrub_text
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.storage.minio_client import ObjectStorage
from jober_api.vault.fill_policy import FillOutcome, resolve_field_fill
from jober_api.vault.sensitive_store import merge_sensitive_answers

pytestmark = pytest.mark.policy

requires_postgres = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres",
)

TENANT_B = uuid.UUID("00000000-0000-4000-8000-000000000099")
USER_B = uuid.UUID("00000000-0000-4000-8000-00000000009a")
_FAKE_SK = "sk-FAKE-test-key-abcdefghijklmnop"


def test_scrub_text_redacted_mode_truncates() -> None:
    scrubbed = scrub_text("a" * 500, debug=False)
    assert len(scrubbed) <= 401


def test_scrub_text_debug_allows_longer_but_masks_secrets() -> None:
    raw = "a" * 500 + f" token={_FAKE_SK}"
    scrubbed = scrub_text(raw, debug=True)
    assert _FAKE_SK not in scrubbed
    assert len(scrubbed) > 400


def test_sensitive_fill_refused_without_consent() -> None:
    profile = UserProfile()
    merge_sensitive_answers(profile, {"disability": "prefer_not_to_answer"})
    profile.field_consent = {}
    resolution = resolve_field_fill(profile, "disability")
    assert resolution.outcome == FillOutcome.NEEDS_HUMAN


@pytest.mark.asyncio
async def test_api_responses_include_security_headers() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/healthz")
    assert response.status_code == 200
    assert response.headers.get("x-content-type-options") == "nosniff"
    assert response.headers.get("referrer-policy") == "strict-origin-when-cross-origin"
    assert response.headers.get("x-frame-options") == "DENY"


@pytest.mark.asyncio
async def test_stripe_webhook_rejects_invalid_signature(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from jober_api.config import settings

    monkeypatch.setattr(settings, "stripe_webhook_secret", "whsec_FAKE_test_secret_value")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/webhooks/stripe",
            content=b'{"id":"evt_fake"}',
            headers={"Stripe-Signature": "t=0,v1=invalid"},
        )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid Stripe signature"
    assert "whsec" not in response.text


@requires_postgres
@pytest.mark.asyncio
async def test_cross_tenant_resume_activate_blocked(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module
    from jober_api.models.resume_asset import ResumeAsset

    db_session.add(
        Tenant(id=TENANT_B, name="Tenant B", plan=PlanTier.FREE, policy={})
    )
    db_session.add(User(id=USER_B, tenant_id=TENANT_B, email="b@test.local"))
    asset_id = uuid.uuid4()
    db_session.add(
        ResumeAsset(
            id=asset_id,
            tenant_id=DEFAULT_DEV_TENANT_ID,
            object_key=f"tenants/{DEFAULT_DEV_TENANT_ID}/resumes/{asset_id}/cv.pdf",
            original_filename="cv.pdf",
            is_active=False,
        )
    )
    await db_session.commit()

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    headers_b = {
        "X-Jober-Tenant-Id": str(TENANT_B),
        "X-Jober-User-Id": str(USER_B),
    }
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/resumes/{asset_id}/activate",
                headers=headers_b,
            )
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


@requires_postgres
@pytest.mark.asyncio
async def test_cross_tenant_library_search_excludes_other_tenant(
    db_session, truncate_tables
) -> None:
    from jober_api.db import session as db_session_module

    db_session.add(
        Tenant(id=TENANT_B, name="Tenant B", plan=PlanTier.FREE, policy={})
    )
    db_session.add(User(id=USER_B, tenant_id=TENANT_B, email="b@test.local"))
    jobs = JobTargetRepository(db_session, DEFAULT_DEV_TENANT_ID)
    await jobs.create(company="Library A Co", role="Eng", status=JobTargetStatus.NEW)
    await db_session.commit()

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    headers_b = {
        "X-Jober-Tenant-Id": str(TENANT_B),
        "X-Jober-User-Id": str(USER_B),
    }
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/api/library/search",
                params={"q": "Library"},
                headers=headers_b,
            )
        assert response.status_code == 200
        body = response.json()
        companies = {job.get("company") for job in body.get("jobs", [])}
        assert "Library A Co" not in companies
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_presigned_url_expires_after_ttl() -> None:
    if os.getenv("CI") != "true" and os.getenv("RUN_INTEGRATION") != "1":
        pytest.skip("requires MinIO")

    storage = ObjectStorage()
    key = f"test/expiry-{uuid.uuid4()}.txt"
    await storage.put_object(key, b"ttl-probe")
    url = await storage.presigned_get(key, expires=timedelta(seconds=1))
    await asyncio.sleep(2)
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    assert response.status_code in (403, 404)
    await storage.remove_object(key)
