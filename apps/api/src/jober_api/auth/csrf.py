from __future__ import annotations

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from jober_api.auth.deps import PUBLIC_API_PREFIXES
from jober_api.auth.sessions import load_session
from jober_api.config import settings
from jober_api.errors import CORRELATION_ID_HEADER, get_correlation_id

SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


def is_csrf_exempt(path: str) -> bool:
    """Routes that skip double-submit CSRF (public auth, webhooks, analytics collector)."""
    if path in ("/healthz", "/readyz"):
        return True
    return any(path.startswith(prefix) for prefix in PUBLIC_API_PREFIXES)


def verify_csrf(request: Request, session_csrf: str) -> None:
    if request.method in SAFE_METHODS:
        return
    header = request.headers.get("X-CSRF-Token", "")
    cookie = request.cookies.get(settings.csrf_cookie_name, "")
    if not header or not cookie or header != cookie or header != session_csrf:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF validation failed")


def _csrf_failure_response(request: Request) -> JSONResponse:
    correlation_id = get_correlation_id(request)
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": "CSRF validation failed", "correlation_id": correlation_id},
        headers={CORRELATION_ID_HEADER: correlation_id},
    )


class CsrfMiddleware:
    """Enforce double-submit CSRF when a session cookie is present on mutating /api routes."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "GET").upper()
        path = scope.get("path", "")
        if method in SAFE_METHODS or not path.startswith("/api") or is_csrf_exempt(path):
            await self.app(scope, receive, send)
            return

        headers = scope.get("headers", ())
        session_id: str | None = None
        for name, value in headers:
            if name.lower() != b"cookie":
                continue
            for part in value.decode("latin-1").split(";"):
                part = part.strip()
                if part.startswith(f"{settings.session_cookie_name}="):
                    session_id = part.split("=", 1)[1]
                    break
            if session_id:
                break

        if not session_id:
            await self.app(scope, receive, send)
            return

        data = await load_session(session_id)
        if data is None:
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        try:
            verify_csrf(request, data.csrf_token)
        except HTTPException:
            response = _csrf_failure_response(request)
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)
