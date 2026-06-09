from __future__ import annotations

import json
import time
from typing import Any

_CACHE: dict[str, tuple[float, str]] = {}
_DEFAULT_TTL_SECONDS = 60


def cache_get(key: str, *, ttl_seconds: int = _DEFAULT_TTL_SECONDS) -> Any | None:
    entry = _CACHE.get(key)
    if entry is None:
        return None
    expires_at, payload = entry
    if time.monotonic() > expires_at:
        _CACHE.pop(key, None)
        return None
    return json.loads(payload)


def cache_set(key: str, value: Any, *, ttl_seconds: int = _DEFAULT_TTL_SECONDS) -> None:
    _CACHE[key] = (time.monotonic() + ttl_seconds, json.dumps(value))


def cache_key(*parts: object) -> str:
    return ":".join(str(part) for part in parts)
