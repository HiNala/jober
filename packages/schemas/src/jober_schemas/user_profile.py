from typing import Any
from uuid import UUID

from pydantic import Field

from jober_schemas.common import SchemaBase, TimestampedSchema


class FieldConsentFlags(SchemaBase):
    consent: bool = False
    never_autofill: bool = False


class UserProfileCreate(SchemaBase):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    links: dict[str, str] | None = None
    work_authorization: str | None = None
    relocation_pref: bool | None = None
    onsite_pref: bool | None = None
    hybrid_pref: bool | None = None
    salary_prefs: dict[str, Any] | None = None
    sensitive_eeo_answers: str | None = None
    default_resume_asset_id: UUID | None = None
    cover_letter_style_prefs: dict[str, Any] | None = None
    field_consent: dict[str, FieldConsentFlags] | None = None


class UserProfileRead(TimestampedSchema):
    name: str | None
    email: str | None
    phone: str | None
    location: str | None
    links: dict[str, Any] | None
    work_authorization: str | None
    relocation_pref: bool | None
    onsite_pref: bool | None
    hybrid_pref: bool | None
    salary_prefs: dict[str, Any] | None
    default_resume_asset_id: UUID | None
    cover_letter_style_prefs: dict[str, Any] | None
    profile_completeness_score: float | None
    field_consent: dict[str, Any] | None
    has_sensitive_eeo: bool = Field(
        description="True when encrypted EEO answers are stored (never returned in API)."
    )
