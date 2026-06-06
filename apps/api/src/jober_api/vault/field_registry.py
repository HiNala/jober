from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FieldTier(str, Enum):
    PUBLIC = "public"
    PREFERENCE = "preference"
    SENSITIVE = "sensitive"


@dataclass(frozen=True)
class VaultFieldSpec:
    key: str
    label: str
    tier: FieldTier
    profile_attr: str | None = None
    sensitive_key: str | None = None


SENSITIVE_EEO_KEYS: tuple[str, ...] = (
    "work_authorization",
    "sponsorship_needed",
    "disability",
    "veteran_status",
    "race_ethnicity",
    "gender",
    "legal_authorization",
)

VAULT_FIELDS: tuple[VaultFieldSpec, ...] = (
    VaultFieldSpec("name", "Full name", FieldTier.PUBLIC, "name"),
    VaultFieldSpec("email", "Email", FieldTier.PUBLIC, "email"),
    VaultFieldSpec("phone", "Phone", FieldTier.PUBLIC, "phone"),
    VaultFieldSpec("location", "Location", FieldTier.PUBLIC, "location"),
    VaultFieldSpec("current_title", "Current title", FieldTier.PUBLIC, "current_title"),
    VaultFieldSpec("links", "Links", FieldTier.PUBLIC, "links"),
    VaultFieldSpec(
        "relocation_pref", "Open to relocation", FieldTier.PREFERENCE, "relocation_pref"
    ),
    VaultFieldSpec("onsite_pref", "Onsite OK", FieldTier.PREFERENCE, "onsite_pref"),
    VaultFieldSpec("hybrid_pref", "Hybrid OK", FieldTier.PREFERENCE, "hybrid_pref"),
    VaultFieldSpec("notice_period", "Notice period", FieldTier.PREFERENCE, "notice_period"),
    VaultFieldSpec("salary_prefs", "Salary preferences", FieldTier.PREFERENCE, "salary_prefs"),
    VaultFieldSpec(
        "work_authorization",
        "Work authorization",
        FieldTier.SENSITIVE,
        sensitive_key="work_authorization",
    ),
    VaultFieldSpec(
        "sponsorship_needed",
        "Sponsorship needed",
        FieldTier.SENSITIVE,
        sensitive_key="sponsorship_needed",
    ),
    VaultFieldSpec(
        "disability",
        "Disability status",
        FieldTier.SENSITIVE,
        sensitive_key="disability",
    ),
    VaultFieldSpec(
        "veteran_status",
        "Veteran status",
        FieldTier.SENSITIVE,
        sensitive_key="veteran_status",
    ),
    VaultFieldSpec(
        "race_ethnicity",
        "Race / ethnicity",
        FieldTier.SENSITIVE,
        sensitive_key="race_ethnicity",
    ),
    VaultFieldSpec("gender", "Gender", FieldTier.SENSITIVE, sensitive_key="gender"),
    VaultFieldSpec(
        "legal_authorization",
        "Legal authorization attestation",
        FieldTier.SENSITIVE,
        sensitive_key="legal_authorization",
    ),
)

FIELD_BY_KEY: dict[str, VaultFieldSpec] = {field.key: field for field in VAULT_FIELDS}

DEFAULT_COMMON_ANSWERS: tuple[tuple[str, str], ...] = (
    ("why_this_company", "Why do you want to work here?"),
    ("about_yourself", "Tell us about yourself"),
    ("proudest_accomplishment", "Proudest accomplishment"),
)
