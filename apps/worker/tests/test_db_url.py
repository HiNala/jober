from __future__ import annotations

import pytest

from jober_worker import db
from jober_worker.config import Settings


def test_sync_database_url_uses_psycopg_driver_for_railway(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        db,
        "settings",
        Settings(
            database_url="postgresql://postgres:secret@postgres.railway.internal:5432/railway",
        ),
    )
    url = db._sync_database_url()
    assert url.startswith("postgresql+psycopg://")
    assert "sslmode=require" in url


def test_sync_database_url_skips_ssl_for_local_disable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        db,
        "settings",
        Settings(
            database_url=(
                "postgresql+asyncpg://jober:jober@localhost:5432/jober?ssl=disable"
            ),
        ),
    )
    url = db._sync_database_url()
    assert url.startswith("postgresql+psycopg://")
    assert "sslmode=require" not in url
