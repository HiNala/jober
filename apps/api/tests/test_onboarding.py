from __future__ import annotations

import os

import pytest
from httpx import ASGITransport, AsyncClient

from jober_api.config import settings
from jober_api.main import app

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres + Redis",
)


@pytest.mark.asyncio
async def test_demo_workspace_seeds_jobs(db_session, truncate_tables, monkeypatch) -> None:
    from jober_api.auth.constants import DEFAULT_DEV_TENANT_ID, DEFAULT_DEV_USER_ID
    from jober_api.db import session as db_session_module
    from jober_api.repositories.job_target import JobTargetRepository

    monkeypatch.setattr(settings, "auth_mode", "native")
    monkeypatch.setattr(settings, "dev_auth_bypass", False)

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    transport = ASGITransport(app=app, raise_app_exceptions=False)

    from jober_api.auth.sessions import create_session

    session_id, refresh_id, csrf = await create_session(
        DEFAULT_DEV_USER_ID,
        DEFAULT_DEV_TENANT_ID,
    )
    cookies = {
        settings.session_cookie_name: session_id,
        settings.refresh_cookie_name: refresh_id,
        settings.csrf_cookie_name: csrf,
    }

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            created = await client.post(
                "/api/onboarding/demo-workspace",
                cookies=cookies,
                headers={"X-CSRF-Token": csrf},
            )
            assert created.status_code == 200
            body = created.json()
            assert body["jobs_created"] == 4

            duplicate = await client.post(
                "/api/onboarding/demo-workspace",
                cookies=cookies,
                headers={"X-CSRF-Token": csrf},
            )
            assert duplicate.status_code == 409

        jobs = JobTargetRepository(db_session, DEFAULT_DEV_TENANT_ID)
        rows = await jobs.list_filtered(limit=10)
        assert len(rows) == 4
    finally:
        app.dependency_overrides.clear()
