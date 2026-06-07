from __future__ import annotations

import re
from typing import Any

_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_PHONE_RE = re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")
_BEARER_RE = re.compile(r"Bearer\s+[A-Za-z0-9._\-]+", re.I)
_SK_KEY_RE = re.compile(r"\bsk-[A-Za-z0-9]{16,}\b")
_API_KEY_PAIR_RE = re.compile(
    r"(?i)(api[_-]?key|password|secret|token|authorization)\s*[:=]\s*['\"]?([^\s'\",;]+)",
)
_JWT_RE = re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b")

_RUNTIME_SECRETS: list[str] = []


def register_runtime_secrets(*values: str | None) -> None:
    """Register env secrets so scrubbers never persist them in logs or events."""
    for value in values:
        if value and len(value) >= 8 and value not in _RUNTIME_SECRETS:
            _RUNTIME_SECRETS.append(value)


def _mask_email(match: re.Match[str]) -> str:
    local, domain = match.group(0).split("@", 1)
    masked_local = (local[:1] + "***") if local else "***"
    return f"{masked_local}@{domain}"


def _mask_phone(match: re.Match[str]) -> str:
    digits = "".join(c for c in match.group(0) if c.isdigit())
    if len(digits) >= 4:
        return f"***-***-{digits[-4:]}"
    return "***"


def scrub_text(text: str, *, debug: bool = False, limit: int | None = None) -> str:
    """Mask secrets and PII before any log/event/LLM audit write."""
    if not text:
        return ""
    out = text
    for secret in sorted(_RUNTIME_SECRETS, key=len, reverse=True):
        out = out.replace(secret, "[REDACTED_SECRET]")
    out = _BEARER_RE.sub("Bearer [REDACTED_TOKEN]", out)
    out = _SK_KEY_RE.sub("[REDACTED_API_KEY]", out)
    out = _JWT_RE.sub("[REDACTED_JWT]", out)
    out = _API_KEY_PAIR_RE.sub(r"\1=[REDACTED]", out)
    out = _EMAIL_RE.sub(_mask_email, out)
    out = _PHONE_RE.sub(_mask_phone, out)
    max_len = limit if limit is not None else (2000 if debug else 400)
    trimmed = out.strip()
    if len(trimmed) <= max_len:
        return trimmed
    return f"{trimmed[:max_len]}…"


def scrub_value(value: Any, *, debug: bool = False) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        return scrub_text(value, debug=debug)
    if isinstance(value, dict):
        return scrub_dict(value, debug=debug)
    if isinstance(value, list):
        return [scrub_value(item, debug=debug) for item in value]
    return value


def scrub_dict(payload: dict[str, Any] | None, *, debug: bool = False) -> dict[str, Any]:
    if not payload:
        return {}
    sensitive_keys = {
        "password",
        "secret",
        "token",
        "api_key",
        "authorization",
        "cookie",
        "cookies",
        "storage_state",
        "sensitive_eeo_answers",
        "vault",
        "ssn",
        "credit_card",
    }
    out: dict[str, Any] = {}
    for key, value in payload.items():
        key_lower = key.lower()
        if any(marker in key_lower for marker in sensitive_keys):
            out[key] = "[REDACTED]"
            continue
        out[key] = scrub_value(value, debug=debug)
    return out


def scrub_event_message(message: str, *, debug: bool = False) -> str:
    return scrub_text(message, debug=debug, limit=2000 if debug else 500)
