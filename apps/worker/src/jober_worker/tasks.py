from __future__ import annotations

import uuid

from jober_worker.celery_app import celery_app
from jober_worker.extraction_runner import run_browser_extraction
from jober_worker.fill_runner import run_browser_form_fill
from jober_worker.job_context import load_extraction_context


@celery_app.task(name="jober_worker.tasks.ping")
def ping() -> str:
    return "pong"


@celery_app.task(name="jober_worker.tasks.extract_job", bind=True)
def extract_job(
    self: object,
    run_id: str,
    job_target_id: str,
    url: str,
    force: bool = False,
) -> dict[str, object]:
    del self, force
    ctx = load_extraction_context(uuid.UUID(job_target_id))
    return run_browser_extraction(
        run_id=uuid.UUID(run_id),
        job_target_id=uuid.UUID(job_target_id),
        url=url,
        company_hint=str(ctx.get("company_hint", "")),
        resume_skills=ctx.get("resume_skills") or None,
    )


@celery_app.task(name="jober_worker.tasks.fill_form", bind=True)
def fill_form(
    self: object,
    run_id: str,
    job_target_id: str,
    url: str,
) -> dict[str, object]:
    del self
    from sqlalchemy import text

    from jober_worker.db import get_sync_session

    with get_sync_session() as session:
        row = session.execute(
            text(
                """
                SELECT id FROM application_attempts
                WHERE run_id = :run_id
                ORDER BY attempt_index DESC
                LIMIT 1
                """
            ),
            {"run_id": run_id},
        ).mappings().first()
    if row is None:
        msg = "No application attempt for fill run"
        raise ValueError(msg)
    return run_browser_form_fill(
        run_id=uuid.UUID(run_id),
        attempt_id=uuid.UUID(str(row["id"])),
        job_target_id=uuid.UUID(job_target_id),
        url=url,
    )


@celery_app.task(name="jober_worker.tasks.batch_orchestrator_tick")
def batch_orchestrator_tick(batch_id: str | None = None) -> dict[str, object]:
    from jober_worker.batch_orchestrator import run_orchestrator_tick

    return run_orchestrator_tick(batch_id)


@celery_app.task(name="jober_worker.tasks.run_artifact_retention_purge")
def run_artifact_retention_purge() -> dict[str, object]:
    import asyncio

    from jober_api.db.session import async_session_factory
    from jober_api.services.privacy.artifact_retention import purge_stale_run_artifacts

    async def _run() -> dict[str, object]:
        async with async_session_factory() as session:
            return await purge_stale_run_artifacts(session)

    return asyncio.run(_run())


@celery_app.task(name="jober_worker.tasks.analytics_retention_purge")
def analytics_retention_purge() -> dict[str, object]:
    from jober_api.services.analytics.retention import purge_stale_analytics_events_sync

    from jober_worker.db import get_sync_session

    with get_sync_session() as session:
        result: dict[str, object] = purge_stale_analytics_events_sync(session)
        return result


@celery_app.task(name="jober_worker.tasks.analytics_daily_rollup")
def analytics_daily_rollup(day: str | None = None) -> dict[str, object]:
    from datetime import UTC, date, datetime, timedelta

    from jober_api.services.analytics.rollups import rollup_analytics_day_sync

    from jober_worker.db import get_sync_session

    target = date.fromisoformat(day) if day else (datetime.now(UTC).date() - timedelta(days=1))
    with get_sync_session() as session:
        result: dict[str, object] = rollup_analytics_day_sync(session, target)
        return result


@celery_app.task(name="jober_worker.tasks.execute_batch_item", bind=True)
def execute_batch_item(self: object, item_id: str) -> dict[str, object]:
    del self
    from jober_worker.batch_runner import run_batch_item

    return run_batch_item(uuid.UUID(item_id))
