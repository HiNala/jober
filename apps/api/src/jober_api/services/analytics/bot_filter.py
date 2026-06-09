from __future__ import annotations

from jober_api.auth.context import AuthContext
from jober_api.config import settings
from jober_api.services.analytics.user_agent import is_bot_user_agent


def is_internal_traffic(
    *,
    auth: AuthContext | None,
) -> bool:
    if auth is not None and settings.analytics_internal_user_ids:
        internal = {s.strip() for s in settings.analytics_internal_user_ids.split(",") if s.strip()}
        if str(auth.user_id) in internal:
            return True
    return settings.jober_env in ("development", "test") and settings.dev_auth_bypass


def should_drop_event(*, user_agent: str | None) -> bool:
    return is_bot_user_agent(user_agent)


def mark_bot_and_internal(
    *,
    auth: AuthContext | None,
    user_agent: str | None,
) -> tuple[bool, bool]:
    return is_bot_user_agent(user_agent), is_internal_traffic(auth=auth)
