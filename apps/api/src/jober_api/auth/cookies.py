from __future__ import annotations

from fastapi import Response

from jober_api.config import settings


def _cookie_samesite() -> str:
    """Cross-origin web→API deploys (Railway) need SameSite=None when Secure."""
    return "none" if settings.cookie_secure else "lax"


def set_auth_cookies(
    response: Response,
    session_id: str,
    refresh_id: str,
    csrf_token: str,
) -> None:
    response.set_cookie(
        settings.session_cookie_name,
        session_id,
        max_age=settings.session_ttl_seconds,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=_cookie_samesite(),
        path="/",
    )
    response.set_cookie(
        settings.refresh_cookie_name,
        refresh_id,
        max_age=settings.refresh_ttl_seconds,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=_cookie_samesite(),
        path="/",
    )
    response.set_cookie(
        settings.csrf_cookie_name,
        csrf_token,
        max_age=settings.session_ttl_seconds,
        httponly=False,
        secure=settings.cookie_secure,
        samesite=_cookie_samesite(),
        path="/",
    )


def clear_auth_cookies(response: Response) -> None:
    same_site = _cookie_samesite()
    for name in (
        settings.session_cookie_name,
        settings.refresh_cookie_name,
        settings.csrf_cookie_name,
    ):
        response.delete_cookie(
            name,
            path="/",
            secure=settings.cookie_secure,
            samesite=same_site,
        )
