from __future__ import annotations

import logging

from jober_api.services.email.types import TransactionalEmail

logger = logging.getLogger(__name__)


class ConsoleEmailSender:
    """Dev/CI backend — logs email content, never opens network connections."""

    def send(self, message: TransactionalEmail) -> None:
        logger.info(
            "email.console to=%s subject=%s\n%s",
            message.to_email,
            message.subject,
            message.text_body,
        )
