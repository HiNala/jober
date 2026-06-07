from __future__ import annotations

import logging
from typing import Any

from jober_api.config import settings
from jober_api.privacy.redaction import scrub_dict, scrub_text

_logger = logging.getLogger("jober")


def is_debug_logging() -> bool:
    return settings.log_mode == "debug"


def safe_log(level: int, message: str, **context: Any) -> None:
    """Structured-safe log line; secrets are scrubbed even in debug mode."""
    debug = is_debug_logging()
    scrubbed_message = scrub_text(message, debug=debug)
    if context:
        scrubbed_context = scrub_dict(context, debug=debug)
        _logger.log(level, "%s | %s", scrubbed_message, scrubbed_context)
    else:
        _logger.log(level, scrubbed_message)
