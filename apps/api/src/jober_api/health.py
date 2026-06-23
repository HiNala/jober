from typing import Any

import redis.asyncio as aioredis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from jober_api.config import settings
from jober_api.db.session import engine
from jober_api.storage.minio_client import ObjectStorage


async def check_postgres(db_engine: AsyncEngine) -> tuple[bool, str]:
    try:
        async with db_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True, "ok"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


async def check_redis(url: str) -> tuple[bool, str]:
    try:
        async with aioredis.from_url(url, socket_connect_timeout=2) as client:
            pong = await client.ping()
        return (pong is True, "ok" if pong else "no pong")
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


async def check_minio() -> tuple[bool, str]:
    try:
        storage = ObjectStorage()
        exists = await storage.bucket_exists()
        if not exists:
            return False, f"bucket '{settings.minio_bucket}' not found"
        return True, "ok"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


async def readiness_report(database_url: str, redis_url: str) -> dict[str, Any]:
    del database_url  # shared pool via db.session.engine
    pg_ok, pg_msg = await check_postgres(engine)
    redis_ok, redis_msg = await check_redis(redis_url)
    minio_ok, minio_msg = await check_minio()

    checks = {
        "postgres": {"ok": pg_ok, "detail": pg_msg},
        "redis": {"ok": redis_ok, "detail": redis_msg},
        "minio": {"ok": minio_ok, "detail": minio_msg},
    }
    all_ok = pg_ok and redis_ok and minio_ok
    return {"status": "ready" if all_ok else "not_ready", "checks": checks}
