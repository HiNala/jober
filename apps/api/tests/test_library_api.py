from __future__ import annotations

import os

import pytest
from httpx import ASGITransport, AsyncClient

from jober_api.auth.constants import DEFAULT_DEV_TENANT_ID
from jober_api.main import app
from jober_api.models.enums import JobTargetStatus
from jober_api.repositories.job_target import JobTargetRepository

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres",
)


@pytest.mark.asyncio
async def test_library_search_finds_job_target(
    db_session,
    truncate_tables,
    auth_headers,
) -> None:
    jobs = JobTargetRepository(db_session, DEFAULT_DEV_TENANT_ID)
    job = await jobs.create(
        company="Acme Robotics",
        role="Staff Engineer",
        status=JobTargetStatus.NEW,
    )
    await db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            "/api/library/search",
            params={"q": "Robotics"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert any(item["id"] == str(job.id) for item in body["jobs"])


@pytest.mark.asyncio
async def test_job_list_archive_round_trip(
    db_session,
    truncate_tables,
    auth_headers,
) -> None:
    del db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create = await client.post(
            "/api/job-lists",
            headers=auth_headers,
            json={"name": "Priority A"},
        )
        assert create.status_code == 200
        list_id = create.json()["id"]

        archive = await client.patch(
            f"/api/job-lists/{list_id}",
            headers=auth_headers,
            json={"archived": True},
        )
        assert archive.status_code == 200
        assert archive.json()["archived"] is True

        active = await client.get("/api/job-lists", headers=auth_headers)
        assert all(item["id"] != list_id for item in active.json()["items"])

        with_archived = await client.get(
            "/api/job-lists",
            params={"include_archived": "true"},
            headers=auth_headers,
        )
        assert any(item["id"] == list_id for item in with_archived.json()["items"])
