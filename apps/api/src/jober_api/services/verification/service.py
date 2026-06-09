from __future__ import annotations

import asyncio
import uuid
from datetime import UTC, datetime
from typing import Any

from jober_schemas.enums import JobTargetStatus, RunPolicy, RunStatus
from jober_verify.summary import build_human_summary
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.application_attempt import ApplicationAttempt
from jober_api.models.application_run import ApplicationRun
from jober_api.models.enums import AttemptStatus, CheckpointStatus, CheckpointType, DocumentType
from jober_api.models.generated_document import GeneratedDocument
from jober_api.models.human_checkpoint import HumanCheckpoint
from jober_api.repositories.application_run import ApplicationRunRepository
from jober_api.repositories.form_field_observation import FormFieldObservationRepository
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.repositories.user_profile import UserProfileRepository
from jober_api.services.form_discovery.service import _serialize_observation
from jober_api.vault.field_registry import FIELD_BY_KEY, FieldTier
from jober_api.vault.fill_policy import resolve_field_fill


class VerifyBlockedError(Exception):
    def __init__(self, *, reason: str, run_id: uuid.UUID, readiness: dict[str, Any]) -> None:
        self.reason = reason
        self.run_id = run_id
        self.readiness = readiness
        super().__init__(reason)


class SubmitPolicyError(Exception):
    pass


async def _load_observation_payloads(
    session: AsyncSession,
    job_target_id: uuid.UUID,
    observations_attempt_id: uuid.UUID | None,
) -> tuple[list[dict[str, Any]], uuid.UUID]:
    obs_repo = FormFieldObservationRepository(session)
    if observations_attempt_id:
        rows = await obs_repo.list_for_attempt(observations_attempt_id)
        attempt_id = observations_attempt_id
    else:
        rows = await obs_repo.list_for_job_latest(job_target_id)
        attempt_id = rows[0].attempt_id if rows else uuid.UUID(int=0)
    if not rows:
        msg = "No field observations — run discover-form first"
        raise ValueError(msg)

    payloads: list[dict[str, Any]] = []
    for row in rows:
        spec = FIELD_BY_KEY.get(row.mapped_profile_field or "")
        payloads.append(
            {
                "field_key": row.field_key,
                "label": row.label,
                "field_type": row.field_type,
                "mapped_profile_field": row.mapped_profile_field,
                "status": row.status.value,
                "is_sensitive": spec is not None and spec.tier == FieldTier.SENSITIVE,
            }
        )
    return payloads, attempt_id


async def _latest_fill_run(
    session: AsyncSession,
    job_target_id: uuid.UUID,
) -> ApplicationRun | None:
    stmt = (
        select(ApplicationRun)
        .where(
            ApplicationRun.job_target_id == job_target_id,
            ApplicationRun.status == RunStatus.FILL_FORM,
        )
        .order_by(ApplicationRun.created_at.desc())
        .limit(1)
    )
    return (await session.execute(stmt)).scalar_one_or_none()


async def _profile_values_for_observations(
    session: AsyncSession,
    observations: list[dict[str, Any]],
) -> dict[str, Any]:
    profiles = UserProfileRepository(session)
    profile = await profiles.get_singleton()
    values: dict[str, Any] = {}
    if not profile:
        return values
    for row in observations:
        mapped = row.get("mapped_profile_field")
        if not mapped or mapped in ("resume_upload", "cover_letter_upload"):
            continue
        resolution = resolve_field_fill(profile, str(mapped))
        if resolution.outcome.value == "value":
            values[str(mapped)] = resolution.value
    return values


