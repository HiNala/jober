"""Integration tests for /readyz against live service containers (CI or RUN_INTEGRATION=1)."""

import os

import pytest
from httpx import ASGITransport, AsyncClient

from jober_api.main import app

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_INTEGRATION") != "1",
    reason="requires CI service containers or RUN_INTEGRATION=1",
)


@pytest.mark.asyncio
async def test_readyz_reports_ready_when_dependencies_up() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/readyz")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    checks = body["checks"]
    assert checks["postgres"]["ok"] is True, checks["postgres"]["detail"]
    assert checks["redis"]["ok"] is True, checks["redis"]["detail"]
    assert checks["minio"]["ok"] is True, checks["minio"]["detail"]
