from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from jober_verify.idempotency import has_prior_successful_run
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.config import settings
from jober_api.models.application_batch import ApplicationBatch
from jober_api.models.application_run import ApplicationRun
from jober_api.models.batch_item import BatchItem
from jober_api.models.enums import (
    BatchItemStatus,
    BatchStatus,
    JobTargetStatus,
    RunPolicy,
    RunStatus,
)
from jober_api.repositories.application_batch import ApplicationBatchRepository, BatchItemRepository
from jober_api.repositories.application_run import ApplicationRunRepository
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.services.ats_guess import guess_ats
from jober_api.services.batch import redis_control
from jober_api.services.batch.domain import extract_domain, job_apply_url
from jober_api.services.batch.quiet_hours import in_quiet_hours


class BatchValidationError(ValueError):
    pass


def _parse_policy(raw: str | None) -> RunPolicy:
    if raw is None:
        return RunPolicy.REVIEW_BEFORE_SUBMIT
    try:
        policy = RunPolicy(raw)
    except ValueError as exc:
        msg = f"Invalid policy: {raw}"
        raise BatchValidationError(msg) from exc
    if policy == RunPolicy.AUTO_SUBMIT and not settings.auto_submit_opt_in:
        msg = "auto_submit requires explicit local opt-in (AUTO_SUBMIT_OPT_IN=true)"
        raise BatchValidationError(msg)
    return policy


async def _eligible_jobs(session: AsyncSession, filters: dict[str, Any]) -> list[Any]:
    repo = JobTargetRepository(session)
    status_raw = filters.get("status")
    status = JobTargetStatus(status_raw) if status_raw else None
    rows = await repo.list_filtered(
        status=status,
        priority=str(filters["priority"]) if filters.get("priority") else None,
        company=str(filters["company"]) if filters.get("company") else None,
        role=str(filters["role"]) if filters.get("role") else None,
        location=str(filters["location"]) if filters.get("location") else None,
        limit=int(filters.get("limit", 500)),
    )
    ats = filters.get("ats_guess")
    if ats:
        rows = [job for job in rows if guess_ats(job_apply_url(job)) == ats]
    return rows


async def _skip_reason(session: AsyncSession, job: Any) -> str | None:
    if job.status == JobTargetStatus.APPLIED:
        return "already_applied"
    runs = await ApplicationRunRepository(session).list_for_job(job.id)
    if has_prior_successful_run(runs):
        return "prior_successful_run"
    url = job_apply_url(job)
    if not url:
        return "missing_apply_url"
    return None


async def preview_batch(session: AsyncSession, filters: dict[str, Any]) -> dict[str, Any]:
    jobs = await _eligible_jobs(session, filters)
    included: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    domains: set[str] = set()
    for job in jobs:
        reason = await _skip_reason(session, job)
        url = job_apply_url(job)
        domain = extract_domain(url) if url else "unknown"
        entry = {
            "job_target_id": str(job.id),
            "company": job.company,
            "role": job.role,
            "priority": job.priority,
            "domain": domain,
            "apply_url": url,
        }
        if reason:
            excluded.append({**entry, "reason": reason})
        else:
            domains.add(domain)
            included.append(entry)
    est_cost = len(included) * 0.18
    return {
        "filters": filters,
        "included": included,
        "excluded": excluded,
        "domain_count": len(domains),
        "estimated_cost_usd": round(est_cost, 2),
    }


async def create_batch(
    session: AsyncSession,
    *,
    name: str,
    policy: str,
    filters: dict[str, Any],
    scheduled_at: datetime | None = None,
    max_concurrency: int | None = None,
    site_cooldown_seconds: float | None = None,
) -> ApplicationBatch:
    preview = await preview_batch(session, filters)
    if not preview["included"]:
        msg = "No eligible jobs for batch"
        raise BatchValidationError(msg)
    parsed_policy = _parse_policy(policy)
    batch = ApplicationBatch(
        name=name,
        status=BatchStatus.SCHEDULED if scheduled_at else BatchStatus.DRAFT,
        policy=parsed_policy,
        filters=filters,
        scheduled_at=scheduled_at,
        quiet_hours_start=settings.quiet_hours_start,
        quiet_hours_end=settings.quiet_hours_end,
        max_concurrency=max_concurrency or settings.batch_max_concurrency,
        site_cooldown_seconds=site_cooldown_seconds or settings.batch_site_cooldown_seconds,
        action_delay_ms=settings.batch_action_delay_ms,
    )
    session.add(batch)
    await session.flush()
    for index, row in enumerate(preview["included"]):
        item = BatchItem(
            batch_id=batch.id,
            job_target_id=uuid.UUID(row["job_target_id"]),
            sort_order=index,
            status=BatchItemStatus.PENDING,
            domain=row["domain"],
        )
        session.add(item)
    await session.flush()
    await session.refresh(batch)
    return batch