async def verify_ready_from_fixture(
    session: AsyncSession,
    *,
    job_target_id: uuid.UUID,
    fixture_html: str,
    run_id: uuid.UUID | None = None,
    policy: RunPolicy = RunPolicy.REVIEW_BEFORE_SUBMIT,
    auto_submit_after_verify: bool = False,
    refilled: bool = True,
) -> dict[str, Any]:
    jobs = JobTargetRepository(session)
    job = await jobs.get(job_target_id)
    if job is None:
        msg = "Job target not found"
        raise ValueError(msg)

    runs = ApplicationRunRepository(session)
    if run_id:
        run = await runs.get(run_id)
        if run is None or run.job_target_id != job_target_id:
            msg = "Run not found for job target"
            raise ValueError(msg)
        attempt_stmt = (
            select(ApplicationAttempt)
            .where(ApplicationAttempt.run_id == run.id)
            .order_by(ApplicationAttempt.attempt_index.desc())
            .limit(1)
        )
        attempt = (await session.execute(attempt_stmt)).scalar_one_or_none()
        if attempt is None:
            msg = "Run has no attempts"
            raise ValueError(msg)
    else:
        now = datetime.now(UTC)
        run = await _latest_fill_run(session, job_target_id)
        if run is not None:
            await runs.update_fields(
                run.id,
                status=RunStatus.VERIFY_READY,
                current_step=RunStatus.VERIFY_READY,
                policy=policy,
            )
            attempt_stmt = (
                select(ApplicationAttempt)
                .where(ApplicationAttempt.run_id == run.id)
                .order_by(ApplicationAttempt.attempt_index.desc())
                .limit(1)
            )
            attempt = (await session.execute(attempt_stmt)).scalar_one_or_none()
            if attempt is None:
                msg = "Fill run has no attempts"
                raise ValueError(msg)
        else:
            run = await runs.create(
                job_target_id=job_target_id,
                status=RunStatus.VERIFY_READY,
                current_step=RunStatus.VERIFY_READY,
                policy=policy,
                started_at=now,
            )
            attempt = ApplicationAttempt(
                run_id=run.id,
                attempt_index=1,
                status=AttemptStatus.RUNNING,
                strategy_name="fixture_verify_ready",
                started_at=now,
            )
            session.add(attempt)
            await session.flush()
            await session.refresh(attempt)

    observations, _ = await _load_observation_payloads(session, job_target_id, None)
    profile_values = await _profile_values_for_observations(session, observations)

    verify_run_id = run.id
    verify_attempt_id = attempt.id
    await session.commit()

    from jober_worker.verify_runner import persist_verify_result, run_fixture_verify_readiness

    result = await asyncio.to_thread(
        run_fixture_verify_readiness,
        run_id=verify_run_id,
        attempt_id=verify_attempt_id,
        fixture_html=fixture_html,
        observations=observations,
        profile_values=profile_values,
        refilled=refilled,
        require_uploads=False,
    )

    if result.get("status") == "already_applied":
        summary = build_human_summary(
            company=job.company,
            role=job.role,
            observations=observations,
            readiness_passed=False,
        )
        await asyncio.to_thread(
            persist_verify_result,
            run_id=verify_run_id,
            attempt_id=verify_attempt_id,
            passed=False,
            readiness=result.get("readiness", {}),
            artifact_keys=result.get("artifact_keys", {}),
            human_summary=summary,
            already_applied=True,
        )
        return {
            "run_id": str(verify_run_id),
            "status": RunStatus.SKIPPED.value,
            "readiness": result.get("readiness", {}),
            "human_summary": summary,
            "gate": "already_applied",
        }

    readiness = result.get("readiness", {})
    passed = bool(readiness.get("passed"))
    obs_repo = FormFieldObservationRepository(session)
    rows = await obs_repo.list_for_job_latest(job_target_id)
    serialized = [_serialize_observation(r).model_dump() for r in rows]
    summary = build_human_summary(
        company=job.company,
        role=job.role,
        observations=serialized,
        readiness_passed=passed,
    )

    await asyncio.to_thread(
        persist_verify_result,
        run_id=verify_run_id,
        attempt_id=verify_attempt_id,
        passed=passed,
        readiness=readiness,
        artifact_keys=result.get("artifact_keys", {}),
        human_summary=summary,
    )

    if not passed:
        raise VerifyBlockedError(
            reason="readiness_failed",
            run_id=verify_run_id,
            readiness=readiness,
        )

    if auto_submit_after_verify and policy == RunPolicy.AUTO_SUBMIT:
        submit_result = await submit_application(
            session,
            run_id=verify_run_id,
            fixture_html=fixture_html,
            human_approved=True,
        )
        return {
            "run_id": str(verify_run_id),
            "status": submit_result.get("run_status", RunStatus.SUCCEEDED.value),
            "readiness": readiness,
            "human_summary": summary,
            "auto_submitted": True,
            "submit": submit_result,
        }

    return {
        "run_id": str(verify_run_id),
        "status": RunStatus.REVIEW_AND_SUBMIT.value,
        "readiness": readiness,
        "human_summary": summary,
    }


