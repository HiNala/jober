import asyncio
from typing import Any

import redis.asyncio as aioredis
from minio import Minio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from jober_api.config import settings


async def check_postgres(engine: AsyncEngine) -> tuple[bool, str]:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True, "ok"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


async def check_redis(url: str) -> tuple[bool, str]:
    client = aioredis.from_url(url, socket_connect_timeout=2)
    try:
        pong = await client.ping()
        return (pong is True, "ok" if pong else "no pong")
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)
    finally:
        await client.close()


def check_minio() -> tuple[bool, str]:
    try:
        client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        exists = client.bucket_exists(settings.minio_bucket)
        if not exists:
            return False, f"bucket '{settings.minio_bucket}' not found"
        return True, "ok"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


async def readiness_report(database_url: str, redis_url: str) -> dict[str, Any]:
    engine = create_async_engine(
        database_url,
        pool_pre_ping=True,
        connect_args={"ssl": False},
    )
    try:
        pg_ok, pg_msg = await check_postgres(engine)
        redis_ok, redis_msg = await check_redis(redis_url)
        minio_ok, minio_msg = await asyncio.to_thread(check_minio)

        checks = {
            "postgres": {"ok": pg_ok, "detail": pg_msg},
            "redis": {"ok": redis_ok, "detail": redis_msg},
            "minio": {"ok": minio_ok, "detail": minio_msg},
        }
        all_ok = pg_ok and redis_ok and minio_ok
        return {"status": "ready" if all_ok else "not_ready", "checks": checks}
    finally:
        await engine.dispose()
