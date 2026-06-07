from __future__ import annotations

from datetime import UTC, datetime, time
from zoneinfo import ZoneInfo


def _parse_hhmm(value: str) -> time:
    hour, minute = value.split(":", 1)
    return time(hour=int(hour), minute=int(minute))


def in_quiet_hours(
    *,
    now: datetime | None = None,
    start: str,
    end: str,
    timezone: str = "UTC",
) -> bool:
    """True when local time is inside quiet hours (stay available for checkpoints)."""
    tz = ZoneInfo(timezone)
    local_now = (now or datetime.now(UTC)).astimezone(tz)
    start_t = _parse_hhmm(start)
    end_t = _parse_hhmm(end)
    current = local_now.time()
    if start_t <= end_t:
        return start_t <= current < end_t
    return current >= start_t or current < end_t
