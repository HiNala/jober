from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.resume_asset import ResumeAsset
from jober_api.models.user_profile import UserProfile
from jober_api.repositories.resume_asset import ResumeAssetRepository
from jober_api.services.claims_index import build_claims_index
from jober_api.services.embedding_gateway import maybe_create_resume_embedding
from jober_api.services.resume_parser import extract_resume_text, parse_skills_index
from jober_api.storage.keys import resume_key
from jober_api.storage.minio_client import ObjectStorage
from jober_api.vault.completeness import compute_completeness_score

CONTENT_TYPES = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def _content_type(filename: str) -> str:
    lower = filename.lower()
    for ext, mime in CONTENT_TYPES.items():
        if lower.endswith(ext):
            return mime
    return "application/octet-stream"


async def upload_resume(
    session: AsyncSession,
    storage: ObjectStorage,
    profile: UserProfile,
    *,
    filename: str,
    data: bytes,
    set_active: bool = True,
) -> ResumeAsset:
    if not filename.lower().endswith((".pdf", ".docx")):
        msg = "Only PDF and DOCX resumes are supported"
        raise ValueError(msg)

    asset_id = uuid.uuid4()
    key = resume_key(asset_id, filename)
    await storage.put_object(key, data, content_type=_content_type(filename))

    text = extract_resume_text(data, filename)
    skills_index: dict[str, Any] = parse_skills_index(text)
    skills_index["claims_index"] = build_claims_index(text, skills_index)

    repo = ResumeAssetRepository(session, profile.tenant_id)
    asset = await repo.create(
        id=asset_id,
        tenant_id=profile.tenant_id,
        object_key=key,
        original_filename=filename,
        extracted_text=text,
        skills_index=skills_index,
        is_active=set_active,
    )

    if set_active:
        await repo.deactivate_except(asset.id)
        profile.default_resume_asset_id = asset.id

    asset.embedding_id = await maybe_create_resume_embedding(asset.id, text)

    active = await repo.get_active()
    profile.profile_completeness_score = compute_completeness_score(profile, active)

    await session.flush()
    await session.refresh(asset)
    return asset