async def get_review_package_for_job(
    session: AsyncSession,
    job_target_id: uuid.UUID,
) -> dict[str, Any] | None:
    stmt = (
        select(ApplicationRun)
        .where(
            ApplicationRun.job_target_id == job_target_id,
            ApplicationRun.status == RunStatus.REVIEW_AND_SUBMIT,
        )
        .order_by(ApplicationRun.created_at.desc())
        .limit(1)
    )
    run = (await session.execute(stmt)).scalar_one_or_none()
    if run is None:
        return None
    return await get_review_package(session, run.id)


async def get_review_package(session: AsyncSession, run_id: uuid.UUID) -> dict[str, Any]:
    runs = ApplicationRunRepository(session)
    run = await runs.get(run_id)
    if run is None:
        msg = "Run not found"
        raise ValueError(msg)

    jobs = JobTargetRepository(session)
    job = await jobs.get(run.job_target_id)
    if job is None:
        msg = "Job target not found"
        raise ValueError(msg)

    cp_stmt = (
        select(HumanCheckpoint)
        .where(
            HumanCheckpoint.run_id == run_id,
            HumanCheckpoint.checkpoint_type == CheckpointType.REVIEW_SUBMIT,
            HumanCheckpoint.status == CheckpointStatus.OPEN,
        )
        .order_by(HumanCheckpoint.created_at.desc())
        .limit(1)
    )
    checkpoint = (await session.execute(cp_stmt)).scalar_one_or_none()

    readiness: dict[str, Any] = {"passed": False, "checks": []}
    human_summary = ""
    if checkpoint and checkpoint.options:
        readiness = checkpoint.options.get("readiness", readiness)
        human_summary = str(checkpoint.options.get("human_summary", ""))

    obs_repo = FormFieldObservationRepository(session)
    rows = await obs_repo.list_for_job_latest(run.job_target_id)
    fill_diffs: list[dict[str, Any]] = []
    for row in rows:
        evidence = row.evidence or {}
        diff = evidence.get("fill_diff")
        if diff:
            fill_diffs.append(
                {
                    "field_key": row.field_key,
                    "label": row.label,
                    **diff,
                }
            )

    attempt_stmt = (
        select(ApplicationAttempt)
        .where(ApplicationAttempt.run_id == run_id)
        .order_by(ApplicationAttempt.attempt_index.desc())
        .limit(1)
    )
    attempt = (await session.execute(attempt_stmt)).scalar_one_or_none()
    screenshot_key = attempt.final_screenshot_object_key if attempt else None

    doc_stmt = (
        select(GeneratedDocument)
        .where(
            GeneratedDocument.job_target_id == run.job_target_id,
            GeneratedDocument.document_type == DocumentType.COVER_LETTER,
        )
        .order_by(GeneratedDocument.created_at.desc())
        .limit(1)
    )
    cover_doc = (await session.execute(doc_stmt)).scalar_one_or_none()

    return {
        "run_id": str(run.id),
        "job_target_id": str(run.job_target_id),
        "company": job.company,
        "role": job.role,
        "status": run.status.value,
        "human_summary": human_summary,
        "readiness": readiness,
        "fill_diffs": fill_diffs,
        "screenshot_object_key": screenshot_key,
        "resume_filename": "resume.pdf",
        "cover_letter_preview": (cover_doc.text[:500] if cover_doc and cover_doc.text else None),
        "cover_letter": (
            {
                "id": str(cover_doc.id),
                "text": cover_doc.text,
                "ats_score": cover_doc.ats_score,
                "keyword_coverage": cover_doc.keyword_coverage,
                "template_style": (cover_doc.keyword_coverage or {}).get("template_style"),
                "voice_preset": (cover_doc.keyword_coverage or {}).get("voice_preset"),
                "locked_paragraphs": (cover_doc.keyword_coverage or {}).get("locked_paragraphs")
                or [],
                "pdf_download_path": f"/api/documents/{cover_doc.id}/download/pdf",
            }
            if cover_doc and cover_doc.text
            else None
        ),
        "checkpoint_id": str(checkpoint.id) if checkpoint else None,
        "policy": run.policy.value,
    }


