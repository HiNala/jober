from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from typing import Any

from jober_extraction.a11y import extract_visible_text_from_html
from jober_extraction.gates import GateKind, detect_access_gates
from jober_extraction.intelligence import build_job_profile
from jober_extraction.platform import detect_platform
from jober_schemas.job_profile import JobExtractionRead, JobProfileRead, PlatformDetectionRead
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.enums import (
    CheckpointType,
    RunPolicy,
    RunStatus,
)
from jober_api.repositories.application_run import ApplicationRunRepository
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.repositories.resume_asset import ResumeAssetRepository


class ExtractionBlockedError(Exception):
    def __init__(self, gate: GateKind, run_id: uuid.UUID) -> None:
        self.gate = gate
        self.run_id = run_id
        super().__init__(f"Human checkpoint required: {gate.value}")


def _today() -> date:
    return datetime.now(UTC).date()


def _resume_skills(resume: Any) -> list[str]:
    if resume and resume.skills_index and isinstance(resume.skills_index.get("skills"), list):
        return [str(s) for s in resume.skills_index["skills"]]
    return []


def extract_from_page_content(
    *,
    url: str,
    html: str,
    visible_text: str,
    accessibility_tree: dict[str, Any] | list[Any] | None,
    company_hint: str,
    resume_skills: list[str] | None = None,
) -> tuple[PlatformDetectionRead, JobProfileRead]:
    platform = detect_platform(url, html)
    profile = build_job_profile(
        html=html,
        visible_text=visible_text,
        accessibility_tree=accessibility_tree,
        company_hint=company_hint,
        resume_skills=resume_skills,
    )
    return platform, profile


async def get_cached_extraction(
    session: AsyncSession,
    job_target_id: uuid.UUID,
) -> JobExtractionRead | None:
    jobs = JobTargetRepository(session)
    job = await jobs.get(job_target_id)
    if job is None or not job.extracted_job_profile or job.job_profile_cache_date != _today():
        return None
    platform = PlatformDetectionRead.model_validate(job.platform_detection or {})
    profile = JobProfileRead.model_validate(job.extracted_job_profile)
    return JobExtractionRead(
        id=str(job.id),
        job_target_id=str(job.id),
        created_at=job.created_at.isoformat(),
        updated_at=job.updated_at.isoformat(),
        platform_detection=platform,
        job_profile=profile,
        cached=True,
        extracted_at=job.job_profile_extracted_at.isoformat()
        if job.job_profile_extracted_at
        else None,
    )


async def persist_extraction(
    session: AsyncSession,
    *,
    job_target_id: uuid.UUID,
    platform: PlatformDetectionRead,
    profile: JobProfileRead,
    run_id: uuid.UUID | None = None,
) -> JobExtractionRead:
    jobs = JobTargetRepository(session)
    now = datetime.now(UTC)
    job = await jobs.update_fields(
        job_target_id,
        extracted_job_profile=profile.model_dump(),
        platform_detection=platform.model_dump(),
        job_profile_extracted_at=now,
        job_profile_cache_date=_today(),
    )
    if job is None:
        msg = "Job target not found"
        raise ValueError(msg)
    return JobExtractionRead(
        id=str(job.id),
        job_target_id=str(job.id),
        created_at=job.created_at.isoformat(),
        updated_at=job.updated_at.isoformat(),
        platform_detection=platform,
        job_profile=profile,
        cached=False,
        extracted_at=now.isoformat(),
        run_id=str(run_id) if run_id else None,
    )


async def extract_from_fixture_html(
    session: AsyncSession,
    *,
    job_target_id: uuid.UUID,
    url: str,
    html: str,
    force: bool = False,
) -> JobExtractionRead:
    if not force:
        cached = await get_cached_extraction(session, job_target_id)
        if cached is not None:
            return cached

    jobs = JobTargetRepository(session)
    job = await jobs.get(job_target_id)
    if job is None:
        msg = "Job target not found"
        raise ValueError(msg)

    resumes = ResumeAssetRepository(session)
    resume = await resumes.get_active()
    visible = extract_visible_text_from_html(html)
    gates = detect_access_gates(html, visible)
    runs = ApplicationRunRepository(session)

    run = await runs.create(
        job_target_id=job_target_id,
        status=RunStatus.EXTRACT_JOB,
        current_step=RunStatus.EXTRACT_JOB,
        policy=RunPolicy.DRY_RUN,
    )

    if gates:
        gate = gates[0]
        checkpoint_type = {
            GateKind.LOGIN: CheckpointType.LOGIN,
            GateKind.CAPTCHA: CheckpointType.CAPTCHA,
            GateKind.TWO_FACTOR: CheckpointType.TWO_FACTOR,
        }[gate]
        await runs.create_checkpoint(
            run.id,
            checkpoint_type=checkpoint_type,
            prompt=f"Resolve {gate.value} before extraction can continue.",
        )
        await runs.update_fields(
            run.id,
            status=RunStatus.NEEDS_HUMAN,
            human_review_required_reason=gate.value,
        )
        raise ExtractionBlockedError(gate, run.id)

    platform, profile = extract_from_page_content(
        url=url,
        html=html,
        visible_text=visible,
        accessibility_tree=None,
        company_hint=job.company,
        resume_skills=_resume_skills(resume),
    )
    await runs.update_fields(run.id, status=RunStatus.EXTRACT_JOB, final_url=url)
    result = await persist_extraction(
        session,
        job_target_id=job_target_id,
        platform=platform,
        profile=profile,
        run_id=run.id,
    )
    await runs.update_fields(run.id, status=RunStatus.SUCCEEDED)
    return result


async def enqueue_browser_extraction(
    session: AsyncSession,
    *,
    job_target_id: uuid.UUID,
    force: bool = False,
) -> dict[str, Any]:
    if not force:
        cached = await get_cached_extraction(session, job_target_id)
        if cached is not None:
            return {"status": "cached", "extraction": cached.model_dump()}

    jobs = JobTargetRepository(session)
    job = await jobs.get(job_target_id)
    if job is None:
        msg = "Job target not found"
        raise ValueError(msg)
    url = (job.direct_apply_url or job.company_careers_url or "").strip()
    if not url:
        msg = "Job target has no apply URL"
        raise ValueError(msg)

    runs = ApplicationRunRepository(session)
    run = await runs.create(
        job_target_id=job_target_id,
        status=RunStatus.QUEUED,
        current_step=RunStatus.OPEN_JOB,
        policy=RunPolicy.DRY_RUN,
    )

    from jober_api.services.job_extraction.celery_dispatch import dispatch_extract_job

    task_id = dispatch_extract_job(str(run.id), str(job_target_id), url, force)
    payload: dict[str, Any] = {
        "status": "queued",
        "run_id": str(run.id),
        "task_id": task_id,
    }
    if task_id is None:
        payload["warning"] = (
            "Run created but worker task was not enqueued. Start Celery/worker or use fixture_html."
        )
    return payload
