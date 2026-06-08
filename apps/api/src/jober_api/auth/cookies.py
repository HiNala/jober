from __future__ import annotations

from fastapi import Response

from jober_api.config import settings


def _cookie_flags() -> dict[str, object]:
    return {
        "httponly": True,
        "secure": settings.cookie_secure,
        "samesite": "lax",
        "path": "/",
    }


def set_auth_cookies(
    response: Response,
    session_id: str,
    refresh_id: str,
    csrf_token: str,
) -> None:
    flags = _cookie_flags()
    response.set_cookie(
        settings.session_cookie_name,
        session_id,
        max_age=settings.session_ttl_seconds,
        **flags,
    )
    response.set_cookie(
        settings.refresh_cookie_name,
        refresh_id,
        max_age=settings.refresh_ttl_seconds,
        **flags,
    )
    response.set_cookie(
        settings.csrf_cookie_name,
        csrf_token,
        max_age=settings.session_ttl_seconds,
        httponly=False,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )


def clear_auth_cookies(response: Response) -> None:
    for name in (
        settings.session_cookie_name,
        settings.refresh_cookie_name,
        settings.csrf_cookie_name,
    ):
        response.delete_cookie(name, path="/")
