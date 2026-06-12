from __future__ import annotations

from jober_api.config import settings
from jober_api.services.email.types import TransactionalEmail

PRODUCT_NAME = "Jober"


def _web_link(path: str, token: str) -> str:
    base = settings.web_app_url.rstrip("/")
    return f"{base}{path}?token={token}"


def verification_email(to_email: str, token: str, display_name: str | None) -> TransactionalEmail:
    name = display_name or to_email.split("@")[0]
    link = _web_link("/verify-email", token)
    text = f"""Hi {name},

Confirm your email to finish setting up your {PRODUCT_NAME} account:

{link}

This link expires in 24 hours. If you did not create an account, you can ignore this email.

— {PRODUCT_NAME}
"""
    return TransactionalEmail(
        to_email=to_email,
        subject=f"Verify your {PRODUCT_NAME} email",
        text_body=text,
    )


def password_reset_email(to_email: str, token: str) -> TransactionalEmail:
    link = _web_link("/reset-password", token)
    text = f"""Hi,

We received a request to reset your {PRODUCT_NAME} password. Use the link below to choose a new one:

{link}

This link expires in 1 hour. If you did not request a reset, ignore this email —
your password will not change.

— {PRODUCT_NAME}
"""
    return TransactionalEmail(
        to_email=to_email,
        subject=f"Reset your {PRODUCT_NAME} password",
        text_body=text,
    )
