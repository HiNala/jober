"""Cross-tenant ops metrics for admin overview and alerting."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.failure_event import FailureEvent
from jober_api.services.batch.cost_governor import budget_status
from jober_api.services.batch.redis_control import celery_broker_depth

CIRCUIT_BREAKER_THRESHOLD = 5
QUEUE_BACKLOG_WARN = 20


async def global_circuit_trips(
    session: AsyncSession,
    *,
    threshold: int = CIRCUIT_BREAKER_THRESHOLD,
) -> list[dict[str, Any]]:
    stmt = (
        select(
            FailureEvent.platform,
            FailureEvent.failure_class,
            func.count(FailureEvent.id),
        )
        .group_by(FailureEvent.platform, FailureEvent.failure_class)
        .having(func.count(FailureEvent.id) >= threshold)
        .order_by(func.count(FailureEvent.id).desc())
        .limit(20)
    )
    rows = (await session.execute(stmt)).all()
    return [
        {
            "platform": platform,
            "failure_class": failure_class,
            "count": int(count),
            "threshold": threshold,
        }
        for platform, failure_class, count in rows
    ]


async def build_ops_attention(
    session: AsyncSession,
    *,
    queue: dict[str, Any],
    broker_depth: int | None = None,
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    """Return attention items and ops metric snapshot for admin overview."""
    depth = broker_depth if broker_depth is not None else celery_broker_depth()
    budget = await budget_status(session)
    trips = await global_circuit_trips(session)

    attention: list[dict[str, str]] = []

    if budget["hard_stop"]:
        attention.append(
            {
                "level": "error",
                "message": (
                    f"LLM monthly budget exceeded "
                    f"(${budget['spent_usd']:.2f} / ${budget['monthly_budget_usd']:.2f})."
                ),
            }
        )
    elif budget["soft_warn"]:
        attention.append(
            {
                "level": "warn",
                "message": (
                    f"LLM spend at soft warn "
                    f"(${budget['spent_usd']:.2f} / ${budget['monthly_budget_usd']:.2f})."
                ),
            }
        )

    for trip in trips[:5]:
        attention.append(
            {
                "level": "warn",
                "message": (
                    f"Circuit breaker: {trip['count']} {trip['failure_class']} "
                    f"failures on {trip['platform']}."
                ),
            }
        )

    if depth >= QUEUE_BACKLOG_WARN and int(queue.get("active_runs", 0)) == 0:
        attention.append(
            {
                "level": "warn",
                "message": (
                    f"Celery broker backlog ({depth} pending) with no active runs — "
                    "worker may be stalled."
                ),
            }
        )

    if queue.get("globally_paused"):
        pass  # overview already adds queue paused attention

    ops = {
        "celery_broker_depth": depth,
        "circuit_trips": trips,
        "budget": budget,
    }
    return attention, ops
