from __future__ import annotations

import pytest

from jober_api.db.connect import asyncpg_connect_args


def test_asyncpg_ssl_disabled_in_url() -> None:
    url = "postgresql+asyncpg://u:p@localhost:5432/db?ssl=disable"
    assert asyncpg_connect_args(url) == {"ssl": False}


def test_asyncpg_ssl_required_in_url() -> None:
    url = "postgresql+asyncpg://u:p@host:5432/railway?sslmode=require"
    assert asyncpg_connect_args(url) == {"ssl": True}


def test_asyncpg_ssl_defaults_on_production_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JOBER_ENV", "production")
    url = "postgresql+asyncpg://u:p@host:5432/railway"
    assert asyncpg_connect_args(url) == {"ssl": True}


def test_asyncpg_ssl_disabled_on_railway_internal(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JOBER_ENV", "production")
    url = "postgresql://postgres:pw@postgres.railway.internal:5432/railway"
    assert asyncpg_connect_args(url) == {"ssl": False}
