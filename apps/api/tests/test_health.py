import pytest
from httpx import ASGITransport, AsyncClient

from jober_api.main import app


@pytest.mark.asyncio
async def test_healthz_returns_ok() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_readyz_returns_report(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_readiness_report(database_url: str, redis_url: str) -> dict[str, object]:
        _ = database_url, redis_url
        return {
            "status": "not_ready",
            "checks": {
                "postgres": {"ok": False, "detail": "connection refused"},
                "redis": {"ok": False, "detail": "connection refused"},
                "minio": {"ok": False, "detail": "connection refused"},
            },
        }

    monkeypatch.setattr("jober_api.main.readiness_report", fake_readiness_report)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/readyz")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "not_ready"
    assert "checks" in body
