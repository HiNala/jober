from __future__ import annotations

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from jober_api.auth.context import AuthContext
from jober_api.auth.deps import PUBLIC_API_PREFIXES, get_auth_context
from jober_api.db.session import async_session_factory
from jober_api.errors import CORRELATION_ID_HEADER, get_correlation_id


def _is_public_path(path: str) -> bool:
    if path in ("/healthz", "/readyz"):
        return True
    return any(path.startswith(prefix) for prefix in PUBLIC_API_PREFIXES)


class AuthMiddleware:
    """Pure ASGI auth context — avoids BaseHTTPMiddleware event-loop clashes in pytest-asyncio."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if path.startswith("/api") and not _is_public_path(path):
            request = Request(scope, receive)
            try:
                async with async_session_factory() as session:
                    auth = await get_auth_context(request, session)
                    scope.setdefault("state", {})["auth"] = auth
            except HTTPException as exc:
                correlation_id = get_correlation_id(request)
                response = JSONResponse(
                    status_code=exc.status_code,
                    content={"detail": exc.detail, "correlation_id": correlation_id},
                    headers={CORRELATION_ID_HEADER: correlation_id},
                )
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)


def require_auth(request: Request) -> AuthContext:
    auth: AuthContext | None = getattr(request.state, "auth", None)
    if auth is None:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return auth
