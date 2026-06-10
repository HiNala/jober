"""Resilience tests — readiness degrades when dependencies fail."""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from jober_api.main import app

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_INTEGRATION") != "1",
    reason="requires CI service containers or RUN_INTEGRATION=1",
)


@pytest.mark.asyncio
async def test_readyz_degraded_when_redis_unreachable() -> None:
    transport = ASGITransport(app=app)
    with patch(
        "jober_api.health.check_redis",
        new_callable=AsyncMock,
        return_value=(False, "connection refused"),
    ):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/readyz")
    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "not_ready"
    assert body["checks"]["redis"]["ok"] is False


@pytest.mark.asyncio
async def test_healthz_stays_live_when_redis_down() -> None:
    transport = ASGITransport(app=app)
    with patch(
        "jober_api.health.check_redis",
        new_callable=AsyncMock,
        return_value=(False, "connection refused"),
    ):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
