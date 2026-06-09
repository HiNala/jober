from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any

from jober_api.config import settings
from jober_api.services.analytics.event_registry import FUNNEL_STEPS

SESSION_GAP = timedelta(minutes=30)


@dataclass(frozen=True)
class PageMetric:
    page: str
    page_views: int
    unique_sessions: int
    total_time_on_page_sec: float
    bounces: int


@dataclass(frozen=True)
class FunnelMetric:
    step: str
    event_count: int
    unique_users: int
    unique_sessions: int


def _actor_key(event: dict[str, Any]) -> str:
    if event.get("user_id"):
        return f"u:{event['user_id']}"
    if event.get("anon_id"):
        return f"a:{event['anon_id']}"
    return f"s:{event['session_id']}"


def compute_page_metrics(events: list[dict[str, Any]]) -> list[PageMetric]:
    """Derive per-page views, time-on-page, and bounces from page.view events."""
    by_session: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        if event.get("is_bot") or event.get("is_internal"):
            continue
        if event.get("name") != "page.view":
            continue
        by_session[str(event["session_id"])].append(event)

    page_views: dict[str, int] = defaultdict(int)
    page_sessions: dict[str, set[str]] = defaultdict(set)
    page_time: dict[str, float] = defaultdict(float)
    page_bounces: dict[str, int] = defaultdict(int)

    for session_id, session_events in by_session.items():
        ordered = sorted(session_events, key=lambda e: e["ts"])
        if len(ordered) == 1:
            page = ordered[0].get("page") or "/"
            page_bounces[page] += 1

        for idx, event in enumerate(ordered):
            page = event.get("page") or "/"
            page_views[page] += 1
            page_sessions[page].add(session_id)
            if idx + 1 < len(ordered):
                delta = ordered[idx + 1]["ts"] - event["ts"]
                if isinstance(delta, timedelta):
                    seconds = min(delta.total_seconds(), SESSION_GAP.total_seconds())
                else:
                    seconds = 0.0
                page_time[page] += max(seconds, 0.0)

    pages = set(page_views) | set(page_bounces)
    return [
        PageMetric(
            page=page,
            page_views=page_views[page],
            unique_sessions=len(page_sessions[page]),
            total_time_on_page_sec=page_time[page],
            bounces=page_bounces[page],
        )
        for page in sorted(pages)
    ]


def compute_funnel_metrics(events: list[dict[str, Any]]) -> list[FunnelMetric]:
    """Count funnel steps from canonical event names for a single day."""
    product_events = [
        e
        for e in events
        if not e.get("is_bot") and not e.get("is_internal")
    ]
    by_step: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for step, event_name in FUNNEL_STEPS.items():
        for event in product_events:
            if event.get("name") == event_name:
                by_step[step].append(event)

    metrics: list[FunnelMetric] = []
    for step in FUNNEL_STEPS:
        rows = by_step.get(step, [])
        users = {_actor_key(e) for e in rows}
        sessions = {str(e["session_id"]) for e in rows}
        metrics.append(
            FunnelMetric(
                step=step,
                event_count=len(rows),
                unique_users=len(users),
                unique_sessions=len(sessions),
            )
        )
    return metrics


def compute_active_users(
    events: list[dict[str, Any]],
    *,
    day: date,
) -> tuple[int, int, int]:
    """DAU for day; WAU/MAU from event window in rollup input."""
    del day
    actors_today: set[str] = set()
    for event in events:
        if event.get("is_bot") or event.get("is_internal"):
            continue
        actors_today.add(_actor_key(event))
    dau = len(actors_today)
    return dau, dau, dau


def session_timeout_minutes() -> int:
    return settings.analytics_session_timeout_minutes
