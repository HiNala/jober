from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.db.session import get_session
from jober_api.repositories.profile_common_answer import ProfileCommonAnswerRepository
from jober_api.repositories.resume_asset import ResumeAssetRepository
from jober_api.repositories.user_profile import UserProfileRepository
from jober_api.serializers.profile import serialize_common_answer, serialize_profile
from jober_api.vault.completeness import compute_completeness_score
from jober_api.vault.field_registry import DEFAULT_COMMON_ANSWERS, SENSITIVE_EEO_KEYS
from jober_api.vault.sensitive_store import merge_sensitive_answers

router = APIRouter(prefix="/profile", tags=["profile"])

_PUBLIC_PATCH_KEYS = {
    "name",
    "email",
    "phone",
    "location",
    "current_title",
    "notice_period",
    "links",
}
_PREFERENCE_PATCH_KEYS = {
    "relocation_pref",
    "onsite_pref",
    "hybrid_pref",
    "salary_prefs",
}


async def _load_profile_context(session: AsyncSession) -> tuple[Any, Any, Any]:
    profiles = UserProfileRepository(session)
    resumes = ResumeAssetRepository(session)
    profile = await profiles.get_or_create_singleton()
    active = await resumes.get_active()
    return profiles, profile, active


@router.get("")
async def get_profile(session: AsyncSession = Depends(get_session)) -> dict[str, object]:
    _profiles, profile, active = await _load_profile_context(session)
    await _ensure_default_answers(session, profile.id)
    return serialize_profile(profile, active_resume=active, include_sensitive=True)


@router.patch("")
async def patch_profile(
    body: dict[str, object],
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    profiles, profile, active = await _load_profile_context(session)
    allowed = _PUBLIC_PATCH_KEYS | _PREFERENCE_PATCH_KEYS
    updates = {k: v for k, v in body.items() if k in allowed}
    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid fields")
    await profiles.update_fields(profile, **updates)
    profile.profile_completeness_score = compute_completeness_score(profile, active)
    await session.commit()
    await session.refresh(profile)
    return serialize_profile(profile, active_resume=active, include_sensitive=True)


@router.patch("/vault")
async def patch_vault(
    body: dict[str, object],
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    profiles, profile, active = await _load_profile_context(session)
    sensitive_updates: dict[str, str | None] = {}
    for key in SENSITIVE_EEO_KEYS:
        if key in body:
            raw = body[key]
            sensitive_updates[key] = str(raw) if raw is not None else None

    consent_updates = body.get("field_consent")
    if isinstance(consent_updates, dict):
        merged = dict(profile.field_consent or {})
        now = datetime.now(UTC).isoformat()
        for field_key, flags in consent_updates.items():
            if not isinstance(flags, dict):
                continue
            entry = dict(merged.get(field_key, {}))
            if "consent" in flags:
                entry["consent"] = bool(flags["consent"])
                if entry["consent"]:
                    entry["consented_at"] = now
            if "never_autofill" in flags:
                entry["never_autofill"] = bool(flags["never_autofill"])
            merged[field_key] = entry
        profile.field_consent = merged

    if sensitive_updates:
        merge_sensitive_answers(profile, sensitive_updates)

    profile.profile_completeness_score = compute_completeness_score(profile, active)
    await session.commit()
    await session.refresh(profile)
    return serialize_profile(profile, active_resume=active, include_sensitive=True)


@router.get("/common-answers")
async def list_common_answers(
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    profiles, profile, _active = await _load_profile_context(session)
    await _ensure_default_answers(session, profile.id)
    repo = ProfileCommonAnswerRepository(session)
    rows = await repo.list_for_profile(profile.id)
    return {"items": [serialize_common_answer(row) for row in rows]}


@router.put("/common-answers/{answer_key}")
async def upsert_common_answer(
    answer_key: str,
    body: dict[str, object],
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    _profiles, profile, _active = await _load_profile_context(session)
    label = str(body.get("label") or answer_key.replace("_", " ").title())
    text = body.get("body")
    if not isinstance(text, str) or not text.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="body is required")
    repo = ProfileCommonAnswerRepository(session)
    row = await repo.upsert(profile.id, answer_key, label=label, body=text.strip())
    await session.commit()
    return serialize_common_answer(row)


async def _ensure_default_answers(session: AsyncSession, profile_id: Any) -> None:
    repo = ProfileCommonAnswerRepository(session)
    existing = await repo.list_for_profile(profile_id)
    if existing:
        return
    for key, label in DEFAULT_COMMON_ANSWERS:
        await repo.upsert(profile_id, key, label=label, body="")
    await session.flush()
