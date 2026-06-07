from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from jober_forms.mapper import FieldMapping, map_discovered_field
from jober_forms.policy import apply_confidence_policy
from jober_forms.scanner import detect_steps, scan_multistep_form
from jober_schemas.form_field import FormDiscoveryRead, FormFieldObservationRead
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.application_attempt import ApplicationAttempt
from jober_api.models.enums import AttemptStatus, FieldObservationStatus, RunPolicy, RunStatus
from jober_api.models.form_field_observation import FormFieldObservation
from jober_api.repositories.application_run import ApplicationRunRepository
from jober_api.repositories.field_mapping_memory import FieldMappingMemoryRepository
from jober_api.repositories.form_field_observation import FormFieldObservationRepository
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.repositories.user_profile import UserProfileRepository
from jober_api.vault.field_registry import FIELD_BY_KEY, FieldTier
from jober_api.vault.fill_policy import resolve_field_fill


def _serialize_observation(row: FormFieldObservation) -> FormFieldObservationRead:
    options = None
    if isinstance(row.options, dict):
        raw = row.options.get("items")
        if isinstance(raw, list):
            options = [str(x) for x in raw]
    elif isinstance(row.options, list):
        options = [str(x) for x in row.options]
    return FormFieldObservationRead(
        id=str(row.id),
        created_at=row.created_at.isoformat(),
        updated_at=row.updated_at.isoformat(),
        attempt_id=str(row.attempt_id),
        field_key=row.field_key,
        label=row.label,
        field_type=row.field_type,
        required=row.required,
        options=options,
        mapped_profile_field=row.mapped_profile_field,
        proposed_value_redacted=row.proposed_value_redacted,
        confidence=row.confidence,
        status=row.status,
        evidence=row.evidence,
    )


async def discover_from_fixture_html(
    session: AsyncSession,
    *,
    job_target_id: uuid.UUID,
    html: str,
    platform: str = "generic",
) -> FormDiscoveryRead:
    jobs = JobTargetRepository(session)
    job = await jobs.get(job_target_id)
    if job is None:
        msg = "Job target not found"
        raise ValueError(msg)

    profiles = UserProfileRepository(session)
    profile = await profiles.get_singleton()

    memory_repo = FieldMappingMemoryRepository(session)
    discovered = scan_multistep_form(html)
    steps = detect_steps(html)

    runs = ApplicationRunRepository(session)
    now = datetime.now(UTC)
    run = await runs.create(
        job_target_id=job_target_id,
        status=RunStatus.DISCOVER_FORM,
        current_step=RunStatus.DISCOVER_FORM,
        policy=RunPolicy.DRY_RUN,
        started_at=now,
    )
    attempt = ApplicationAttempt(
        run_id=run.id,
        attempt_index=1,
        status=AttemptStatus.RUNNING,
        platform_detected=platform,
        strategy_name="fixture_discover_form",
        started_at=now,
    )
    session.add(attempt)
    await session.flush()
    await session.refresh(attempt)

    observations: list[FormFieldObservation] = []
    for field in discovered:
        remembered = await memory_repo.lookup(platform, field.label or field.field_key)
        mapping = map_discovered_field(field, platform=platform)
        if remembered and mapping.confidence < 0.9:
            mapping = FieldMapping(
                mapped_profile_field=remembered,
                confidence=0.95,
                mapping_evidence=[*mapping.mapping_evidence, f"memory:{remembered}"],
                ambiguous=mapping.ambiguous,
            )

        mapped_key = mapping.mapped_profile_field
        spec = FIELD_BY_KEY.get(mapped_key) if mapped_key else None
        is_sensitive = spec is not None and spec.tier == FieldTier.SENSITIVE

        fill_outcome = "needs_human"
        fill_value = None
        if profile and mapped_key and mapped_key not in ("resume_upload", "cover_letter_upload"):
            resolution = resolve_field_fill(profile, mapped_key)
            fill_outcome = resolution.outcome.value
            fill_value = resolution.value

        draft = apply_confidence_policy(
            mapped_field=mapped_key,
            confidence=mapping.confidence,
            fill_outcome=fill_outcome,
            fill_value=fill_value,
            field_type=field.field_type,
            is_sensitive=is_sensitive,
            is_ambiguous=mapping.ambiguous,
            is_upload=field.is_upload,
        )

        evidence_payload: dict[str, Any] = {
            "label_sources": [{"source": e.source, "text": e.text} for e in field.evidence],
            "mapping": mapping.mapping_evidence,
            "step_index": field.step_index,
            **draft.evidence,
        }

        row = FormFieldObservation(
            attempt_id=attempt.id,
            field_key=field.field_key,
            label=field.label,
            field_type=field.field_type,
            required=field.required,
            options={"items": field.options} if field.options else None,
            mapped_profile_field=draft.mapped_profile_field,
            proposed_value_redacted=draft.proposed_value_redacted,
            confidence=draft.confidence,
            status=FieldObservationStatus(draft.status),
            evidence=evidence_payload,
        )
        session.add(row)
        observations.append(row)

    await session.flush()
    for row in observations:
        await session.refresh(row)

    attempt.status = AttemptStatus.SUCCEEDED
    attempt.completed_at = now
    await runs.update_fields(run.id, status=RunStatus.DISCOVER_FORM, completed_at=now)

    items = [_serialize_observation(row) for row in observations]
    return FormDiscoveryRead(
        run_id=str(run.id),
        attempt_id=str(attempt.id),
        platform=platform,
        step_count=len(steps),
        items=items,
    )


async def list_field_observations(
    session: AsyncSession,
    job_target_id: uuid.UUID,
) -> list[FormFieldObservationRead]:
    repo = FormFieldObservationRepository(session)
    rows = await repo.list_for_job_latest(job_target_id)
    return [_serialize_observation(row) for row in rows]


async def update_field_observation(
    session: AsyncSession,
    observation_id: uuid.UUID,
    *,
    mapped_profile_field: str | None = None,
    status: FieldObservationStatus | None = None,
    remember: bool = False,
    platform: str = "generic",
) -> FormFieldObservationRead:
    repo = FormFieldObservationRepository(session)
    row = await repo.get(observation_id)
    if row is None:
        msg = "Observation not found"
        raise ValueError(msg)

    if mapped_profile_field is not None:
        row.mapped_profile_field = mapped_profile_field
    if status is not None:
        row.status = status

    if remember and row.label and row.mapped_profile_field:
        memory = FieldMappingMemoryRepository(session)
        await memory.remember(platform, row.label, row.mapped_profile_field)

    await session.flush()
    await session.refresh(row)
    return _serialize_observation(row)
