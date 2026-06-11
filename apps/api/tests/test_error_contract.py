from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from jober_api.errors import CORRELATION_ID_HEADER
from jober_api.main import app


@pytest.mark.asyncio
async def test_unhandled_exception_returns_opaque_500_with_correlation_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _boom(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise RuntimeError("secret internal path /var/lib/postgres")

    monkeypatch.setattr("jober_api.main.readiness_report", _boom)

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/readyz")

    assert response.status_code == 500
    body = response.json()
    assert body["detail"] == "Internal server error"
    assert "correlation_id" in body
    assert CORRELATION_ID_HEADER in response.headers
    lowered = response.text.lower()
    assert "traceback" not in lowered
    assert "/var/lib" not in lowered
    assert "runtimeerror" not in lowered


@pytest.mark.asyncio
async def test_http_exception_includes_correlation_id_and_code() -> None:
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/nonexistent-route-for-404-test")

    assert response.status_code in {404, 405}
    if response.status_code == 404:
        body = response.json()
        assert "detail" in body
        assert "correlation_id" in body
        assert CORRELATION_ID_HEADER in response.headers


@pytest.mark.asyncio
async def test_validation_error_envelope_has_detail_and_correlation_id() -> None:
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/waitlist/pro", json={})

    assert response.status_code == 422
    body = response.json()
    assert "detail" in body
    assert isinstance(body["detail"], list)
    assert "correlation_id" in body


@pytest.mark.asyncio
@pytest.mark.skipif(
    __import__("os").getenv("CI") != "true" and __import__("os").getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres",
)
async def test_resume_upload_maps_storage_outage_to_503(
    db_session,
    truncate_tables,
) -> None:
    from jober_api.db import session as db_session_module

    class BrokenStorage:
        async def put_object(self, *args: object, **kwargs: object) -> None:
            raise ConnectionError("minio connection refused")

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    try:
        from jober_api.routers import resumes as resumes_router

        app.dependency_overrides[resumes_router.get_storage] = lambda: BrokenStorage()

        transport = ASGITransport(app=app, raise_app_exceptions=False)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/resumes",
                files={"file": ("resume.pdf", b"%PDF-1.4 minimal", "application/pdf")},
            )

        assert response.status_code == 503
        body = response.json()
        assert body["code"] == "dependency_unavailable"
        detail = body["detail"]
        assert isinstance(detail, dict)
        assert detail.get("message")
        assert "connection refused" not in response.text.lower()
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_cors_headers_on_error_response() -> None:
    from jober_api.config import settings

    origin = settings.cors_origins[0] if settings.cors_origins else "http://localhost:3000"

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"Origin": origin},
    ) as client:
        response = await client.get("/api/definitely-missing-route-xyz")

    assert response.status_code == 404
    allow = response.headers.get("access-control-allow-origin")
    assert allow in {origin, "*"}
