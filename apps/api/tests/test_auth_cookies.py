from __future__ import annotations

import pytest
from starlette.responses import Response

from jober_api.auth.cookies import _cookie_samesite, set_auth_cookies
from jober_api.config import settings


def test_cookie_samesite_none_when_secure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "cookie_secure", True)
    assert _cookie_samesite() == "none"


def test_cookie_samesite_lax_when_not_secure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "cookie_secure", False)
    assert _cookie_samesite() == "lax"


def test_auth_cookies_set_expected_flags(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "cookie_secure", True)
    response = Response()
    set_auth_cookies(response, "sess", "refr", "csrf-tok")
    set_cookie_headers = [
        value.decode("latin-1")
        for key, value in response.raw_headers
        if key.lower() == b"set-cookie"
    ]
    assert len(set_cookie_headers) == 3
    session_line = next(
        line for line in set_cookie_headers if line.startswith(f"{settings.session_cookie_name}=")
    )
    csrf_name = settings.csrf_cookie_name
    csrf_line = next(line for line in set_cookie_headers if line.startswith(f"{csrf_name}="))
    assert "HttpOnly" in session_line
    assert "Secure" in session_line
    assert "samesite=none" in session_line.lower()
    assert "httponly" not in csrf_line.lower()


def test_production_requires_cookie_secure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "jober_env", "production")
    monkeypatch.setattr(settings, "auth_mode", "native")
    monkeypatch.setattr(settings, "dev_auth_bypass", False)
    monkeypatch.setattr(settings, "cookie_secure", False)
    vault_key = "w-CndrrLpumBk62xq-1SBueyOre-DhzV_gGc86LmvnQ="
    monkeypatch.setattr(settings, "vault_encryption_key", vault_key)
    monkeypatch.setattr(settings, "secret_key", "production-secret-key-value")
    monkeypatch.setattr(settings, "minio_access_key", "real-access-key")
    monkeypatch.setattr(settings, "minio_secret_key", "real-secret-key")
    from jober_api.privacy.secrets_check import validate_startup_secrets

    with pytest.raises(RuntimeError, match="COOKIE_SECURE"):
        validate_startup_secrets()
