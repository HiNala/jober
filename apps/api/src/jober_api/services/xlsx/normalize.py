from __future__ import annotations

import re
from datetime import date, datetime
from urllib.parse import urlparse

from jober_api.models.enums import JobTargetStatus

_STATUS_MAP: dict[str, JobTargetStatus] = {
    "not started": JobTargetStatus.NEW,
    "new": JobTargetStatus.NEW,
    "queued": JobTargetStatus.QUEUED,
    "in progress": JobTargetStatus.IN_PROGRESS,
    "running": JobTargetStatus.IN_PROGRESS,
    "applied": JobTargetStatus.APPLIED,
    "rejected": JobTargetStatus.REJECTED,
    "withdrawn": JobTargetStatus.WITHDRAWN,
    "skipped": JobTargetStatus.SKIPPED,
}

_EXPORT_STATUS: dict[JobTargetStatus, str] = {
    JobTargetStatus.NEW: "Not started",
    JobTargetStatus.QUEUED: "Queued",
    JobTargetStatus.IN_PROGRESS: "In progress",
    JobTargetStatus.APPLIED: "Applied",
    JobTargetStatus.REJECTED: "Rejected",
    JobTargetStatus.WITHDRAWN: "Withdrawn",
    JobTargetStatus.SKIPPED: "Skipped",
}


def clean_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def normalize_priority(value: object) -> str | None:
    text = clean_text(value)
    if not text:
        return None
    letter = text.upper()[0]
    if letter in {"A", "B", "C"}:
        return letter
    return text.upper()[:8]


def parse_date(value: object) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def parse_int(value: object) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(str(value)))
    except ValueError:
        return None


def normalize_url(value: object) -> tuple[str | None, str | None]:
    text = clean_text(value)
    if not text:
        return None, None
    if not re.match(r"^https?://", text, re.I):
        text = f"https://{text}"
    parsed = urlparse(text)
    if not parsed.netloc:
        return None, "invalid_url"
    return text, None


def parse_status(value: object) -> JobTargetStatus:
    text = clean_text(value)
    if not text:
        return JobTargetStatus.NEW
    key = text.lower()
    return _STATUS_MAP.get(key, JobTargetStatus.NEW)


def export_status(status: JobTargetStatus) -> str:
    return _EXPORT_STATUS.get(status, status.value)