async def submit_application(
    session: AsyncSession,
    *,
    run_id: uuid.UUID,
    fixture_html: str | None = None,
    human_approved: bool = True,
) -> dict[str, Any]:
    runs = ApplicationRunRepository(session)
    run = await runs.get(run_id)
    if run is None:
        msg = "Run not found"
        raise ValueError(msg)

    if run.policy == RunPolicy.DRY_RUN and not fixture_html:
        msg = "Dry-run policy cannot submit without fixture_html"
        raise SubmitPolicyError(msg)

    if run.policy == RunPolicy.REVIEW_BEFORE_SUBMIT and not human_approved:
        msg = "Human approval required before submit"
        raise SubmitPolicyError(msg)

    if run.status not in (
        RunStatus.REVIEW_AND_SUBMIT,
        RunStatus.VERIFY_READY,
        RunStatus.FILL_FORM,
    ):
        msg = f"Run not ready for submit (status={run.status.value})"
        raise ValueError(msg)

    prior = await runs.list_for_job(run.job_target_id)
    attempt_stmt = (
        select(ApplicationAttempt)
        .where(ApplicationAttempt.run_id == run_id)
        .order_by(ApplicationAttempt.attempt_index.desc())
        .limit(1)
    )
    attempt = (await session.execute(attempt_stmt)).scalar_one_or_none()
    if attempt is None:
        msg = "Run has no attempts"
        raise ValueError(msg)

    if not fixture_html:
        msg = (
            "fixture_html is required for fixture submit replay. "
            "Live browser submit will use the worker queue in a later mission."
        )
        raise ValueError(msg)

    submit_run_id = run.id
    submit_attempt_id = attempt.id
    job_target_id = run.job_target_id
    await session.commit()

    from jober_worker.submit_runner import persist_submit_result, run_fixture_submit

    verification = await asyncio.to_thread(
        run_fixture_submit,
        run_id=submit_run_id,
        attempt_id=submit_attempt_id,
        job_target_id=job_target_id,
        fixture_html=fixture_html,
    )
    await asyncio.to_thread(
        persist_submit_result,
        run_id=submit_run_id,
        job_target_id=job_target_id,
        verification=verification,
        prior_runs=prior,
    )

    from jober_api.services.analytics.collector import emit_server_event
    from jober_api.services.analytics.rollups import server_session_id

    await emit_server_event(
        session,
        name="submit.complete",
        session_id=server_session_id(run_id=submit_run_id),
        tenant_id=run.tenant_id,
        props={"run_id": str(submit_run_id)},
    )
    await session.commit()

    outcome = verification.get("outcome")
    run_status_by_outcome = {
        "success": RunStatus.SUCCEEDED.value,
        "already_applied": RunStatus.SKIPPED.value,
        "uncertain": RunStatus.VERIFY_SUBMISSION.value,
        "failed": RunStatus.NEEDS_HUMAN.value,
    }
    job_status_by_outcome = {
        "success": JobTargetStatus.APPLIED.value,
        "already_applied": JobTargetStatus.APPLIED.value,
        "uncertain": JobTargetStatus.IN_PROGRESS.value,
        "failed": JobTargetStatus.IN_PROGRESS.value,
    }

    return {
        "run_id": str(submit_run_id),
        "outcome": outcome,
        "confirmation_text": verification.get("confirmation_text"),
        "final_url": verification.get("final_url"),
        "note": verification.get("note"),
        "run_status": run_status_by_outcome.get(str(outcome), RunStatus.NEEDS_HUMAN.value),
        "job_target_status": job_status_by_outcome.get(
            str(outcome), JobTargetStatus.IN_PROGRESS.value
        ),
    }


async def skip_submit(session: AsyncSession, run_id: uuid.UUID) -> dict[str, Any]:
    runs = ApplicationRunRepository(session)
    run = await runs.get(run_id)
    if run is None:
        msg = "Run not found"
        raise ValueError(msg)

    now = datetime.now(UTC)
    await runs.update_fields(
        run_id,
        status=RunStatus.SKIPPED,
        current_step=RunStatus.SKIPPED,
        completed_at=now,
        human_review_required_reason="submit_skipped_by_user",
    )
    cp_stmt = select(HumanCheckpoint).where(
        HumanCheckpoint.run_id == run_id,
        HumanCheckpoint.checkpoint_type == CheckpointType.REVIEW_SUBMIT,
        HumanCheckpoint.status == CheckpointStatus.OPEN,
    )
    for cp in (await session.execute(cp_stmt)).scalars():
        cp.status = CheckpointStatus.DISMISSED
        cp.resolved_at = now

    return {"run_id": str(run_id), "status": RunStatus.SKIPPED.value}
