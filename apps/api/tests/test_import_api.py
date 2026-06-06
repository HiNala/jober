from __future__ import annotations

import os

import pytest
from httpx import ASGITransport, AsyncClient

from jober_api.main import app
from tests.fixtures.workbook import build_sample_workbook

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres",
)


@pytest.mark.asyncio
async def test_import_jobs_xlsx_endpoint(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        data = build_sample_workbook()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            preview = await client.post(
                "/api/imports/jobs-xlsx?dry_run=true",
                files={
                    "file": (
                        "jobs.xlsx",
                        data,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                },
            )
            assert preview.status_code == 200
            body = preview.json()
            assert body["dry_run"] is True
            assert "mappings" in body

            committed = await client.post(
                "/api/imports/jobs-xlsx",
                files={
                    "file": (
                        "jobs.xlsx",
                        data,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                },
            )
            assert committed.status_code == 200
            result = committed.json()
            assert result["job_targets"]["created"] == 3

            listing = await client.get("/api/job-targets")
            assert listing.status_code == 200
            items = listing.json()["items"]
            assert len(items) == 3
            assert items[0]["ats_guess"] == "lever"

            bad = await client.post(
                "/api/imports/jobs-xlsx",
                files={"file": ("bad.xlsx", b"not-a-workbook", "application/octet-stream")},
            )
            assert bad.status_code == 422
            assert "Could not read workbook" in bad.json()["detail"]
    finally:
        app.dependency_overrides.clear()
