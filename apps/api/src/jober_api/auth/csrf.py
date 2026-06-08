from __future__ import annotations

from fastapi import HTTPException, Request, status

from jober_api.config import settings

SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


def verify_csrf(request: Request, session_csrf: str) -> None:
    if request.method in SAFE_METHODS:
        return
    header = request.headers.get("X-CSRF-Token", "")
    cookie = request.cookies.get(settings.csrf_cookie_name, "")
    if not header or not cookie or header != cookie or header != session_csrf:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF validation failed")
