from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class SubmissionOutcome(StrEnum):
    SUCCESS = "success"
    ALREADY_APPLIED = "already_applied"
    UNCERTAIN = "uncertain"
    FAILED = "failed"


_SUCCESS_PATTERNS = (
    r"application\s+received",
    r"thank\s+you\s+for\s+applying",
    r"successfully\s+submitted",
    r"application\s+submitted",
    r"we\s+received\s+your\s+application",
    r"thanks\s+for\s+applying",
)

_ALREADY_APPLIED_PATTERNS = (
    r"already\s+applied",
    r"previously\s+submitted",
    r"duplicate\s+application",
    r"you\s+have\s+already\s+applied",
    r"application\s+on\s+file",
)

_UNCERTAIN_PATTERNS = (
    r"check\s+your\s+email",
    r"being\s+processed",
    r"may\s+take\s+a\s+few",
    r"confirmation\s+email",
)


@dataclass(frozen=True)
class SubmissionVerification:
    outcome: SubmissionOutcome
    confirmation_text: str | None
    final_url: str | None
    evidence: dict[str, Any] = field(default_factory=dict)
    note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome": self.outcome.value,
            "confirmation_text": self.confirmation_text,
            "final_url": self.final_url,
            "evidence": self.evidence,
            "note": self.note,
        }


def _first_match(text: str, patterns: tuple[str, ...]) -> str | None:
    lowered = text.lower()
    for pattern in patterns:
        match = re.search(pattern, lowered)
        if match:
            start = max(0, match.start() - 40)
            end = min(len(text), match.end() + 80)
            return text[start:end].strip()
    return None


def classify_submission(
    *,
    html: str,
    visible_text: str,
    final_url: str | None,
    before_url: str | None = None,
    submit_clicked: bool = True,
) -> SubmissionVerification:
    combined = f"{visible_text}\n{html}"
    evidence: dict[str, Any] = {
        "submit_clicked": submit_clicked,
        "url_changed": bool(before_url and final_url and before_url != final_url),
    }

    already = _first_match(combined, _ALREADY_APPLIED_PATTERNS)
    if already:
        return SubmissionVerification(
            outcome=SubmissionOutcome.ALREADY_APPLIED,
            confirmation_text=already,
            final_url=final_url,
            evidence=evidence,
            note="Detected prior application — submission skipped",
        )

    if not submit_clicked:
        return SubmissionVerification(
            outcome=SubmissionOutcome.FAILED,
            confirmation_text=None,
            final_url=final_url,
            evidence=evidence,
            note="Submit action was not performed",
        )

    success = _first_match(combined, _SUCCESS_PATTERNS)
    if success:
        return SubmissionVerification(
            outcome=SubmissionOutcome.SUCCESS,
            confirmation_text=success,
            final_url=final_url,
            evidence=evidence,
            note="On-page confirmation captured; email confirmation may follow",
        )

    uncertain = _first_match(combined, _UNCERTAIN_PATTERNS)
    if uncertain or (before_url and final_url and before_url == final_url):
        return SubmissionVerification(
            outcome=SubmissionOutcome.UNCERTAIN,
            confirmation_text=uncertain,
            final_url=final_url,
            evidence=evidence,
            note="Confirmation unclear — human verification required",
        )

    return SubmissionVerification(
        outcome=SubmissionOutcome.UNCERTAIN,
        confirmation_text=visible_text[:240] if visible_text else None,
        final_url=final_url,
        evidence=evidence,
        note="No confident success signal — flagged for human verification",
    )
