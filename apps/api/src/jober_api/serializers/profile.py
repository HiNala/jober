from __future__ import annotations

from typing import Any

from jober_api.models.profile_common_answer import ProfileCommonAnswer
from jober_api.models.resume_asset import ResumeAsset
from jober_api.models.user_profile import UserProfile
from jober_api.vault.completeness import ChecklistItem, build_checklist, compute_completeness_score
from jober_api.vault.field_registry import FIELD_BY_KEY, FieldTier
from jober_api.vault.sensitive_store import get_consent_flags, load_sensitive_answers


def serialize_resume(asset: ResumeAsset) -> dict[str, Any]:
    skills = []
    if asset.skills_index and isinstance(asset.skills_index.get("skills"), list):
        skills = asset.skills_index["skills"]
    return {
        "id": str(asset.id),
        "created_at": asset.created_at.isoformat(),
        "updated_at": asset.updated_at.isoformat(),
        "original_filename": asset.original_filename,
        "is_active": asset.is_active,
        "embedding_id": asset.embedding_id,
        "skills": skills,
        "extracted_text_preview": (asset.extracted_text or "")[:400],
        "has_text": bool(asset.extracted_text),
    }


def serialize_checklist(items: list[ChecklistItem]) -> list[dict[str, Any]]:
    return [
        {
            "key": item.key,
            "label": item.label,
            "tier": item.tier,
            "filled": item.filled,
            "required": item.required,
        }
        for item in items
    ]


def serialize_profile(
    profile: UserProfile,
    *,
    active_resume: ResumeAsset | None,
    include_sensitive: bool = False,
) -> dict[str, Any]:
    checklist = build_checklist(profile, active_resume)
    score = compute_completeness_score(profile, active_resume)
    fields_meta: list[dict[str, Any]] = []
    for key, spec in FIELD_BY_KEY.items():
        consent = get_consent_flags(profile, key)
        entry: dict[str, Any] = {
            "key": key,
            "label": spec.label,
            "tier": spec.tier.value,
            "consent": consent,
        }
        if spec.tier == FieldTier.SENSITIVE:
            if include_sensitive:
                answers = load_sensitive_answers(profile)
                sensitive_key = spec.sensitive_key or key
                entry["value"] = answers.get(sensitive_key)
            else:
                answers = load_sensitive_answers(profile)
                sensitive_key = spec.sensitive_key or key
                entry["has_value"] = bool(answers.get(sensitive_key))
        elif spec.profile_attr:
            entry["value"] = getattr(profile, spec.profile_attr, None)
        fields_meta.append(entry)

    payload: dict[str, Any] = {
        "id": str(profile.id),
        "created_at": profile.created_at.isoformat(),
        "updated_at": profile.updated_at.isoformat(),
        "name": profile.name,
        "email": profile.email,
        "phone": profile.phone,
        "location": profile.location,
        "current_title": profile.current_title,
        "notice_period": profile.notice_period,
        "links": profile.links,
        "relocation_pref": profile.relocation_pref,
        "onsite_pref": profile.onsite_pref,
        "hybrid_pref": profile.hybrid_pref,
        "salary_prefs": profile.salary_prefs,
        "default_resume_asset_id": (
            str(profile.default_resume_asset_id) if profile.default_resume_asset_id else None
        ),
        "profile_completeness_score": score,
        "checklist": serialize_checklist(checklist),
        "fields": fields_meta,
        "has_sensitive_eeo": bool(profile.sensitive_eeo_answers),
        "active_resume": serialize_resume(active_resume) if active_resume else None,
    }
    return payload


def serialize_common_answer(row: ProfileCommonAnswer) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "answer_key": row.answer_key,
        "label": row.label,
        "body": row.body,
        "updated_at": row.updated_at.isoformat(),
    }
