from __future__ import annotations

import logging

from jober_api.config import settings
from jober_api.services.email.sender import (
    deliver_email_payload,
    email_dispatch_enabled,
    email_to_payload,
    mask_email,
)
from jober_api.services.email.templates import password_reset_email, verification_email

logger = logging.getLogger(__name__)


def _enqueue_or_deliver(payload: dict[str, str]) -> str | None:
    if not email_dispatch_enabled():
        logger.warning("email.skip to=%s reason=backend_disabled", mask_email(payload["to_email"]))
        return None
    try:
        from jober_worker.tasks import send_transactional_email

        result = send_transactional_email.delay(payload)
        return str(result.id)
    except Exception:
        if settings.jober_env == "development":
            deliver_email_payload(payload)
            return "sync-dev"
        logger.exception("email.enqueue_failed to=%s", mask_email(payload["to_email"]))
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
