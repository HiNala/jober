from __future__ import annotations

import logging

from celery import Celery
from celery.schedules import crontab
from celery.signals import task_prerun

from jober_worker.config import settings

celery_app = Celery(
    "jober_worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["jober_worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    beat_schedule={
        "batch-orchestrator-tick": {
            "task": "jober_worker.tasks.batch_orchestrator_tick",
            "schedule": float(settings.batch_tick_seconds),
        },
        "analytics-daily-rollup": {
            "task": "jober_worker.tasks.analytics_daily_rollup",
            "schedule": crontab(hour=2, minute=15),
        },
        "analytics-retention-purge": {
            "task": "jober_worker.tasks.analytics_retention_purge",
            "schedule": crontab(hour=3, minute=30, day_of_week="sun"),
        },
        "run-artifact-retention-purge": {
            "task": "jober_worker.tasks.run_artifact_retention_purge",
            "schedule": crontab(hour=4, minute=0, day_of_week="sun"),
        },
    },
)


@task_prerun.connect  # type: ignore[untyped-decorator]
def _log_celery_task_prerun(
    task_id: str,
    task: object,
    *args: object,
    **kwargs: object,
) -> None:
    from jober_api.privacy.logging import safe_log

    request = getattr(task, "request", None)
    correlation_id: str | None = None
    if request is not None:
        headers = getattr(request, "headers", None) or {}
        if isinstance(headers, dict):
            raw = headers.get("correlation_id")
            if isinstance(raw, str) and raw:
                correlation_id = raw
    if correlation_id is None and args:
        first = args[0]
        if isinstance(first, dict):
            raw = first.get("correlation_id")
            if isinstance(raw, str) and raw:
                correlation_id = raw

    task_name = getattr(task, "name", "unknown")
    fields: dict[str, object] = {"task": task_name, "celery_task_id": task_id}
    if correlation_id:
        fields["correlation_id"] = correlation_id
    if len(args) >= 1 and isinstance(args[0], str):
        fields["arg0"] = args[0]
    safe_log(logging.INFO, "celery_task_start", **fields)
