from __future__ import annotations

import smtplib
from email.message import EmailMessage

from jober_api.config import settings
from jober_api.services.email.types import TransactionalEmail


class SmtpEmailSender:
    """Provider-agnostic SMTP backend (Resend, SendGrid, Mailgun, self-hosted)."""

    def send(self, message: TransactionalEmail) -> None:
        host = settings.smtp_host.strip()
        if not host:
            msg = "SMTP_HOST is required when EMAIL_BACKEND=smtp"
            raise RuntimeError(msg)

        email = EmailMessage()
        email["From"] = settings.email_from
        email["To"] = message.to_email
        email["Subject"] = message.subject
        email.set_content(message.text_body)
        if message.html_body:
            email.add_alternative(message.html_body, subtype="html")

        with smtplib.SMTP(host, settings.smtp_port, timeout=30) as smtp:
            if settings.smtp_use_tls:
                smtp.starttls()
            user = settings.smtp_user.strip()
            password = settings.smtp_password
            if user:
                smtp.login(user, password)
            smtp.send_message(email)
