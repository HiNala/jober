"""Enqueue Celery tasks with request correlation id in headers."""

from __future__ import annotations

from typing import Any

from celery import Task

from jober_api.request_context import current_correlation_id


def enqueue_task(task: Task, *args: Any, **kwargs: Any) -> Any:
    """apply_async with correlation_id header when bound on the request."""
    correlation_id = current_correlation_id()
    if correlation_id:
        return task.apply_async(
            args=args,
            kwargs=kwargs,
            headers={"correlation_id": correlation_id},
        )
    return task.delay(*args, **kwargs)
