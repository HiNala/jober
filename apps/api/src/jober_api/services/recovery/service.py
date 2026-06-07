from __future__ import annotations

import asyncio
import uuid
from datetime import UTC, datetime
from typing import Any

from jober_recover.budget import AttemptBudget
from jober_recover.circuit_breaker import CircuitBreaker
from jober_recover.failure_report import build_failure_report
from jober_recover.self_assessment import build_self_assessment
from jober_recover.strategy import RecoveryStrategy, propose_recovery_strategy
from jober_recover.taxonomy import FailureClass, is_human_only
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.application_attempt import ApplicationAttempt
from jober_api.models.application_run import ApplicationRun
from jober_api.models.enums import RunPolicy, RunStatus
from jober_api.models.failure_event import FailureEvent
from jober_api.repositories.application_run import ApplicationRunRepository
from jober_api.repositories.field_mapping_memory import FieldMappingMemoryRepository
from jober_api.repositories.form_field_observation import FormFieldObservationRepository
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.services.verification.service import _profile_values_for_observations
from jober_api.vault.field_registry import FIELD_BY_KEY, FieldTier

_circuit_breaker = CircuitBreaker(threshold=5)


async def _load_observations(
    session: AsyncSession,
    job_target_id: uuid.UUID,
) -> list[dict[str, Any]]:
    obs_repo = FormFieldObservationRepository(session)
    rows = await obs_repo.list_for_job_latest(job_target_id)
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
    return payloads


async def _record_failure_event(
    session: AsyncSession,
    *,
    job_target_id: uuid.UUID,
    run_id: uuid.UUID,
    platform: str,
    failure_class: FailureClass,
) -> None:
    row = FailureEvent(
        id=uuid.uuid4(),
        job_target_id=job_target_id,
        run_id=run_id,
        platform=platform.casefold(),
        failure_class=failure_class.value,
        created_at=datetime.now(UTC),
    )
    session.add(row)
    await session.flush()
    _circuit_breaker.record(platform, failure_class)


