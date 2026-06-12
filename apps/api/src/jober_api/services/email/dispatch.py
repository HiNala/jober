from __future__ import annotations

import logging

from jober_api.celery_enqueue import enqueue_task
from jober_api.config import settings
from jober_api.request_context import current_correlation_id
from jober_api.services.email.sender import (
    deliver_email_payload,
    email_dispatch_enabled,
    email_to_payload,
    mask_email,
)
from jober_api.services.email.templates import password_reset_email, verification_email
from jober_api.services.ops.alerting import (
    RUNBOOK_EMAIL_DELIVERY,
    dispatch_ops_alerts_sync,
    ops_attention,
)

logger = logging.getLogger(__name__)


def _enqueue_or_deliver(payload: dict[str, str]) -> str | None:
    if not email_dispatch_enabled():
        logger.warning("email.skip to=%s reason=backend_disabled", mask_email(payload["to_email"]))
        return None
    correlation_id = current_correlation_id()
    if correlation_id:
        payload = {**payload, "correlation_id": correlation_id}
    try:
        from jober_worker.tasks import send_transactional_email

        result = enqueue_task(send_transactional_email, payload)
        return str(result.id)
    except Exception:
        if settings.jober_env == "development":
            deliver_email_payload(payload)
            return "sync-dev"
        masked = mask_email(payload["to_email"])
        logger.exception("email.enqueue_failed to=%s", masked)
        dispatch_ops_alerts_sync(
            "email_enqueue_failed",
            [
                ops_attention(
                    "error",
                    f"Failed to enqueue transactional email for {masked}.",
                    runbook=RUNBOOK_EMAIL_DELIVERY,
                )
            ],
            force=False,
        )
        return None


def dispatch_verification_email(
    to_email: str,
    token: str,
    display_name: str | None,
) -> str | None:
    message = verification_email(to_email, token, display_name)
    return _enqueue_or_deliver(email_to_payload(message))


def dispatch_password_reset_email(to_email: str, token: str) -> str | None:
    message = password_reset_email(to_email, token)
    return _enqueue_or_deliver(email_to_payload(message))
