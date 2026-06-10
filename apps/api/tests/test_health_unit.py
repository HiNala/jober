"""Unit tests for readiness helpers (no external services required)."""

import pytest

from jober_api.health import check_minio, check_redis


@pytest.mark.asyncio
async def test_check_redis_fails_fast_on_bad_host() -> None:
    ok, detail = await check_redis("redis://127.0.0.1:1/0")
    assert ok is False
    assert detail


@pytest.mark.asyncio
async def test_check_minio_reports_missing_bucket(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeStorage:
        async def bucket_exists(self) -> bool:
            return False

    monkeypatch.setattr("jober_api.health.ObjectStorage", lambda: FakeStorage())

    ok, detail = await check_minio()
    assert ok is False
    assert "not found" in detail
