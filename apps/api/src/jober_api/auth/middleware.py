from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from jober_api.auth.context import AuthContext
from jober_api.auth.deps import PUBLIC_API_PREFIXES, get_auth_context
from jober_api.db.session import async_session_factory


def _is_public_path(path: str) -> bool:
    if path in ("/healthz", "/readyz"):
        return True
    return any(path.startswith(prefix) for prefix in PUBLIC_API_PREFIXES)


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if request.url.path.startswith("/api") and not _is_public_path(request.url.path):
            async with async_session_factory() as session:
                auth = await get_auth_context(request, session)
                request.state.auth = auth
        return await call_next(request)


def require_auth(request: Request) -> AuthContext:
    auth: AuthContext | None = getattr(request.state, "auth", None)
    if auth is None:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return auth
