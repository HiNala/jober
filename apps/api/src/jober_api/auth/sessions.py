from __future__ import annotations

import json
import secrets
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from jober_api.auth.redis_client import get_redis
from jober_api.config import settings

SESSION_PREFIX = "jober:session:"
REFRESH_PREFIX = "jober:refresh:"
USER_SESSIONS_PREFIX = "jober:user_sessions:"


@dataclass(frozen=True)
class SessionData:
    session_id: str
    user_id: uuid.UUID
    tenant_id: uuid.UUID
    csrf_token: str


def _session_key(session_id: str) -> str:
    return f"{SESSION_PREFIX}{session_id}"


def _refresh_key(refresh_id: str) -> str:
    return f"{REFRESH_PREFIX}{refresh_id}"


def _user_sessions_key(user_id: uuid.UUID) -> str:
    return f"{USER_SESSIONS_PREFIX}{user_id}"


async def create_session(
    user_id: uuid.UUID,
    tenant_id: uuid.UUID,
) -> tuple[str, str, str]:
    """Returns (session_id, refresh_id, csrf_token)."""
    session_id = secrets.token_urlsafe(32)
    refresh_id = secrets.token_urlsafe(32)
    csrf_token = secrets.token_urlsafe(24)
    payload = json.dumps(
        {
            "user_id": str(user_id),
            "tenant_id": str(tenant_id),
            "csrf": csrf_token,
            "created_at": datetime.now(UTC).isoformat(),
        }
    )
    redis = get_redis()
    await redis.setex(_session_key(session_id), settings.session_ttl_seconds, payload)
    await redis.setex(
        _refresh_key(refresh_id),
        settings.refresh_ttl_seconds,
        session_id,
    )
    await redis.sadd(_user_sessions_key(user_id), session_id)
    await redis.expire(_user_sessions_key(user_id), settings.refresh_ttl_seconds)
    return session_id, refresh_id, csrf_token


async def load_session(session_id: str) -> SessionData | None:
    redis = get_redis()
    raw = await redis.get(_session_key(session_id))
    if not raw:
        return None
    data = json.loads(raw)
    return SessionData(
        session_id=session_id,
        user_id=uuid.UUID(data["user_id"]),
        tenant_id=uuid.UUID(data["tenant_id"]),
        csrf_token=data["csrf"],
    )


async def refresh_session(refresh_id: str) -> tuple[str, str, str] | None:
    redis = get_redis()
    session_id = await redis.get(_refresh_key(refresh_id))
    if not session_id:
        return None
    existing = await load_session(session_id)
    if existing is None:
        return None
    await revoke_session(session_id)
    return await create_session(existing.user_id, existing.tenant_id)


async def revoke_session(session_id: str) -> None:
    redis = get_redis()
    existing = await load_session(session_id)
    await redis.delete(_session_key(session_id))
    if existing:
        await redis.srem(_user_sessions_key(existing.user_id), session_id)


async def revoke_all_sessions(user_id: uuid.UUID) -> int:
    redis = get_redis()
    session_ids = await redis.smembers(_user_sessions_key(user_id))
    count = 0
    for sid in session_ids:
        await redis.delete(_session_key(sid))
        count += 1
    await redis.delete(_user_sessions_key(user_id))
    return count


async def list_active_sessions(user_id: uuid.UUID) -> list[str]:
    redis = get_redis()
    return list(await redis.smembers(_user_sessions_key(user_id)))
