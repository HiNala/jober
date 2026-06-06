from __future__ import annotations

from dataclasses import dataclass

from jober_api.models.resume_asset import ResumeAsset
from jober_api.models.user_profile import UserProfile
from jober_api.vault.field_registry import FIELD_BY_KEY, FieldTier
from jober_api.vault.sensitive_store import get_consent_flags, load_sensitive_answers


@dataclass(frozen=True)
class ChecklistItem:
    key: str
    label: str
    tier: str
    filled: bool
    required: bool


def _is_filled(profile: UserProfile, key: str, active_resume: ResumeAsset | None) -> bool:
    if key == "resume":
        return active_resume is not None and bool(active_resume.extracted_text)
    if key == "skills":
        return active_resume is not None and bool((active_resume.skills_index or {}).get("skills"))
    spec = FIELD_BY_KEY.get(key)
    if spec is None:
        return False
    if spec.tier == FieldTier.SENSITIVE:
        answers = load_sensitive_answers(profile)
        sensitive_key = spec.sensitive_key or spec.key
        return bool(answers.get(sensitive_key))
    attr = spec.profile_attr
    if not attr:
        return False
    value = getattr(profile, attr, None)
    if value is None:
        return False
    return not (isinstance(value, (dict, list, str)) and not value)


def build_checklist(
    profile: UserProfile,
    active_resume: ResumeAsset | None,
) -> list[ChecklistItem]:
    items: list[ChecklistItem] = [
        ChecklistItem(
            "resume",
            "Canonical resume uploaded",
            "public",
            _is_filled(profile, "resume", active_resume),
            True,
        ),
        ChecklistItem(
            "skills",
            "Skills index parsed",
            "public",
            _is_filled(profile, "skills", active_resume),
            True,
        ),
    ]
    for key, spec in FIELD_BY_KEY.items():
        required = spec.tier == FieldTier.PUBLIC and key in {"name", "email"}
        items.append(
            ChecklistItem(
                key=key,
                label=spec.label,
                tier=spec.tier.value,
                filled=_is_filled(profile, key, active_resume),
                required=required,
            )
        )
    return items


def compute_completeness_score(
    profile: UserProfile,
    active_resume: ResumeAsset | None,
) -> float:
    checklist = build_checklist(profile, active_resume)
    earned = 0.0
    possible = 0.0
    for item in checklist:
        weight = 2.0 if item.required else 1.0
        if item.tier == "sensitive":
            consent = get_consent_flags(profile, item.key)
            if consent["never_autofill"]:
                weight *= 0.25
        possible += weight
        if item.filled:
            earned += weight
    if possible == 0:
        return 0.0
    return round(min(1.0, earned / possible), 3)
