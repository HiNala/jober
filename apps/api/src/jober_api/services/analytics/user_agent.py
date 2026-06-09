from __future__ import annotations

import re

_BOT_RE = re.compile(
    r"(bot|crawler|spider|slurp|curl|wget|python-requests|headless|lighthouse|preview)",
    re.I,
)


def user_agent_family(user_agent: str | None) -> str | None:
    if not user_agent:
        return None
    ua = user_agent[:512]
    if _BOT_RE.search(ua):
        return "bot"
    if "Edg/" in ua:
        return "edge"
    if "Chrome/" in ua and "Chromium" not in ua:
        return "chrome"
    if "Firefox/" in ua:
        return "firefox"
    if "Safari/" in ua and "Chrome" not in ua:
        return "safari"
    return "other"


def is_bot_user_agent(user_agent: str | None) -> bool:
    return user_agent_family(user_agent) == "bot"
