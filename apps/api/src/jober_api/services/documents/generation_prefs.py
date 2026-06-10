from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.user import User
from jober_api.repositories.user_preferences import UserPreferencesRepository
from jober_api.services.documents.letter_styles import (
    DEFAULT_LETTER_TEMPLATE,
    DEFAULT_VOICE_PRESET,
    normalize_template,
    normalize_voice_preset,
)
from jober_api.services.preferences.defaults import merged_preferences


async def resolve_user_id_for_tenant(
    session: AsyncSession,
    tenant_id: uuid.UUID,
) -> uuid.UUID | None:
    stmt = (
        select(User.id).where(User.tenant_id == tenant_id).order_by(User.created_at.asc()).limit(1)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def load_letter_defaults(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID | None,
) -> dict[str, Any]:
    uid = user_id or await resolve_user_id_for_tenant(session, tenant_id)
    if uid is None:
        return {
            "generate_cover_letter": True,
            "template_style": DEFAULT_LETTER_TEMPLATE,
            "voice_preset": DEFAULT_VOICE_PRESET,
        }
    repo = UserPreferencesRepository(session)
    row = await repo.get_or_create(uid)
    prefs = merged_preferences(row.prefs)
    app = prefs.get("application_defaults") or {}
    return {
        "generate_cover_letter": bool(app.get("generate_cover_letter_per_run", True)),
        "template_style": normalize_template(app.get("letter_template")),
        "voice_preset": normalize_voice_preset(app.get("voice_preset")),
    }


def merge_run_letter_options(
    defaults: dict[str, Any],
    *,
    batch_filters: dict[str, Any] | None = None,
    run_checkpoint: dict[str, Any] | None = None,
) -> dict[str, Any]:
    merged = dict(defaults)
    if batch_filters:
        if "generate_cover_letter" in batch_filters:
            merged["generate_cover_letter"] = bool(batch_filters["generate_cover_letter"])
        if batch_filters.get("letter_template"):
            merged["template_style"] = normalize_template(str(batch_filters["letter_template"]))
        if batch_filters.get("voice_preset"):
            merged["voice_preset"] = normalize_voice_preset(str(batch_filters["voice_preset"]))
    checkpoint = run_checkpoint or {}
    if "generate_cover_letter" in checkpoint:
        merged["generate_cover_letter"] = bool(checkpoint["generate_cover_letter"])
    if checkpoint.get("letter_template"):
        merged["template_style"] = normalize_template(str(checkpoint["letter_template"]))
    if checkpoint.get("voice_preset"):
        merged["voice_preset"] = normalize_voice_preset(str(checkpoint["voice_preset"]))
    return merged
