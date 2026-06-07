from __future__ import annotations


def dispatch_batch_tick(batch_id: str | None = None) -> str | None:
    try:
        from jober_worker.tasks import batch_orchestrator_tick

        result = batch_orchestrator_tick.delay(batch_id)
        return str(result.id)
    except Exception:
        return None


def dispatch_batch_item(item_id: str) -> str | None:
    try:
        from jober_worker.tasks import execute_batch_item

        result = execute_batch_item.delay(item_id)
        return str(result.id)
    except Exception:
        return None
