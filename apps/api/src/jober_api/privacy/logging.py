from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any

from jober_api.config import settings
from jober_api.privacy.redaction import scrub_dict, scrub_text

_logger = logging.getLogger("jober")


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": scrub_text(record.getMessage(), debug=is_debug_logging()),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def is_debug_logging() -> bool:
    return settings.log_mode == "debug"


def configure_logging() -> None:
    """Configure root logging — JSON lines when LOG_FORMAT=json (Railway drains)."""
    root = logging.getLogger()
    if root.handlers:
        return
    handler = logging.StreamHandler()
    if settings.log_format.strip().lower() == "json":
        handler.setFormatter(_JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"),
        )
    root.addHandler(handler)
    root.setLevel(logging.INFO)
    logging.getLogger("jober").setLevel(logging.INFO)


def safe_log(level: int, message: str, **context: Any) -> None:
    """Structured-safe log line; secrets are scrubbed even in debug mode."""
    debug = is_debug_logging()
    scrubbed_message = scrub_text(message, debug=debug)
    if context:
        scrubbed_context = scrub_dict(context, debug=debug)
        if settings.log_format.strip().lower() == "json":
            _logger.log(
                level,
                "%s | %s",
                scrubbed_message,
                json.dumps(scrubbed_context, default=str),
            )
        else:
            _logger.log(level, "%s | %s", scrubbed_message, scrubbed_context)
    else:
        _logger.log(level, scrubbed_message)


def init_sentry() -> None:
    dsn = settings.sentry_dsn.strip()
    if not dsn:
        return
    try:
        import sentry_sdk  # type: ignore[import-not-found]
        from sentry_sdk.integrations.fastapi import FastApiIntegration  # type: ignore[import-not-found]
    except ImportError:
        safe_log(logging.WARNING, "sentry-sdk not installed; error tracking disabled")
        return
    sentry_sdk.init(
        dsn=dsn,
        environment=settings.jober_env,
        integrations=[FastApiIntegration()],
        send_default_pii=False,
        traces_sample_rate=0.1 if settings.jober_env == "production" else 0.0,
    )
