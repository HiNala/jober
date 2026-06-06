from __future__ import annotations

import uuid

from jober_api.config import settings


async def maybe_create_resume_embedding(resume_asset_id: uuid.UUID, text: str) -> str | None:
    """Optional embedding hook for semantic keyword matching (LLM gateway stub)."""
    if not settings.llm_api_key or not text.strip():
        return None
    # Provider integration lands with the LiteLLM gateway; store a stable reference now.
    return f"resume-embed:{resume_asset_id}"
