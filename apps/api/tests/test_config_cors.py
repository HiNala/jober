from __future__ import annotations

import pytest

from jober_api.config import Settings


def test_cors_origins_parses_comma_separated_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", "https://a.example.com, https://b.example.com")
    settings = Settings()
    assert settings.cors_origins == ["https://a.example.com", "https://b.example.com"]
