"""Lightweight concurrent load smoke — hot read paths under parallel traffic."""

from __future__ import annotations

import asyncio
import os
import time

import pytest
from httpx import ASGITransport, AsyncClient

from jober_api.main import app

pytestmark = [
    pytest.mark.load,
    pytest.mark.skipif(
        os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
        reason="requires Postgres",
    ),
]


async def _timed_get(client: AsyncClient, path: str, **kwargs: object) -> float:
    start = time.perf_counter()
    response = await client.get(path, **kwargs)
    elapsed = time.perf_counter() - start
    assert response.status_code == 200, response.text
    return elapsed


@pytest.mark.asyncio
async def test_hot_read_paths_under_concurrent_load(
    db_session, truncate_tables, auth_headers
) -> None:
    from jober_api.db import session as db_session_module

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            paths = [
                ("/healthz", {}),
                ("/api/batches/dashboard/summary", {"headers": auth_headers}),
                ("/api/analytics/me", {"headers": auth_headers}),
            ]
            tasks = [
                _timed_get(client, path, **kwargs) for path, kwargs in paths for _ in range(10)
            ]
            elapsed = await asyncio.gather(*tasks)
        assert max(elapsed) < 3.0, f"slowest request {max(elapsed):.2f}s"
    finally:
        app.dependency_overrides.clear()