async def recovery_fill_from_fixture(
    session: AsyncSession,
    *,
    job_target_id: uuid.UUID,
    fixture_html: str,
    platform: str = "greenhouse",
    force_brittle: bool = False,
    simulate_failure_class: str | None = None,
) -> dict[str, Any]:
    jobs = JobTargetRepository(session)
    job = await jobs.get(job_target_id)
    if job is None:
        msg = "Job target not found"
        raise ValueError(msg)

    observations = await _load_observations(session, job_target_id)
    profile_values = await _profile_values_for_observations(session, observations)

    runs = ApplicationRunRepository(session)
    now = datetime.now(UTC)
    run = await runs.create(
        job_target_id=job_target_id,
        status=RunStatus.FILL_FORM,
        current_step=RunStatus.FILL_FORM,
        policy=RunPolicy.REVIEW_BEFORE_SUBMIT,
        started_at=now,
    )
    run_id = run.id
    await session.commit()

    budget = AttemptBudget()
    assessments: list[dict[str, Any]] = []
    attempted_actions: list[str] = []
    last_failure_class = FailureClass.UNKNOWN
    last_error = ""
    last_keys: dict[str, str] = {}

    from jober_worker.attempt_manager import (
        create_attempt,
        persist_attempt_failure,
        persist_attempt_success,
        persist_final_failure_report,
    )
    from jober_worker.recovery_runner import run_fixture_recovery_fill

    for attempt_index in range(1, budget.max_attempts + 1):
        if force_brittle:
            strategy = RecoveryStrategy(
                name="primary_css",
                locator_mode="css",
                description="Forced brittle CSS (test exhaust)",
            )
        else:
            strategy = propose_recovery_strategy(
                last_failure_class if attempt_index > 1 else FailureClass.SELECTOR,
                attempt_index=attempt_index,
                platform=platform,
            )

        attempt_id = await asyncio.to_thread(
            create_attempt,
            run_id=run_id,
            attempt_index=attempt_index,
            strategy_name=strategy.name,
        )
        attempted_actions.append(f"{strategy.name}:{strategy.locator_mode}")

        if simulate_failure_class:
            failure_class = FailureClass(simulate_failure_class)
            result = {
                "status": "failed",
                "failure_class": failure_class.value,
                "error": f"Simulated {failure_class.value} for fixture test",
                "artifact_keys": {},
            }
        else:
            result = await asyncio.to_thread(
                run_fixture_recovery_fill,
                run_id=run_id,
                attempt_id=attempt_id,
                fixture_html=fixture_html,
                observations=observations,
                profile_values=profile_values,
                strategy=strategy,
            )

        if result.get("status") == "succeeded":
            if strategy.remember_mapping:
                memory = FieldMappingMemoryRepository(session)
                for obs in observations:
                    label = obs.get("label")
                    mapped = obs.get("mapped_profile_field")
                    if label and mapped:
                        await memory.remember(platform, label, mapped)
                await session.commit()
            await asyncio.to_thread(
                persist_attempt_success,
                run_id=run_id,
                attempt_id=attempt_id,
                artifact_keys=result.get("artifact_keys", {}),
            )
            return {
                "run_id": str(run_id),
                "status": "succeeded",
                "attempt_count": attempt_index,
                "strategy": result.get("strategy"),
                "filled": result.get("filled", []),
                "resumed_from_checkpoint": result.get("resumed_from_checkpoint", False),
            }

        last_error = str(result.get("error", "unknown failure"))
        last_failure_class = FailureClass(result.get("failure_class", FailureClass.UNKNOWN.value))
        last_keys = result.get("artifact_keys", {})
        next_strategy = (
            propose_recovery_strategy(
                last_failure_class,
                attempt_index=attempt_index + 1,
                platform=platform,
            )
            if budget.can_retry(attempt_index, failure_class=last_failure_class)
            else None
        )
        assessment = build_self_assessment(
            attempt_index=attempt_index,
            strategy=strategy,
            failure_class=last_failure_class,
            error_message=last_error,
            next_strategy=next_strategy,
        )
        assessments.append(assessment.to_dict())

        await asyncio.to_thread(
            persist_attempt_failure,
            run_id=run_id,
            attempt_id=attempt_id,
            failure_class=last_failure_class,
            error_message=last_error,
            assessment=assessment,
            artifact_keys=last_keys,
            budget=budget,
        )
        await _record_failure_event(
            session,
            job_target_id=job_target_id,
            run_id=run_id,
            platform=platform,
            failure_class=last_failure_class,
        )
        await session.commit()

        if not budget.can_retry(attempt_index, failure_class=last_failure_class):
            break

    final_status = (
        RunStatus.NEEDS_HUMAN if is_human_only(last_failure_class) else RunStatus.FAILED_FINAL
    )
    attempt_total = len(assessments) if is_human_only(last_failure_class) else budget.max_attempts
    report = build_failure_report(
        job_target_id=str(job_target_id),
        company=job.company,
        role=job.role,
        apply_url=job.direct_apply_url,
        failed_step=RunStatus.FILL_FORM.value,
        failure_class=last_failure_class,
        error_message=last_error,
        attempt_count=attempt_total,
        artifact_keys={k: v for k, v in last_keys.items()},
        attempted_actions=attempted_actions,
        self_assessments=assessments,
    )
    await asyncio.to_thread(
        persist_final_failure_report,
        run_id=run_id,
        report=report,
        run_status=final_status.value,
    )
    await session.commit()

    circuit_state = _circuit_breaker.state_for(platform, last_failure_class)
    return {
        "run_id": str(run_id),
        "status": final_status.value,
        "failure_report": report.to_dict(),
        "circuit_alert": circuit_state.to_dict() if circuit_state.tripped else None,
    }


