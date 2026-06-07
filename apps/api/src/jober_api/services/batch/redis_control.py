from __future__ import annotations

import time
from typing import Any

import redis

from jober_api.config import settings

_PREFIX = "jober:batch"
_DOMAIN_LOCK_TTL_SEC = 3600


def _client() -> redis.Redis[str]:
    return redis.Redis.from_url(settings.redis_url, decode_responses=True)


def pause_all() -> None:
    _client().set(f"{_PREFIX}:paused", "1")


def resume_all() -> None:
    _client().delete(f"{_PREFIX}:paused")


def is_globally_paused() -> bool:
    return _client().get(f"{_PREFIX}:paused") == "1"


def set_max_concurrency(value: int) -> None:
    _client().set(f"{_PREFIX}:max_concurrency", str(max(1, value)))


def get_max_concurrency(default: int) -> int:
    raw = _client().get(f"{_PREFIX}:max_concurrency")
    if raw is None:
        return default
    try:
        return max(1, int(raw))
    except ValueError:
        return default


def count_active_slots() -> int:
    return int(_client().scard(f"{_PREFIX}:active_runs") or 0)


def register_active_run(run_id: str) -> None:
    _client().sadd(f"{_PREFIX}:active_runs", run_id)


def unregister_active_run(run_id: str) -> None:
    _client().srem(f"{_PREFIX}:active_runs", run_id)


def try_acquire_domain_lock(domain: str, run_id: str) -> bool:
    key = f"{_PREFIX}:domain_lock:{domain}"
    acquired = _client().set(key, run_id, nx=True, ex=_DOMAIN_LOCK_TTL_SEC)
    return bool(acquired)


def release_domain_lock(domain: str, run_id: str) -> None:
    key = f"{_PREFIX}:domain_lock:{domain}"
    client = _client()
    if client.get(key) == run_id:
        client.delete(key)


def domain_lock_holder(domain: str) -> str | None:
    return _client().get(f"{_PREFIX}:domain_lock:{domain}")


def record_domain_request(domain: str) -> float:
    """Record last request time for cooldown pacing; returns timestamp recorded."""
    now = time.time()
    _client().set(f"{_PREFIX}:domain_last:{domain}", str(now))
    return now


def seconds_since_domain_request(domain: str) -> float | None:
    raw = _client().get(f"{_PREFIX}:domain_last:{domain}")
    if raw is None:
        return None
    try:
        return time.time() - float(raw)
    except ValueError:
        return None


def wait_for_domain_cooldown(domain: str, cooldown_seconds: float) -> float:
    """Block until cooldown elapsed. Returns seconds waited (server-friendly pacing)."""
    elapsed = seconds_since_domain_request(domain)
    if elapsed is None or elapsed >= cooldown_seconds:
        return 0.0
    wait = cooldown_seconds - elapsed
    time.sleep(wait)
    return wait


def mark_run_cancelled(run_id: str) -> None:
    _client().setex(f"{_PREFIX}:cancel:{run_id}", 86400, "1")


def is_run_cancelled(run_id: str) -> bool:
    return _client().get(f"{_PREFIX}:cancel:{run_id}") == "1"


def set_batch_paused(batch_id: str, paused: bool) -> None:
    key = f"{_PREFIX}:batch_paused:{batch_id}"
    if paused:
        _client().set(key, "1")
    else:
        _client().delete(key)


def is_batch_paused(batch_id: str) -> bool:
    return _client().get(f"{_PREFIX}:batch_paused:{batch_id}") == "1"


def queue_snapshot(default_max_concurrency: int) -> dict[str, Any]:
    client = _client()
    return {
        "globally_paused": is_globally_paused(),
        "max_concurrency": get_max_concurrency(default_max_concurrency),
        "active_runs": count_active_slots(),
        "active_run_ids": list(client.smembers(f"{_PREFIX}:active_runs") or []),
    }
