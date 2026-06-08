from __future__ import annotations

import os

from jober_api.config import settings
from jober_api.privacy.redaction import register_runtime_secrets

_PLACEHOLDER_VALUES = frozenset(
    {
        "",
        "changeme",
        "change-me",
        "replace-me",
        "your-key-here",
        "xxx",
        "minioadmin",
    }
)


def _is_placeholder(value: str) -> bool:
    normalized = value.strip().lower()
    return not normalized or normalized in _PLACEHOLDER_VALUES


def register_secrets_for_redaction() -> None:
    register_runtime_secrets(
        settings.vault_encryption_key,
        settings.llm_api_key,
        settings.secret_key,
        settings.minio_access_key,
        settings.minio_secret_key,
    )


def validate_startup_secrets() -> None:
    """Refuse boot when required secrets are missing or placeholder (non-dev)."""
    register_secrets_for_redaction()
    if settings.dev_auth_bypass and settings.jober_env not in ("development", "test"):
        msg = "DEV_AUTH_BYPASS is only allowed in development or test environments"
        raise RuntimeError(msg)
    if settings.jober_env == "production" and settings.dev_auth_bypass:
        msg = "DEV_AUTH_BYPASS must be disabled in production"
        raise RuntimeError(msg)
    if os.getenv("CI") == "true":
        return
    if settings.jober_env == "development" and not settings.require_secrets:
        return
    if _is_placeholder(settings.vault_encryption_key):
        msg = "VAULT_ENCRYPTION_KEY is missing or a placeholder — set a Fernet key before starting"
        raise RuntimeError(msg)
    if _is_placeholder(settings.secret_key):
        msg = "SECRET_KEY is missing or a placeholder — set a strong secret before starting"
        raise RuntimeError(msg)
