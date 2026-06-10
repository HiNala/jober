from __future__ import annotations

import pytest

from jober_api.config import settings
from jober_api.services.ops import alerting


@pytest.mark.asyncio
async def test_dispatch_ops_alerts_skips_without_webhook(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "ops_alert_webhook_url", "")
    sent = await alerting.dispatch_ops_alerts(
        "test",
        [{"level": "error", "message": "infra down"}],
        force=True,
    )
    assert sent is False


@pytest.mark.asyncio
async def test_dispatch_ops_alerts_respects_cooldown(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "ops_alert_webhook_url", "https://hooks.example/alert")
    monkeypatch.setattr(settings, "ops_alert_cooldown_seconds", 60)
    monkeypatch.setattr(alerting, "_should_fire", lambda _fp: False)

    sent = await alerting.dispatch_ops_alerts(
        "test",
        [{"level": "error", "message": "duplicate"}],
    )
    assert sent is False


@pytest.mark.asyncio
async def test_dispatch_ops_alerts_posts_webhook(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    posted: list[dict[str, object]] = []

    class _FakeResponse:
        def raise_for_status(self) -> None:
            return None

    class _FakeClient:
        async def __aenter__(self) -> _FakeClient:
            return self

        async def __aexit__(self, *_args: object) -> None:
            return None

        async def post(self, url: str, json: dict[str, object]) -> _FakeResponse:
            posted.append({"url": url, "json": json})
            return _FakeResponse()

    monkeypatch.setattr(settings, "ops_alert_webhook_url", "https://hooks.example/alert")
    monkeypatch.setattr(alerting, "_should_fire", lambda _fp: True)
    monkeypatch.setattr(alerting.httpx, "AsyncClient", lambda **_kw: _FakeClient())

    sent = await alerting.dispatch_ops_alerts(
        "test",
        [{"level": "error", "message": "infra down"}],
        force=True,
    )
    assert sent is True
    assert len(posted) == 1
    assert posted[0]["url"] == "https://hooks.example/alert"
    json_body = posted[0]["json"]
    assert isinstance(json_body, dict)
    assert json_body["source"] == "test"
    attention = json_body["attention"]
    assert isinstance(attention, list)
    assert attention[0]["level"] == "error"
