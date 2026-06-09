from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.enums import RunStatus
from jober_api.repositories.form_field_observation import FormFieldObservationRepository
from jober_api.services.documents.cover_letter_generator import generate_cover_letter
from jober_api.services.documents.generation_prefs import (
    load_letter_defaults,
    merge_run_letter_options,
)
from jober_api.storage.minio_client import ObjectStorage


def form_has_cover_letter_field(observations: list[Any]) -> bool:
    return any(getattr(row, "field_key", None) == "cover_letter_upload" for row in observations)


async def should_generate_for_run(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID | None,
    batch_filters: dict[str, Any] | None,
    run_checkpoint: dict[str, Any] | None,
    job_target_id: uuid.UUID,
    observations_attempt_id: uuid.UUID | None = None,
) -> tuple[bool, dict[str, Any]]:
    defaults = await load_letter_defaults(session, tenant_id=tenant_id, user_id=user_id)
    options = merge_run_letter_options(
        defaults,
        batch_filters=batch_filters,
        run_checkpoint=run_checkpoint,
    )
    if not options.get("generate_cover_letter", True):
        return False, options

    if observations_attempt_id is not None:
        obs_repo = FormFieldObservationRepository(session)
        rows = await obs_repo.list_for_attempt(observations_attempt_id)
        if rows and not form_has_cover_letter_field(rows):
            return False, options
    return True, options


async def generate_documents_for_run(
    session: AsyncSession,
    storage: ObjectStorage,
    *,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    job_target_id: uuid.UUID,
    run_id: uuid.UUID,
    options: dict[str, Any],
    force: bool = False,
) -> dict[str, Any] | None:
    result = await generate_cover_letter(
        session,
        storage,
        tenant_id=tenant_id,
        user_id=user_id,
        job_target_id=job_target_id,
        run_id=run_id,
        force=force,
        template_style=str(options.get("template_style") or "classic"),
        voice_preset=str(options.get("voice_preset") or "direct"),
    )
    return result


def document_step_status() -> RunStatus:
    return RunStatus.GENERATE_DOCUMENTS
