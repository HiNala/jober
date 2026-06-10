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
