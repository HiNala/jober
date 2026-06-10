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


def _redis() -> redis.Redis[str]:
    return redis.Redis.from_url(settings.redis_url, decode_responses=True)


def _fingerprint(source: str, message: str) -> str:
    digest = hashlib.sha256(f"{source}:{message}".encode()).hexdigest()
    return digest[:20]


def _should_fire(fingerprint: str) -> bool:
    key = f"{_ALERT_PREFIX}{fingerprint}"
    client = _redis()
    return bool(client.set(key, "1", nx=True, ex=settings.ops_alert_cooldown_seconds))


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
            message=primary,
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
