from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from jober_forms.mapper import UPLOAD_FIELD_KEYS
from jober_forms.redact import redact_value

HIGH_CONFIDENCE = 0.82
LOW_CONFIDENCE = 0.65


@dataclass(frozen=True)
class ObservationDraft:
    mapped_profile_field: str | None
    proposed_value_redacted: str | None
    confidence: float
    status: str
    evidence: dict[str, Any]


def apply_confidence_policy(
    *,
    mapped_field: str | None,
    confidence: float,
    fill_outcome: str,
    fill_value: Any,
    field_type: str | None,
    is_sensitive: bool,
    is_ambiguous: bool,
    is_upload: bool,
) -> ObservationDraft:
    """Map fill resolution + confidence to FieldObservationStatus string values."""
    redacted = redact_value(fill_value, field_type=field_type)

    if is_upload or mapped_field in UPLOAD_FIELD_KEYS:
        return ObservationDraft(
            mapped_profile_field=mapped_field,
            proposed_value_redacted="[file upload]",
            confidence=confidence,
            status="needs_review",
            evidence={"upload": True},
        )

    if is_sensitive:
        return ObservationDraft(
            mapped_profile_field=mapped_field,
            proposed_value_redacted=redacted,
            confidence=confidence,
            status="needs_review",
            evidence={"sensitive": True},
        )

    if is_ambiguous or confidence < LOW_CONFIDENCE:
        return ObservationDraft(
            mapped_profile_field=mapped_field,
            proposed_value_redacted=redacted,
            confidence=confidence,
            status="needs_review",
            evidence={"reason": "low_confidence_or_ambiguous"},
        )

    if fill_outcome != "value" and confidence < HIGH_CONFIDENCE:
        return ObservationDraft(
            mapped_profile_field=mapped_field,
            proposed_value_redacted=redacted,
            confidence=confidence,
            status="needs_review",
            evidence={"reason": "no_stored_value"},
        )

    if confidence >= HIGH_CONFIDENCE:
        return ObservationDraft(
            mapped_profile_field=mapped_field,
            proposed_value_redacted=redacted,
            confidence=confidence,
            status="skipped",
            evidence={"reason": "eligible_for_autofill"},
        )

    return ObservationDraft(
        mapped_profile_field=mapped_field,
        proposed_value_redacted=redacted,
        confidence=confidence,
        status="needs_review",
        evidence={"reason": "medium_confidence"},
    )
