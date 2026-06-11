from __future__ import annotations

import logging
from typing import Protocol

from jober_api.config import settings
from jober_api.services.email.console import ConsoleEmailSender
from jober_api.services.email.smtp import SmtpEmailSender
from jober_api.services.email.types import TransactionalEmail

logger = logging.getLogger(__name__)


class EmailSender(Protocol):
    def send(self, message: TransactionalEmail) -> None: ...


def mask_email(email: str) -> str:
    local, _, domain = email.partition("@")
    if not domain:
        return "***"
    masked_local = "*" if len(local) <= 1 else f"{local[0]}***"
    return f"{masked_local}@{domain}"


def inbox_delivery_enabled() -> bool:
    """True when emails are delivered to real inboxes (SMTP configured)."""
    return (
        settings.email_backend.strip().lower() == "smtp"
        and bool(settings.smtp_host.strip())
        and bool(settings.email_from.strip())
    )


def email_dispatch_enabled() -> bool:
    """True when any outbound backend will attempt delivery (smtp or console)."""
    backend = settings.email_backend.strip().lower()
    if backend == "none":
        return False
    if backend == "smtp":
        return inbox_delivery_enabled()
    return backend == "console"


def get_email_sender() -> EmailSender:
    backend = settings.email_backend.strip().lower()
    if backend == "smtp":
        return SmtpEmailSender()
    if backend == "none":
        msg = "EMAIL_BACKEND=none — outbound email disabled"
        raise RuntimeError(msg)
    return ConsoleEmailSender()


def deliver_email_payload(payload: dict[str, str]) -> None:
    message = TransactionalEmail(
        to_email=payload["to_email"],
        subject=payload["subject"],
        text_body=payload["text_body"],
        html_body=payload.get("html_body"),
    )
    get_email_sender().send(message)
    logger.info(
        "email.sent backend=%s to=%s subject=%s",
        settings.email_backend,
        mask_email(message.to_email),
        message.subject,
    )


def email_to_payload(message: TransactionalEmail) -> dict[str, str]:
    data: dict[str, str] = {
        "to_email": message.to_email,
        "subject": message.subject,
        "text_body": message.text_body,
    }
    if message.html_body:
        data["html_body"] = message.html_body
    return data
