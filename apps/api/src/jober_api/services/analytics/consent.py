from __future__ import annotations

from fastapi import Request

CONSENT_COOKIE = "jober_analytics_consent"


def tracking_suppressed(request: Request) -> bool:
    """True when DNT/GPC or explicit opt-out cookie blocks first-party analytics."""
    dnt = request.headers.get("DNT", "").strip()
    if dnt == "1":
        return True
    gpc = request.headers.get("Sec-GPC", "").strip()
    if gpc == "1":
        return True
    consent = request.cookies.get(CONSENT_COOKIE, "").strip()
    # Opt-in: only track when consent cookie is explicitly "1".
    return consent != "1"
