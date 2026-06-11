from __future__ import annotations

import pytest

from jober_api.config import Settings
from jober_api.privacy.secrets_check import validate_startup_secrets


def test_startup_rejects_placeholder_secrets_in_production(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CI", "")
    prod_settings = Settings(
        jober_env="production",
        auth_mode="native",
        cookie_secure=True,
        vault_encryption_key="changeme",
        secret_key="changeme",
        minio_access_key="prod-minio-key",
        minio_secret_key="prod-minio-secret",
    )
    monkeypatch.setattr("jober_api.privacy.secrets_check.settings", prod_settings)
    with pytest.raises(RuntimeError, match="VAULT_ENCRYPTION_KEY"):
        validate_startup_secrets()


def test_startup_rejects_dev_auth_mode_in_production(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CI", "")
    prod_settings = Settings(
        jober_env="production",
        auth_mode="dev",
        cookie_secure=True,
        vault_encryption_key="real-key-value-here-32chars!!",
        secret_key="real-secret-key-value-here!!",
        minio_access_key="prod-minio-key",
        minio_secret_key="prod-minio-secret",
    )
    monkeypatch.setattr("jober_api.privacy.secrets_check.settings", prod_settings)
    with pytest.raises(RuntimeError, match="AUTH_MODE=dev"):
        validate_startup_secrets()


def test_startup_rejects_dev_auth_bypass_in_production(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CI", "")
    prod_settings = Settings(
        jober_env="production",
        auth_mode="native",
        dev_auth_bypass=True,
        cookie_secure=True,
        vault_encryption_key="real-key-value-here-32chars!!",
        secret_key="real-secret-key-value-here!!",
        minio_access_key="prod-minio-key",
        minio_secret_key="prod-minio-secret",
    )
    monkeypatch.setattr("jober_api.privacy.secrets_check.settings", prod_settings)
    with pytest.raises(RuntimeError, match="DEV_AUTH_BYPASS"):
        validate_startup_secrets()


def test_startup_allows_development_without_secrets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CI", "")
    dev_settings = Settings(
        jober_env="development",
        vault_encryption_key="",
        secret_key="",
        require_secrets=False,
    )
    monkeypatch.setattr("jober_api.privacy.secrets_check.settings", dev_settings)
    validate_startup_secrets()