async def enqueue_batch(
    session: AsyncSession, batch_id: uuid.UUID, *, run_at: datetime | None = None
) -> dict[str, Any]:
    batches = ApplicationBatchRepository(session)
    batch = await batches.get(batch_id)
    if batch is None:
        msg = "Batch not found"
        raise BatchValidationError(msg)
    if batch.status in (BatchStatus.CANCELLED, BatchStatus.COMPLETED):
        msg = f"Batch is {batch.status.value}"
        raise BatchValidationError(msg)
    if (
        in_quiet_hours(
            start=batch.quiet_hours_start or settings.quiet_hours_start,
            end=batch.quiet_hours_end or settings.quiet_hours_end,
            timezone=settings.quiet_hours_timezone,
        )
        and batch.policy != RunPolicy.DRY_RUN
    ):
        msg = "Quiet hours active — schedule for later or use dry_run"
        raise BatchValidationError(msg)
    batch.status = BatchStatus.RUNNING
    batch.started_at = datetime.now(UTC)
    if run_at:
        batch.scheduled_at = run_at
    await session.flush()
    from jober_api.services.batch.celery_dispatch import dispatch_batch_tick

    task_id = dispatch_batch_tick(str(batch.id))
    return {
        "batch_id": str(batch.id),
        "status": batch.status.value,
        "orchestrator_task_id": task_id,
    }


async def pause_all_batches() -> dict[str, str]:
    redis_control.pause_all()
    return {"status": "paused"}


async def resume_all_batches() -> dict[str, str]:
    redis_control.resume_all()
    return {"status": "resumed"}


async def pause_batch(batch_id: uuid.UUID) -> None:
    redis_control.set_batch_paused(str(batch_id), True)


async def resume_batch(batch_id: uuid.UUID) -> None:
    redis_control.set_batch_paused(str(batch_id), False)


async def cancel_run(session: AsyncSession, run_id: uuid.UUID) -> None:
    redis_control.mark_run_cancelled(str(run_id))
    runs = ApplicationRunRepository(session)
    await runs.update_fields(run_id, status=RunStatus.SKIPPED, completed_at=datetime.now(UTC))


async def skip_batch_item(
    session: AsyncSession, item_id: uuid.UUID, reason: str = "skipped_by_user"
) -> None:
    items = BatchItemRepository(session)
    item = await items.get(item_id)
    if item is None:
        msg = "Batch item not found"
        raise BatchValidationError(msg)
    item.status = BatchItemStatus.SKIPPED
    item.skip_reason = reason
    await session.flush()


async def reorder_batch_items(
    session: AsyncSession, batch_id: uuid.UUID, ordered_ids: list[uuid.UUID]
) -> None:
    items = BatchItemRepository(session)
    rows = await items.list_for_batch(batch_id)
    by_id = {row.id: row for row in rows}
    for index, item_id in enumerate(ordered_ids):
        row = by_id.get(item_id)
        if row is not None:
            row.sort_order = index
    await session.flush()


async def dashboard_summary(session: AsyncSession) -> dict[str, Any]:
    priority_a = await JobTargetRepository(session).list_filtered(priority="A", limit=2000)
    queue_depth = len(
        [
            j
            for j in priority_a
            if j.status not in (JobTargetStatus.APPLIED, JobTargetStatus.SKIPPED)
        ]
    )
    active_stmt = (
        select(func.count())
        .select_from(ApplicationRun)
        .where(
            ApplicationRun.status.notin_(
                [
                    RunStatus.SUCCEEDED,
                    RunStatus.FAILED_FINAL,
                    RunStatus.FAILED_RETRYABLE,
                    RunStatus.SKIPPED,
                ]
            )
        )
    )
    active_runs = int((await session.execute(active_stmt)).scalar_one())
    needs_review = int(
        (
            await session.execute(
                select(func.count())
                .select_from(ApplicationRun)
                .where(ApplicationRun.status == RunStatus.NEEDS_HUMAN)
            )
        ).scalar_one()
    )
    queue = redis_control.queue_snapshot(settings.batch_max_concurrency)
    batches = ApplicationBatchRepository(session)
    running_batches = await batches.list_running()
    batch_summaries = []
    for batch in running_batches:
        counts = await BatchItemRepository(session).count_by_status(batch.id)
        batch_summaries.append(
            {
                "id": str(batch.id),
                "name": batch.name,
                "status": batch.status.value,
                "policy": batch.policy.value,
                "counts": counts,
            }
        )
    return {
        "queue_depth_priority_a": queue_depth,
        "active_runs": active_runs,
        "needs_review": needs_review,
        "worker": queue,
        "batches": batch_summaries,
    }


async def serialize_batch(session: AsyncSession, batch_id: uuid.UUID) -> dict[str, Any]:
    batches = ApplicationBatchRepository(session)
    batch = await batches.get_with_items(batch_id)
    if batch is None:
        msg = "Batch not found"
        raise BatchValidationError(msg)
    counts = await BatchItemRepository(session).count_by_status(batch.id)
    return {
        "id": str(batch.id),
        "name": batch.name,
        "status": batch.status.value,
        "policy": batch.policy.value,
        "filters": batch.filters,
        "scheduled_at": batch.scheduled_at.isoformat() if batch.scheduled_at else None,
        "max_concurrency": batch.max_concurrency,
        "site_cooldown_seconds": batch.site_cooldown_seconds,
        "counts": counts,
        "items": [
            {
                "id": str(item.id),
                "job_target_id": str(item.job_target_id),
                "sort_order": item.sort_order,
                "status": item.status.value,
                "domain": item.domain,
                "run_id": str(item.run_id) if item.run_id else None,
                "skip_reason": item.skip_reason,
            }
            for item in batch.items
        ],
    }
