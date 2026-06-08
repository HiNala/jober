import os
import time
from collections.abc import AsyncGenerator, Generator

# Worker sync sessions read DATABASE_URL via pydantic-settings (Playwright fill tests).
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://jober:jober@localhost:5432/jober?ssl=disable",
)

import httpx
import pytest
import pytest_asyncio
from cryptography.fernet import Fernet
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from jober_api.auth.constants import DEFAULT_DEV_TENANT_ID, DEFAULT_DEV_USER_ID
from jober_api.config import settings
from jober_api.db.base import Base
from jober_api.models import (  # noqa: F401 — register mappers
    ApplicationAttempt,
    ApplicationBatch,
    ApplicationRun,
    AuditLogEntry,
    AuthToken,
    BatchItem,
    BrowserEvent,
    CompanyBoard,
    CoverLetterAngle,
    FailureEvent,
    FieldMappingMemory,
    FormFieldObservation,
    GeneratedDocument,
    HumanCheckpoint,
    JobTarget,
    LlmCall,
    ProfileCommonAnswer,
    ResumeAsset,
    RunEvent,
    Tenant,
    User,
    UserProfile,
)
from jober_api.models.enums import PlanTier, UserStatus
from jober_api.repositories.base import Repository

requires_db = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres (CI or RUN_DB_TESTS=1)",
)

pytestmark_policy = pytest.mark.policy


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


@pytest.fixture(scope="session")
def fixture_server_url() -> Generator[str, None, None]:
    if os.getenv("SKIP_FIXTURE_SERVER") == "1":
        pytest.skip("fixture server disabled")
    from jober_fixtures.server import FixtureServer

    port = int(os.getenv("FIXTURE_ATS_PORT", "8765"))
    server = FixtureServer(port=port)
    url = server.start()
    for _ in range(50):
        try:
            httpx.get(f"{url}/health", timeout=1.0).raise_for_status()
            break
        except Exception:
            time.sleep(0.1)
    else:
        pytest.fail("ATS fixture server failed to start")
    yield url
    server.stop()


@pytest_asyncio.fixture
async def db_engine(database_url: str, vault_key: str, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "vault_encryption_key", vault_key)
    monkeypatch.setattr(settings, "auth_mode", "dev")
    engine = create_async_engine(database_url, connect_args={"ssl": False})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    monkeypatch.setattr("jober_api.db.session.async_session_factory", factory)
    monkeypatch.setattr("jober_api.auth.middleware.async_session_factory", factory)
    yield engine
    await engine.dispose()


@pytest.fixture(autouse=True)
def inject_default_tenant_on_create(monkeypatch: pytest.MonkeyPatch) -> None:
    original_create = Repository.create

    async def patched_create(self, **fields: object):
        if hasattr(self._model, "tenant_id") and "tenant_id" not in fields:
            repo_tenant = getattr(self, "_tenant_id", None)
            fields["tenant_id"] = repo_tenant or DEFAULT_DEV_TENANT_ID
        return await original_create(self, **fields)

    monkeypatch.setattr(Repository, "create", patched_create)


async def _seed_default_tenant(engine) -> None:
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        session.add(
            Tenant(
                id=DEFAULT_DEV_TENANT_ID,
                name="Test Tenant",
                plan=PlanTier.PRO,
                policy={
                    "default_run_policy": "review_before_submit",
                    "auto_submit_opt_in": False,
                },
            )
        )
        session.add(
            User(
                id=DEFAULT_DEV_USER_ID,
                tenant_id=DEFAULT_DEV_TENANT_ID,
                email="dev@test.local",
                display_name="Test User",
                status=UserStatus.ACTIVE,
            )
        )
        await session.commit()


@pytest_asyncio.fixture(autouse=True)
async def seed_default_tenant(
    db_engine, request: pytest.FixtureRequest
) -> AsyncGenerator[None, None]:
    if "truncate_tables" not in request.fixturenames:
        await _seed_default_tenant(db_engine)
    yield


@pytest_asyncio.fixture(autouse=True)
async def reset_redis_client_between_tests() -> AsyncGenerator[None, None]:
    from jober_api.auth.redis_client import close_redis

    await close_redis()
    yield
    await close_redis()


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {
        "X-Jober-Tenant-Id": str(DEFAULT_DEV_TENANT_ID),
        "X-Jober-User-Id": str(DEFAULT_DEV_USER_ID),
    }


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
    await _seed_default_tenant(db_engine)
    yield
