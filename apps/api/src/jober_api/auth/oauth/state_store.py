from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass

from jober_api.auth.oauth.types import OAuthIntent
from jober_api.auth.redis_client import get_redis
from jober_api.config import settings

OAUTH_STATE_PREFIX = "jober:oauth_state:"
PENDING_LINK_PREFIX = "jober:oauth_link_pending:"


@dataclass
class StoredOAuthState:
    code_verifier: str
    intent: OAuthIntent
    link_user_id: str | None = None
    next_path: str = "/dashboard"


async def save_oauth_state(state: str, payload: StoredOAuthState) -> None:
    redis = get_redis()
    await redis.setex(
        f"{OAUTH_STATE_PREFIX}{state}",
        settings.oauth_state_ttl_seconds,
        json.dumps(asdict(payload)),
    )


async def consume_oauth_state(state: str) -> StoredOAuthState | None:
    redis = get_redis()
    key = f"{OAUTH_STATE_PREFIX}{state}"
    raw = await redis.get(key)
    if raw is None:
        return None
    await redis.delete(key)
    data = json.loads(raw)
    return StoredOAuthState(
        code_verifier=data["code_verifier"],
        intent=OAuthIntent(data["intent"]),
        link_user_id=data.get("link_user_id"),
        next_path=data.get("next_path") or "/dashboard",
    )


@dataclass
class PendingOAuthLink:
    provider: str
    provider_user_id: str
    provider_email: str | None
    display_name: str | None
    avatar_url: str | None
    existing_user_id: str


async def save_pending_link(token: str, payload: PendingOAuthLink) -> None:
    redis = get_redis()
    await redis.setex(
        f"{PENDING_LINK_PREFIX}{token}",
        settings.oauth_state_ttl_seconds,
        json.dumps(asdict(payload)),
    )


async def fetch_pending_link(token: str) -> PendingOAuthLink | None:
    redis = get_redis()
    key = f"{PENDING_LINK_PREFIX}{token}"
    raw = await redis.get(key)
    if raw is None:
        return None
    data = json.loads(raw)
    return PendingOAuthLink(**data)


async def delete_pending_link(token: str) -> None:
    redis = get_redis()
    await redis.delete(f"{PENDING_LINK_PREFIX}{token}")


async def consume_pending_link(token: str) -> PendingOAuthLink | None:
    pending = await fetch_pending_link(token)
    if pending is None:
        return None
    await delete_pending_link(token)
    return pending


def new_link_token() -> str:
    return str(uuid.uuid4())
