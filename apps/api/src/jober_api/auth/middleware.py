from __future__ import annotations

from fastapi import Request
from starlette.types import ASGIApp, Receive, Scope, Send

from jober_api.auth.context import AuthContext
from jober_api.auth.deps import PUBLIC_API_PREFIXES, get_auth_context
from jober_api.db.session import async_session_factory


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
            async with async_session_factory() as session:
                auth = await get_auth_context(request, session)
                scope.setdefault("state", {})["auth"] = auth

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
