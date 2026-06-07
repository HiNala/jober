from __future__ import annotations

from urllib.parse import urlparse


def extract_domain(url: str) -> str:
    """Normalize host for per-domain locks and cooldowns (server-friendliness, not evasion)."""
    parsed = urlparse(url.strip())
    host = (parsed.hostname or "unknown").lower()
    port = parsed.port
    if port and port not in (80, 443):
        return f"{host}:{port}"
    return host


def job_apply_url(job: object) -> str:
    direct = getattr(job, "direct_apply_url", None) or ""
    careers = getattr(job, "company_careers_url", None) or ""
    return str(direct or careers).strip()
