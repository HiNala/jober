from __future__ import annotations

import pytest

from jober_api.config import Settings


def test_database_url_rewrites_postgresql_to_asyncpg(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://postgres:secret@postgres.railway.internal:5432/railway",
    )
    settings = Settings()
    assert settings.database_url.startswith("postgresql+asyncpg://")
