from __future__ import annotations

import os


def dispatch_extract_job(
    run_id: str,
    job_target_id: str,
    url: str,
    force: bool,
) -> str | None:
    """Enqueue worker task via Celery send_task (no hard dependency on worker package)."""
    broker = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    del broker
    try:
        from celery import Celery

        client = Celery(broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"))
        result = client.send_task(
            "jober_worker.tasks.extract_job",
            args=[run_id, job_target_id, url, force],
        )
        return str(result.id)
    except Exception:
        return None
