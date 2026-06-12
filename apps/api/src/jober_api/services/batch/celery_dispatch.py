from __future__ import annotations

from jober_api.celery_enqueue import enqueue_task


def dispatch_batch_tick(batch_id: str | None = None) -> str | None:
    try:
        from jober_worker.tasks import batch_orchestrator_tick

        result = enqueue_task(batch_orchestrator_tick, batch_id)
        return str(result.id)
    except Exception:
        return None


def dispatch_batch_item(item_id: str) -> str | None:
    try:
        from jober_worker.tasks import execute_batch_item

        result = enqueue_task(execute_batch_item, item_id)
        return str(result.id)
    except Exception:
        return None
