"""Outbound ops alerts (webhook) with Redis-backed cooldown."""

from __future__ import annotations

import hashlib
import logging
from typing import Any

import httpx
import redis

from jober_api.config import settings
from jober_api.privacy.logging import safe_log

logger = logging.getLogger(__name__)

_ALERT_PREFIX = "jober:ops:alert:"

# Relative runbook paths — linked in alert payloads for on-call routing.
RUNBOOK_INFRA_DOWN = "docs/runbooks/infra-down.md"
RUNBOOK_QUEUE_BACKED_UP = "docs/runbooks/queue-backed-up.md"
RUNBOOK_WORKER_STUCK = "docs/runbooks/worker-stuck.md"
RUNBOOK_COST_SPIKE = "docs/runbooks/cost-spike.md"
RUNBOOK_EMAIL_DELIVERY = "docs/runbooks/email-delivery.md"
RUNBOOK_UPTIME = "docs/runbooks/uptime-monitoring.md"


def ops_attention(level: str, message: str, *, runbook: str | None = None) -> dict[str, str]:
    """Build a webhook attention item with optional runbook cross-link."""
    item: dict[str, str] = {"level": level, "message": message}
    if runbook:
        item["runbook"] = runbook
        if runbook not in message:
            item["message"] = f"{message} Runbook: {runbook}"
    return item


def _redis() -> redis.Redis[str]:
    return redis.Redis.from_url(settings.redis_url, decode_responses=True)


def _fingerprint(source: str, message: str) -> str:
    digest = hashlib.sha256(f"{source}:{message}".encode()).hexdigest()
    return digest[:20]


def _should_fire(fingerprint: str) -> bool:
    key = f"{_ALERT_PREFIX}{fingerprint}"
    client = _redis()
    return bool(client.set(key, "1", nx=True, ex=settings.ops_alert_cooldown_seconds))


def _post_webhook(body: dict[str, Any]) -> bool:
    url = settings.ops_alert_webhook_url.strip()
    if not url:
        return False
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(url, json=body)
            response.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        safe_log(
            logging.ERROR,
            "ops alert webhook failed",
            source=body.get("source"),
            error=str(exc),
        )
        return False
    source = body.get("source", "unknown")
    attention = body.get("attention", [])
    count = len(attention) if isinstance(attention, list) else 0
    safe_log(logging.INFO, "ops alert dispatched", source=source, count=count)
    return True


async def dispatch_ops_alerts(
    source: str,
    attention: list[dict[str, str]],
    *,
    force: bool = False,
) -> bool:
    """POST attention items to OPS_ALERT_WEBHOOK_URL. Returns True if dispatched."""
    url = settings.ops_alert_webhook_url.strip()
    if not url or not attention:
        return False

    errors = [item for item in attention if item.get("level") == "error"]
    warns = [item for item in attention if item.get("level") == "warn"]
    payload_items = errors if errors else warns[:3]
    if not payload_items:
        return False

    primary = payload_items[0].get("message", source)
    if not force and not _should_fire(_fingerprint(source, primary)):
        safe_log(
            logging.INFO,
            "ops alert suppressed by cooldown",
            source=source,
            alert_message=primary,
        )
        return False

    body: dict[str, Any] = {
        "source": source,
        "environment": settings.jober_env,
        "attention": payload_items,
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=body)
            response.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        safe_log(logging.ERROR, "ops alert webhook failed", source=source, error=str(exc))
        return False

    safe_log(logging.INFO, "ops alert dispatched", source=source, count=len(payload_items))
    return True


def dispatch_ops_alerts_sync(
    source: str,
    attention: list[dict[str, str]],
    *,
    force: bool = False,
) -> bool:
    """Sync webhook dispatch for Celery workers."""
    url = settings.ops_alert_webhook_url.strip()
    if not url or not attention:
        return False

    errors = [item for item in attention if item.get("level") == "error"]
    warns = [item for item in attention if item.get("level") == "warn"]
    payload_items = errors if errors else warns[:3]
    if not payload_items:
        return False

    primary = payload_items[0].get("message", source)
    if not force and not _should_fire(_fingerprint(source, primary)):
        safe_log(
            logging.INFO,
            "ops alert suppressed by cooldown",
            source=source,
            alert_message=primary,
        )
        return False

    body: dict[str, Any] = {
        "source": source,
        "environment": settings.jober_env,
        "attention": payload_items,
    }
    return _post_webhook(body)


def alert_email_send_failed(
    *,
    to_email_masked: str,
    subject: str,
    error: str,
    correlation_id: str | None = None,
) -> None:
    """Fire ops alert when transactional email delivery fails after retries."""
    message = (
        f"Transactional email failed for {to_email_masked} "
        f"(subject: {subject[:80]}): {error[:200]}"
    )
    if correlation_id:
        message = f"{message} correlation_id={correlation_id}"
    dispatch_ops_alerts_sync(
        "email_send_failed",
        [
            ops_attention(
                "error",
                message,
                runbook=RUNBOOK_EMAIL_DELIVERY,
            )
        ],
        force=False,
    )
