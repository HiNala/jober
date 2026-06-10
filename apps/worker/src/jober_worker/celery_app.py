from celery import Celery
from celery.schedules import crontab

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
