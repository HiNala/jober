from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from jober_schemas.common import TimestampedSchema
from jober_schemas.enums import FieldObservationStatus


class FormFieldObservationRead(TimestampedSchema):
    id: str
    attempt_id: str
    field_key: str
    label: str | None
    field_type: str | None
    required: bool
    options: list[str] | None = None
    mapped_profile_field: str | None
    proposed_value_redacted: str | None
    confidence: float | None
    status: FieldObservationStatus
    evidence: dict[str, Any] | None = None


class FormDiscoveryRead(BaseModel):
    run_id: str
    attempt_id: str
    platform: str | None
    step_count: int
    items: list[FormFieldObservationRead]


class FormFieldObservationUpdate(BaseModel):
    mapped_profile_field: str | None = None
    status: FieldObservationStatus | None = None