async def get_failure_report_for_job(
    session: AsyncSession,
    job_target_id: uuid.UUID,
) -> dict[str, Any] | None:
    stmt = (
        select(ApplicationRun)
        .where(
            ApplicationRun.job_target_id == job_target_id,
            ApplicationRun.status.in_(
                (RunStatus.FAILED_FINAL, RunStatus.FAILED_RETRYABLE, RunStatus.NEEDS_HUMAN)
            ),
        )
        .order_by(ApplicationRun.updated_at.desc())
        .limit(1)
    )
    run = (await session.execute(stmt)).scalar_one_or_none()
    if run is None:
        return None
    return await get_failure_report(session, run.id)


async def get_failure_report(session: AsyncSession, run_id: uuid.UUID) -> dict[str, Any]:
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

    checkpoint = run.checkpoint_data or {}
    embedded = checkpoint.get("failure_report")
    if embedded:
        return dict(embedded)

    stmt = (
        select(ApplicationAttempt)
        .where(ApplicationAttempt.run_id == run_id)
        .order_by(ApplicationAttempt.attempt_index.asc())
    )
    attempts = list((await session.execute(stmt)).scalars())
    assessments = [a.self_assessment for a in attempts if a.self_assessment]
    last = attempts[-1] if attempts else None
    failure_class = (
        FailureClass(last.failure_class)
        if last and last.failure_class
        else FailureClass.UNKNOWN
    )

    report = build_failure_report(
        job_target_id=str(run.job_target_id),
        company=job.company,
        role=job.role,
        apply_url=job.direct_apply_url,
        failed_step=(run.current_step or run.status).value,
        failure_class=failure_class,
        error_message=run.failure_reason or "Run failed",
        attempt_count=run.attempt_count or len(attempts),
        artifact_keys={
            "screenshot": last.final_screenshot_object_key if last else None,
            "dom": last.dom_snapshot_object_key if last else None,
        },
        attempted_actions=[a.strategy_name or "" for a in attempts if a.strategy_name],
        self_assessments=[dict(a) for a in assessments if a],
    )
    return report.to_dict()


async def resume_from_checkpoint(session: AsyncSession, run_id: uuid.UUID) -> dict[str, Any]:
    runs = ApplicationRunRepository(session)
    run = await runs.get(run_id)
    if run is None:
        msg = "Run not found"
        raise ValueError(msg)

    checkpoint = run.checkpoint_data or {}
    if not checkpoint.get("step"):
        msg = "No checkpoint to resume from"
        raise ValueError(msg)

    next_index = (run.attempt_count or 0) + 1
    from jober_worker.attempt_manager import create_attempt

    attempt_id = await asyncio.to_thread(
        create_attempt,
        run_id=run_id,
        attempt_index=next_index,
        strategy_name="resume_from_checkpoint",
    )
    await runs.update_fields(
        run_id,
        status=RunStatus.FILL_FORM,
        current_step=RunStatus.FILL_FORM,
    )
    await session.commit()

    return {
        "run_id": str(run_id),
        "attempt_id": str(attempt_id),
        "attempt_index": next_index,
        "checkpoint": checkpoint,
    }


async def get_failure_analytics(session: AsyncSession) -> dict[str, Any]:
    threshold = _circuit_breaker.threshold
    stmt = (
        select(
            FailureEvent.platform,
            FailureEvent.failure_class,
            func.count(FailureEvent.id),
        )
        .group_by(FailureEvent.platform, FailureEvent.failure_class)
        .order_by(func.count(FailureEvent.id).desc())
    )
    rows = (await session.execute(stmt)).all()
    buckets: list[dict[str, Any]] = []
    alerts: list[dict[str, Any]] = []
    for platform, failure_class, count in rows:
        tripped = int(count) >= threshold
        buckets.append(
            {
                "platform": platform,
                "failure_class": failure_class,
                "count": int(count),
                "circuit_tripped": tripped,
            }
        )
        if tripped:
            alerts.append(
                {
                    "tripped": True,
                    "platform": platform,
                    "failure_class": failure_class,
                    "count": int(count),
                    "threshold": threshold,
                    "message": (
                        f"Circuit breaker: {count} {failure_class} failures on {platform}"
                    ),
                }
            )
    return {"buckets": buckets, "alerts": alerts}
