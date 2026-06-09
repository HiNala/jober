from __future__ import annotations

from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, TypeVar, cast

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from jober_api.auth.context import AuthContext
from jober_api.auth.deps import PUBLIC_API_PREFIXES
from jober_api.auth.middleware import require_auth
from jober_api.auth.permissions import Permission, can

F = TypeVar("F", bound=Callable[..., Any])

RBAC_ATTR = "__rbac_permission__"


def mark_permission(permission: Permission, fn: F) -> F:  # noqa: UP047
    setattr(fn, RBAC_ATTR, permission)
    return fn


def requires(permission: Permission) -> Callable[[F], F]:
    """Decorator that tags a route handler with its required permission."""

    def decorator(fn: F) -> F:
        @wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await fn(*args, **kwargs)

        mark_permission(permission, wrapper)
        mark_permission(permission, fn)
        return wrapper  # type: ignore[return-value]

    return decorator


def require_permission(permission: Permission) -> Callable[[Request], Awaitable[AuthContext]]:
    """FastAPI dependency: authenticate and enforce ``permission`` (default-deny)."""

    async def _enforce(request: Request) -> AuthContext:
        auth = require_auth(request)
        if not can(auth, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return auth

    _enforce.__rbac_permission__ = permission  # type: ignore[attr-defined]
    return _enforce


class RBACRouter(APIRouter):
    """APIRouter that attaches a default permission to every route."""

    def __init__(self, *, permission: Permission, **kwargs: Any) -> None:
        deps = list(kwargs.pop("dependencies", []) or [])
        deps.insert(0, Depends(require_permission(permission)))
        super().__init__(dependencies=deps, **kwargs)
        self._rbac_permission = permission

    def add_api_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        *,
        permission: Permission | None = None,
        **kwargs: Any,
    ) -> None:
        perm = permission or self._rbac_permission
        route_deps = list(kwargs.pop("dependencies", []) or [])
        route_deps.insert(0, Depends(require_permission(perm)))
        mark_permission(perm, endpoint)
        super().add_api_route(path, endpoint, dependencies=route_deps, **kwargs)


def _is_public_path(path: str) -> bool:
    if path in ("/healthz", "/readyz"):
        return True
    return any(path.startswith(prefix) for prefix in PUBLIC_API_PREFIXES)


def _route_permission(route: APIRoute) -> Permission | None:
    endpoint = route.endpoint
    perm = getattr(endpoint, RBAC_ATTR, None)
    if perm is not None:
        return cast(Permission, perm)
    # Follow FastAPI wrappers (e.g. ``@requires`` decorator).
    inner = getattr(endpoint, "__wrapped__", None)
    if inner is not None:
        inner_perm = getattr(inner, RBAC_ATTR, None)
        if inner_perm is not None:
            return cast(Permission, inner_perm)
    return None


def validate_rbac_coverage(app: Any) -> None:
    """Fail fast at startup if any protected /api route lacks a permission tag."""
    missing: list[str] = []
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        if not route.path.startswith("/api") or _is_public_path(route.path):
            continue
        if _route_permission(route) is None:
            methods = ",".join(sorted(route.methods or []))
            missing.append(f"{methods} {route.path}")
    if missing:
        msg = "RBAC default-deny: routes missing permission declaration:\n" + "\n".join(
            sorted(missing)
        )
        raise RuntimeError(msg)


class PermissionMiddleware(BaseHTTPMiddleware):
    """Enforce ``__rbac_permission__`` on every authenticated API route."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        path = request.url.path
        if path.startswith("/api") and not _is_public_path(path):
            route = request.scope.get("route")
            permission: Permission | None = None
            if isinstance(route, APIRoute):
                permission = _route_permission(route)
            if permission is None:
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Route permission not declared"},
                )
            auth: AuthContext | None = getattr(request.state, "auth", None)
            if auth is None:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Authentication required"},
                )
            if not can(auth, permission):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Insufficient permissions"},
                )
        return await call_next(request)
