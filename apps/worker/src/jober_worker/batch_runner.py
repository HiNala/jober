from __future__ import annotations

import asyncio
import json
import time
import uuid
from datetime import UTC, datetime
from typing import Any

import httpx
from jober_api.models.application_run import ApplicationRun
from jober_api.models.batch_item import BatchItem
from jober_api.models.enums import BatchItemStatus, RunPolicy, RunStatus
from jober_api.privacy.redaction import scrub_dict, scrub_event_message
from jober_api.services.batch import redis_control
from jober_api.services.batch.domain import job_apply_url
from sqlalchemy import select, text
from sqlalchemy.orm import Session, joinedload

from jober_worker.config import settings as worker_settings
from jober_worker.db import get_sync_session


def _sync_append_run_event(
    session: Session,
    *,
    run_id: uuid.UUID,
    event_type: str,
    message: str,
    payload: dict[str, Any] | None = None,
) -> None:
    seq_row = session.execute(
        text("SELECT COALESCE(MAX(seq), 0) + 1 FROM run_events WHERE run_id = :run_id"),
        {"run_id": str(run_id)},
    ).scalar_one()
    session.execute(
        text(
            """
            INSERT INTO run_events (
                id, run_id, seq, ts, event_type, level, message, payload
            ) VALUES (
                :id, :run_id, :seq, :ts, :event_type, 'info', :message,
                CAST(:payload AS jsonb)
            )
            """
        ),
        {
            "id": str(uuid.uuid4()),
            "run_id": str(run_id),
            "seq": int(seq_row),
            "ts": datetime.now(UTC),
            "event_type": event_type,
            "message": scrub_event_message(message),
            "payload": json.dumps(scrub_dict(payload)),
        },
    )


