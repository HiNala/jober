"""CSRF contract: every mutating /api route is exempt or enforced by CsrfMiddleware."""

from __future__ import annotations

import os
import re
from collections.abc import Iterator

import pytest
from httpx import ASGITransport, AsyncClient

from jober_api.auth.constants import DEFAULT_DEV_TENANT_ID, DEFAULT_DEV_USER_ID
from jober_api.auth.csrf import SAFE_METHODS, is_csrf_exempt
from jober_api.auth.sessions import create_session
from jober_api.config import settings
from jober_api.main import app

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres + Redis",
)

_MUTATING = frozenset({"post", "put", "patch", "delete"})
_PARAM = re.compile(r"\{[^}]+\}")


def _fill_path_params(path: str) -> str:
    return _PARAM.sub("00000000-0000-0000-0000-000000000001", path)


def _iter_mutating_api_routes() -> Iterator[tuple[str, str]]:
    spec = app.openapi()
    for path, operations in spec.get("paths", {}).items():
        if not path.startswith("/api"):
            continue
        for method in operations:
            if method.lower() in _MUTATING:
                yield method.upper(), _fill_path_params(path)


def _classify_routes() -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    exempt: list[tuple[str, str]] = []
    protected: list[tuple[str, str]] = []
    for method, path in _iter_mutating_api_routes():
        if is_csrf_exempt(path):
            exempt.append((method, path))
        else:
            protected.append((method, path))
    return exempt, protected


EXEMPT_ROUTES, PROTECTED_ROUTES = _classify_routes()


def test_mutating_routes_partitioned() -> None:
    assert EXEMPT_ROUTES or PROTECTED_ROUTES
    seen = {(m, p) for m, p in EXEMPT_ROUTES} | {(m, p) for m, p in PROTECTED_ROUTES}
    assert len(seen) == len(EXEMPT_ROUTES) + len(PROTECTED_ROUTES)


@pytest.mark.parametrize("method,path", EXEMPT_ROUTES)
def test_exempt_route_declared(method: str, path: str) -> None:
    assert method.upper() not in SAFE_METHODS
    assert is_csrf_exempt(path)


@pytest.mark.asyncio
@pytest.mark.parametrize("method,path", PROTECTED_ROUTES)
async def test_protected_route_rejects_missing_csrf(
    method: str,
    path: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "auth_mode", "native")
    session_id, refresh_id, csrf = await create_session(DEFAULT_DEV_USER_ID, DEFAULT_DEV_TENANT_ID)
    cookies = {
        settings.session_cookie_name: session_id,
        settings.refresh_cookie_name: refresh_id,
        settings.csrf_cookie_name: csrf,
    }
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.request(method, path, cookies=cookies, json={})
    assert response.status_code == 403, (
        f"{method} {path} -> {response.status_code} {response.text[:200]}"
    )
    body = response.json()
    assert body.get("detail") == "CSRF validation failed"
    assert "correlation_id" in body


@pytest.mark.asyncio
async def test_dev_header_mutations_skip_csrf_without_session_cookie(
    db_session,
    truncate_tables,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Dev/test header auth without session cookies does not require CSRF double-submit."""
    from jober_api.db import session as db_session_module

    monkeypatch.setattr(settings, "auth_mode", "dev")

    async def _override():
        yield db_session

    app.dependency_overrides[db_session_module.get_session] = _override
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/job-targets",
                json={"company": "CSRF Co", "role": "Engineer"},
                headers={
                    "X-Jober-Tenant-Id": str(DEFAULT_DEV_TENANT_ID),
                    "X-Jober-User-Id": str(DEFAULT_DEV_USER_ID),
                },
            )
        assert response.json().get("detail") != "CSRF validation failed"
    finally:
        app.dependency_overrides.clear()
