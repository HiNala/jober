from __future__ import annotations

import os
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from jober_api.auth.constants import DEFAULT_DEV_TENANT_ID, DEFAULT_DEV_USER_ID
from jober_api.main import app
from jober_api.models.enums import JobTargetStatus, PlanTier, RunStatus
from jober_api.models.tenant import Tenant
from jober_api.models.user import User
from jober_api.repositories.application_run import ApplicationRunRepository
from jober_api.repositories.job_target import JobTargetRepository

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres",
)

TENANT_B = uuid.UUID("00000000-0000-4000-8000-000000000099")
USER_B = uuid.UUID("00000000-0000-4000-8000-00000000009a")


@pytest.mark.asyncio
async def test_cross_tenant_job_reads_return_empty_or_404(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    db_session.add(
        Tenant(
            id=TENANT_B,
            name="Tenant B",
            plan=PlanTier.FREE,
            policy={"default_run_policy": "review_before_submit"},
        )
    )
    db_session.add(User(id=USER_B, tenant_id=TENANT_B, email="b@test.local", display_name="User B"))
    await db_session.commit()

    jobs_a = JobTargetRepository(db_session, DEFAULT_DEV_TENANT_ID)
    job_a = await jobs_a.create(company="Tenant A Co", role="Eng", status=JobTargetStatus.NEW)
    jobs_b = JobTargetRepository(db_session, TENANT_B)
    job_b = await jobs_b.create(company="Tenant B Co", role="Eng", status=JobTargetStatus.NEW)
    await db_session.commit()

    assert await JobTargetRepository(db_session, TENANT_B).get(job_a.id) is None
    assert await JobTargetRepository(db_session, DEFAULT_DEV_TENANT_ID).get(job_b.id) is None

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        headers_b = {
            "X-Jober-Tenant-Id": str(TENANT_B),
            "X-Jober-User-Id": str(USER_B),
        }
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            list_a_as_b = await client.get("/api/job-targets", headers=headers_b)
            assert list_a_as_b.status_code == 200
            items = list_a_as_b.json()["items"]
            assert all(item["company"] != "Tenant A Co" for item in items)
            assert any(item["id"] == str(job_b.id) for item in items)

            get_a_as_b = await client.get(f"/api/job-targets/{job_a.id}", headers=headers_b)
            assert get_a_as_b.status_code == 404
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_cross_tenant_export_and_purge_blocked(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    db_session.add(
        Tenant(
            id=TENANT_B,
            name="Tenant B",
            plan=PlanTier.FREE,
            policy={},
        )
    )
    db_session.add(User(id=USER_B, tenant_id=TENANT_B, email="b@test.local", display_name="User B"))
    jobs = JobTargetRepository(db_session, DEFAULT_DEV_TENANT_ID)
    job = await jobs.create(company="Secret Co", role="Eng", status=JobTargetStatus.NEW)
    runs = ApplicationRunRepository(db_session, DEFAULT_DEV_TENANT_ID)
    run = await runs.create(job_target_id=job.id, status=RunStatus.SUCCEEDED)
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
            export_b = await client.get("/api/privacy/export-all", headers=headers_b)
            assert export_b.status_code == 200
            assert export_b.json()["job_targets"] == []

            purge_b = await client.post(f"/api/privacy/runs/{run.id}/purge", headers=headers_b)
            assert purge_b.status_code == 404

            export_a = await client.get(
                "/api/privacy/export-all",
                headers={
                    "X-Jober-Tenant-Id": str(DEFAULT_DEV_TENANT_ID),
                    "X-Jober-User-Id": str(DEFAULT_DEV_USER_ID),
                },
            )
            assert len(export_a.json()["job_targets"]) == 1
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_cross_tenant_documents_blocked(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module
    from jober_api.models.enums import DocumentType
    from jober_api.models.generated_document import GeneratedDocument

    db_session.add(
        Tenant(
            id=TENANT_B,
            name="Tenant B",
            plan=PlanTier.FREE,
            policy={},
        )
    )
    db_session.add(
        User(id=USER_B, tenant_id=TENANT_B, email="b@test.local", display_name="User B")
    )
    jobs = JobTargetRepository(db_session, DEFAULT_DEV_TENANT_ID)
    job = await jobs.create(company="Doc Co", role="Eng", status=JobTargetStatus.NEW)
    db_session.add(
        GeneratedDocument(
            job_target_id=job.id,
            document_type=DocumentType.COVER_LETTER,
            text="Hello",
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
            listing = await client.get(
                f"/api/documents?job_target_id={job.id}",
                headers=headers_b,
            )
            assert listing.status_code == 404
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_cross_tenant_run_console_blocked(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    db_session.add(
        Tenant(
            id=TENANT_B,
            name="Tenant B",
            plan=PlanTier.FREE,
            policy={},
        )
    )
    db_session.add(
        User(id=USER_B, tenant_id=TENANT_B, email="b@test.local", display_name="User B")
    )
    jobs = JobTargetRepository(db_session, DEFAULT_DEV_TENANT_ID)
    job = await jobs.create(company="Run Co", role="Eng", status=JobTargetStatus.NEW)
    runs = ApplicationRunRepository(db_session, DEFAULT_DEV_TENANT_ID)
    run = await runs.create(job_target_id=job.id, status=RunStatus.QUEUED)
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
            res = await client.get(f"/api/application-runs/{run.id}/console", headers=headers_b)
            assert res.status_code == 404
    finally:
        app.dependency_overrides.clear()