async def _run_fixture_pipeline(
    *,
    job_target_id: uuid.UUID,
    html: str,
    platform: str,
    run_id: uuid.UUID,
    tenant_id: uuid.UUID,
    batch_filters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from jober_api.models.enums import RunStatus
    from jober_api.services.documents.generation_prefs import resolve_user_id_for_tenant
    from jober_api.services.documents.run_documents import (
        generate_documents_for_run,
        should_generate_for_run,
    )
    from jober_api.services.form_discovery.service import discover_from_fixture_html
    from jober_api.services.form_fill.service import fill_from_fixture_html
    from jober_api.storage.minio_client import ObjectStorage
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    engine = create_async_engine(worker_settings.database_url, connect_args={"ssl": False})
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    try:
        async with factory() as session:
            discover = await discover_from_fixture_html(
                session,
                job_target_id=job_target_id,
                html=html,
                platform=platform,
            )
            await session.commit()
            attempt_id = uuid.UUID(discover.attempt_id)
            user_id = await resolve_user_id_for_tenant(session, tenant_id)
            run_row = await session.get(ApplicationRun, run_id)
            checkpoint = dict(run_row.checkpoint_data or {}) if run_row else {}
            should_gen, letter_options = await should_generate_for_run(
                session,
                tenant_id=tenant_id,
                user_id=user_id,
                batch_filters=batch_filters,
                run_checkpoint=checkpoint,
                job_target_id=job_target_id,
                observations_attempt_id=attempt_id,
            )
            documents: dict[str, Any] | None = None
            if should_gen and user_id is not None:
                if run_row is not None:
                    run_row.current_step = RunStatus.GENERATE_DOCUMENTS
                    await session.flush()
                storage = ObjectStorage()
                documents = await generate_documents_for_run(
                    session,
                    storage,
                    tenant_id=tenant_id,
                    user_id=user_id,
                    job_target_id=job_target_id,
                    run_id=run_id,
                    options=letter_options,
                )
                await session.commit()
            else:
                documents = {"skipped": True, "reason": "cover_letter_disabled_or_unneeded"}
            fill = await fill_from_fixture_html(
                session,
                job_target_id=job_target_id,
                fixture_html=html,
                observations_attempt_id=attempt_id,
            )
            await session.commit()
            return {
                "discover": discover.model_dump(),
                "documents": documents,
                "fill": fill,
            }
    finally:
        await engine.dispose()


def run_batch_item(item_id: uuid.UUID) -> dict[str, Any]:
    run_id: uuid.UUID | None = None
    domain = "unknown"
    with get_sync_session() as session:
        stmt = (
            select(BatchItem)
            .where(BatchItem.id == item_id)
            .options(joinedload(BatchItem.batch), joinedload(BatchItem.job_target))
        )
        item = session.execute(stmt).scalar_one_or_none()
        if item is None:
            return {"status": "missing"}
        if item.status != BatchItemStatus.PENDING:
            redis_control.release_batch_item_claim(str(item_id))
            return {"status": "not_pending", "item_status": item.status.value}
        batch = item.batch
        job = item.job_target
        if batch is None or job is None:
            redis_control.release_batch_item_claim(str(item_id))
            return {"status": "invalid_item"}
        if redis_control.is_batch_paused(str(batch.id)) or redis_control.is_globally_paused():
            redis_control.release_batch_item_claim(str(item_id))
            return {"status": "paused"}
        if redis_control.is_tenant_paused(str(batch.tenant_id)):
            redis_control.release_batch_item_claim(str(item_id))
            return {"status": "tenant_paused"}
        url = job_apply_url(job)
        domain = item.domain
        if not redis_control.try_acquire_domain_lock(domain, str(item.id)):
            return {"status": "domain_busy", "domain": domain}
        run_id = uuid.uuid4()
        try:
            item.status = BatchItemStatus.RUNNING
            run = ApplicationRun(
                id=run_id,
                tenant_id=job.tenant_id,
                job_target_id=job.id,
                batch_id=batch.id,
                status=RunStatus.QUEUED,
                current_step=RunStatus.PREPARE_CONTEXT,
                policy=batch.policy,
                started_at=datetime.now(UTC),
            )
            session.add(run)
            item.run_id = run_id
            session.flush()
            redis_control.register_active_run(str(run_id))
            waited = redis_control.wait_for_domain_cooldown(domain, batch.site_cooldown_seconds)
            redis_control.record_domain_request(domain)
            _sync_append_run_event(
                session,
                run_id=run_id,
                event_type="batch.cooldown",
                message="Per-site cooldown honored before request",
                payload={"domain": domain, "waited_seconds": round(waited, 3)},
            )
            if batch.action_delay_ms > 0:
                time.sleep(batch.action_delay_ms / 1000.0)
            if redis_control.is_run_cancelled(str(run_id)):
                item.status = BatchItemStatus.CANCELLED
                run.status = RunStatus.SKIPPED
                run.completed_at = datetime.now(UTC)
                session.commit()
                return {"status": "cancelled", "run_id": str(run_id)}
            response = httpx.get(url, timeout=30.0)
            response.raise_for_status()
            html = response.text
            platform = str((job.platform_detection or {}).get("platform", "greenhouse"))
            if batch.policy != RunPolicy.DRY_RUN:
                from jober_api.services.batch.cost_governor import assert_generation_budget

                async def _budget() -> None:
                    from sqlalchemy.ext.asyncio import (
                        AsyncSession,
                        async_sessionmaker,
                        create_async_engine,
                    )

                    engine = create_async_engine(
                        worker_settings.database_url, connect_args={"ssl": False}
                    )
                    factory = async_sessionmaker(
                        engine, class_=AsyncSession, expire_on_commit=False
                    )
                    try:
                        async with factory() as async_session:
                            await assert_generation_budget(async_session, projected_cost=0.2)
                    finally:
                        await engine.dispose()

                asyncio.run(_budget())
            pipeline = asyncio.run(
                _run_fixture_pipeline(
                    job_target_id=job.id,
                    html=html,
                    platform=platform,
                    run_id=run_id,
                    tenant_id=job.tenant_id,
                    batch_filters=dict(batch.filters or {}),
                )
            )
            item.status = BatchItemStatus.SUCCEEDED
            run.status = RunStatus.SUCCEEDED
            run.completed_at = datetime.now(UTC)
            session.commit()
            return {"status": "succeeded", "run_id": str(run_id), "pipeline": pipeline}
        except Exception as exc:
            import logging

            from jober_api.privacy.logging import safe_log

            item.status = BatchItemStatus.FAILED
            if run_id is not None:
                run_row = session.get(ApplicationRun, run_id)
                if run_row is not None:
                    run_row.status = RunStatus.FAILED_FINAL
                    run_row.failure_reason = str(exc)[:500]
                    run_row.completed_at = datetime.now(UTC)
            safe_log(
                logging.ERROR,
                "batch_item_failed",
                run_id=str(run_id) if run_id is not None else None,
                tenant_id=str(job.tenant_id),
                batch_item_id=str(item.id),
                error=str(exc)[:500],
            )
            session.commit()
            return {"status": "failed", "error": str(exc)}
        finally:
            if run_id is not None:
                redis_control.unregister_active_run(str(run_id))
            redis_control.release_domain_lock(domain, str(item.id))
            from jober_worker.tasks import batch_orchestrator_tick

            batch_orchestrator_tick.delay(str(batch.id))
