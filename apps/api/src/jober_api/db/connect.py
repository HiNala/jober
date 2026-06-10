"""Database connection helpers — SSL for managed Postgres (Railway, etc.)."""

from __future__ import annotations

import os


def asyncpg_connect_args(database_url: str) -> dict[str, object]:
    """Return asyncpg ``connect_args`` for SQLAlchemy based on URL and env."""
    lowered = database_url.lower()
    if "ssl=disable" in lowered or "sslmode=disable" in lowered:
        return {"ssl": False}
    if any(
        token in lowered
        for token in ("ssl=require", "sslmode=require", "sslmode=verify-full", "sslmode=verify-ca")
    ):
        return {"ssl": True}
    ssl_env = os.getenv("DATABASE_SSL", "").strip().lower()
    if ssl_env in {"1", "true", "require", "yes"}:
        return {"ssl": True}
    if os.getenv("JOBER_ENV", "").strip().lower() == "production":
        return {"ssl": True}
    return {"ssl": False}
