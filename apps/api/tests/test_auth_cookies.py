from __future__ import annotations

import pytest

from jober_api.auth.cookies import _cookie_samesite
from jober_api.config import settings


def test_cookie_samesite_none_when_secure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "cookie_secure", True)
    assert _cookie_samesite() == "none"


def test_cookie_samesite_lax_when_not_secure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "cookie_secure", False)
    assert _cookie_samesite() == "lax"
