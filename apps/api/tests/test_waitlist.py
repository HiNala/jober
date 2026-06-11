from __future__ import annotations

import os

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from jober_api.main import app
from jober_api.models.pro_waitlist import ProWaitlistEntry

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres",
)


@pytest.mark.asyncio
async def test_pro_waitlist_create_and_dedupe(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            first = await client.post(
                "/api/waitlist/pro",
                json={
                    "email": "pro@example.com",
                    "consent_contact": True,
                    "source": "pricing",
                },
            )
            assert first.status_code == 200
            assert first.json()["status"] == "created"

            second = await client.post(
                "/api/waitlist/pro",
                json={
                    "email": "PRO@example.com",
                    "consent_contact": True,
                    "source": "pricing",
                },
            )
            assert second.status_code == 200
            assert second.json()["status"] == "already_registered"

            rows = (await db_session.scalars(select(ProWaitlistEntry))).all()
            assert len(rows) == 1
            assert rows[0].email == "pro@example.com"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_pro_waitlist_requires_consent(db_session, truncate_tables) -> None:
    from jober_api.db import session as db_session_module

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post(
                "/api/waitlist/pro",
                json={"email": "no@example.com", "consent_contact": False},
            )
            assert res.status_code == 422
    finally:
        app.dependency_overrides.clear()
