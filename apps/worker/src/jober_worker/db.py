from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from jober_worker.config import settings


def _sync_database_url() -> str:
    url = settings.database_url.replace("postgresql+asyncpg://", "postgresql+psycopg://")
    # psycopg does not accept asyncpg's `ssl=disable` query param
    if "?ssl=disable" in url:
        url = url.replace("?ssl=disable", "")
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
