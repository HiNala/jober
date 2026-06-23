from __future__ import annotations

from fastapi import Request

from jober_api.config import settings


def resolve_client_ip(request: Request) -> str:
    """Resolve client IP, honoring forwarded headers only behind a trusted proxy."""
    if settings.trust_proxy_headers:
        forwarded = request.headers.get("X-Forwarded-For", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"
