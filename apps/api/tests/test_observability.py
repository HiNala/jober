from __future__ import annotations

import logging
import os
import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from jober_api.auth.constants import DEFAULT_DEV_TENANT_ID
from jober_api.celery_enqueue import enqueue_task
from jober_api.config import settings
from jober_api.models.application_run import ApplicationRun
from jober_api.models.enums import JobTargetStatus, RunStatus
from jober_api.models.job_target import JobTarget
from jober_api.request_context import bind_correlation_id, clear_correlation_id
from jober_api.services.admin.overview import _run_counts
from jober_api.services.ops import alerting
from jober_api.services.ops.alerting import (
    RUNBOOK_COST_SPIKE,
    alert_email_send_failed,
    ops_attention,
)

requires_postgres = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres",
)


def test_ops_attention_appends_runbook() -> None:
    item = ops_attention("warn", "Budget soft warn.", runbook=RUNBOOK_COST_SPIKE)
    assert item["runbook"] == RUNBOOK_COST_SPIKE
    assert RUNBOOK_COST_SPIKE in item["message"]


def test_enqueue_task_passes_correlation_header(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class _FakeTask:
        def apply_async(self, *, args, kwargs, headers):  # noqa: ANN001
            captured["args"] = args
            captured["kwargs"] = kwargs
            captured["headers"] = headers
            return MagicMock(id="task-1")

        def delay(self, *_args, **_kwargs):  # noqa: ANN001
            raise AssertionError("delay should not be used when correlation id is set")

    bind_correlation_id("corr-test-123")
    try:
        enqueue_task(_FakeTask(), "arg-a")
    finally:
        clear_correlation_id()

    assert captured["headers"] == {"correlation_id": "corr-test-123"}
    assert captured["args"] == ("arg-a",)


def test_alert_email_send_failed_posts_sync(monkeypatch: pytest.MonkeyPatch) -> None:
    posted: list[dict[str, object]] = []
    monkeypatch.setattr(settings, "ops_alert_webhook_url", "https://hooks.example/alert")
    monkeypatch.setattr(alerting, "_should_fire", lambda _fp: True)

    class _FakeResponse:
        def raise_for_status(self) -> None:
            return None

    class _FakeClient:
        def __enter__(self) -> _FakeClient:
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def post(self, url: str, json: dict[str, object]) -> _FakeResponse:
            posted.append({"url": url, "json": json})
            return _FakeResponse()

    monkeypatch.setattr(alerting.httpx, "Client", lambda **_kw: _FakeClient())

    alert_email_send_failed(
        to_email_masked="u***@example.com",
        subject="Verify your email",
        error="SMTP connection refused",
        correlation_id="cid-abc",
    )
    assert len(posted) == 1
    body = posted[0]["json"]
    assert isinstance(body, dict)
    assert body["source"] == "email_send_failed"
    attention = body["attention"]
    assert isinstance(attention, list)
    assert attention[0]["level"] == "error"
    assert "docs/runbooks/email-delivery.md" in str(attention[0])


@requires_postgres
@pytest.mark.asyncio
async def test_admin_overview_run_counts_match_raw_data(db_session, truncate_tables) -> None:
    target = JobTarget(
        id=uuid.uuid4(),
        tenant_id=DEFAULT_DEV_TENANT_ID,
        company="Acme",
        role="Engineer",
        status=JobTargetStatus.QUEUED,
    )
    db_session.add(target)
    await db_session.flush()
    now = datetime.now(UTC)
    db_session.add_all(
        [
            ApplicationRun(
                id=uuid.uuid4(),
                tenant_id=DEFAULT_DEV_TENANT_ID,
                job_target_id=target.id,
                status=RunStatus.SUCCEEDED,
                created_at=now,
            ),
            ApplicationRun(
                id=uuid.uuid4(),
                tenant_id=DEFAULT_DEV_TENANT_ID,
                job_target_id=target.id,
                status=RunStatus.FAILED_FINAL,
                created_at=now,
            ),
        ]
    )
    await db_session.commit()

    today = now.date()
    counts = await _run_counts(db_session, today - __import__("datetime").timedelta(days=29), today)
    assert counts["succeeded"] == 1
    assert counts["failed"] == 1
    assert counts["total"] == 2
    assert round(counts["succeeded"] / max(counts["succeeded"] + counts["failed"], 1), 4) == 0.5


@requires_postgres
@pytest.mark.asyncio
async def test_purge_run_emits_structured_log(
    db_session,
    truncate_tables,
    caplog: pytest.LogCaptureFixture,
) -> None:
    from jober_api.services.privacy.retention import purge_run

    target = JobTarget(
        id=uuid.uuid4(),
        tenant_id=DEFAULT_DEV_TENANT_ID,
        company="Acme",
        role="Engineer",
        status=JobTargetStatus.QUEUED,
    )
    run = ApplicationRun(
        id=uuid.uuid4(),
        tenant_id=DEFAULT_DEV_TENANT_ID,
        job_target_id=target.id,
        status=RunStatus.SUCCEEDED,
    )
    db_session.add_all([target, run])
    await db_session.commit()

    bind_correlation_id("purge-corr-1")
    caplog.set_level(logging.INFO, logger="jober")
    try:
        await purge_run(db_session, run.id, tenant_id=DEFAULT_DEV_TENANT_ID)
    finally:
        clear_correlation_id()

    assert any("run_purged" in r.message and "purge-corr-1" in r.message for r in caplog.records)
