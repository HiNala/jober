from __future__ import annotations

import re
from typing import Any

_ALREADY_APPLIED_PATTERNS = (
    r"already\s+applied",
    r"previously\s+submitted",
    r"duplicate\s+application",
    r"you\s+have\s+already\s+applied",
)


def detect_already_applied_on_page(*, html: str, visible_text: str) -> bool:
    combined = f"{visible_text}\n{html}".lower()
    return any(re.search(pattern, combined) for pattern in _ALREADY_APPLIED_PATTERNS)


def has_prior_successful_run(runs: list[Any]) -> bool:
    for run in runs:
        status = getattr(run, "status", None)
        value = status.value if hasattr(status, "value") else str(status)
        if value == "succeeded":
            return True
    return False
