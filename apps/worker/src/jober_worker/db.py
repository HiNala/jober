from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from jober_worker.config import settings


def _sync_database_url() -> str:
    url = settings.database_url
    if url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    # psycopg does not accept asyncpg's `ssl=disable` query param
    url = url.replace("?ssl=disable", "").replace("&ssl=disable", "")
    lowered_source = settings.database_url.lower()
    if (
        "sslmode=" not in url
        and "ssl=disable" not in lowered_source
        and "sslmode=disable" not in lowered_source
    ):
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}sslmode=require"
    return url


_engine = create_engine(_sync_database_url(), pool_pre_ping=True)
_SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)


@contextmanager
def get_sync_session() -> Iterator[Session]:
    session = _SessionLocal()
    try:
        yield session
    finally:
        session.close()
