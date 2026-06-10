from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from jober_api.config import settings
from jober_api.db.base import Base
from jober_api.db.connect import asyncpg_connect_args

engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args=asyncpg_connect_args(settings.database_url),
)

async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
