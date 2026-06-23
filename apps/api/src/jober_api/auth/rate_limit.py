from __future__ import annotations

from jober_api.auth.redis_client import get_redis
from jober_api.config import settings

RATE_PREFIX = "jober:auth:rate:"
RESEND_PREFIX = "jober:auth:resend:"
LOCKOUT_PREFIX = "jober:auth:lockout:"


async def check_rate_limit(bucket: str) -> bool:
    """Return True if request is allowed."""
    redis = get_redis()
    key = f"{RATE_PREFIX}{bucket}"
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, settings.auth_rate_limit_window_seconds)
    return count <= settings.auth_rate_limit_max


async def record_failed_login(email: str) -> int:
    redis = get_redis()
    key = f"{LOCKOUT_PREFIX}{email.strip().lower()}"
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, settings.auth_lockout_seconds)
    return count


async def is_locked_out(email: str) -> bool:
    redis = get_redis()
    key = f"{LOCKOUT_PREFIX}{email.strip().lower()}"
    count = await redis.get(key)
    if count is None:
        return False
    return int(count) >= settings.auth_lockout_threshold


async def clear_failed_logins(email: str) -> None:
    redis = get_redis()
    await redis.delete(f"{LOCKOUT_PREFIX}{email.strip().lower()}")


async def check_analytics_rate_limit(bucket: str) -> bool:
    """Return True if analytics ingest is allowed for this bucket (typically IP)."""
    redis = get_redis()
    key = f"jober:analytics:rate:{bucket}"
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, settings.analytics_rate_limit_window_seconds)
    return count <= settings.analytics_rate_limit_max


async def check_resend_rate_limit(bucket: str) -> bool:
    """Stricter pacing for verification / reset resend actions."""
    redis = get_redis()
    key = f"{RESEND_PREFIX}{bucket}"
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, settings.email_resend_rate_limit_window_seconds)
    return count <= settings.email_resend_rate_limit_max
