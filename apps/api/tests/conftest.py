import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from cryptography.fernet import Fernet
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from jober_api.config import settings
from jober_api.db.base import Base
from jober_api.models import (  # noqa: F401 — register mappers
    ApplicationAttempt,
    ApplicationRun,
    BrowserEvent,
    CompanyBoard,
    CoverLetterAngle,
    FormFieldObservation,
    GeneratedDocument,
    HumanCheckpoint,
    JobTarget,
    LlmCall,
    ProfileCommonAnswer,
    ResumeAsset,
    UserProfile,
)

requires_db = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres (CI or RUN_DB_TESTS=1)",
)


@pytest.fixture(scope="session")
def database_url() -> str:
    return os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://jober:jober@localhost:5432/jober?ssl=disable",
    )


@pytest.fixture(scope="session")
def vault_key() -> str:
    key = os.getenv("VAULT_ENCRYPTION_KEY")
    if not key:
        key = Fernet.generate_key().decode("utf-8")
    return key


@pytest_asyncio.fixture
async def db_engine(database_url: str, vault_key: str, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "vault_encryption_key", vault_key)
    engine = create_async_engine(database_url, connect_args={"ssl": False})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def raw_connection(database_url: str):
    engine = create_async_engine(database_url, connect_args={"ssl": False})
    async with engine.connect() as conn:
        yield conn
    await engine.dispose()


@pytest_asyncio.fixture
async def truncate_tables(db_engine) -> AsyncGenerator[None, None]:
    tables = ", ".join(f'"{t.name}"' for t in reversed(Base.metadata.sorted_tables))
    async with db_engine.begin() as conn:
        await conn.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))
    yield
