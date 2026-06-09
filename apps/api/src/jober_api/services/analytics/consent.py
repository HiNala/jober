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
    if consent == "0":
        return True
    # Opt-in: no consent cookie means do not track client events.
    if consent != "1":
        return True
    return False
