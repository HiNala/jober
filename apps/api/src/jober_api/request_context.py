"""Request-scoped context (correlation id) for logging and Celery propagation."""

from __future__ import annotations

from contextvars import ContextVar

_correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def bind_correlation_id(correlation_id: str) -> None:
    _correlation_id.set(correlation_id)


def current_correlation_id() -> str | None:
    return _correlation_id.get()


def clear_correlation_id() -> None:
    _correlation_id.set(None)
