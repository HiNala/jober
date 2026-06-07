from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from jober_api.config import settings
from jober_api.models.application_batch import ApplicationBatch
from jober_api.models.batch_item import BatchItem
from jober_api.models.enums import BatchItemStatus, BatchStatus
from jober_api.services.batch import redis_control
from jober_api.services.batch.quiet_hours import in_quiet_hours
from jober_worker.db import get_sync_session


def _complete_batch_if_done(session: object, batch: ApplicationBatch) -> None:
    pending = session.execute(  # type: ignore[union-attr]
        select(BatchItem).where(
            BatchItem.batch_id == batch.id,
            BatchItem.status.in_([BatchItemStatus.PENDING, BatchItemStatus.RUNNING]),
        )
    ).scalars().all()
    if not pending:
        batch.status = BatchStatus.COMPLETED
        batch.completed_at = datetime.now(UTC)


def run_orchestrator_tick(batch_id: str | None = None) -> dict[str, object]:
    if redis_control.is_globally_paused():
        return {"status": "globally_paused"}
    max_conc = redis_control.get_max_concurrency(settings.batch_max_concurrency)
    if redis_control.count_active_slots() >= max_conc:
        return {"status": "at_capacity", "max_concurrency": max_conc}
    with get_sync_session() as session:
        stmt = (
            select(BatchItem)
            .join(ApplicationBatch)
            .where(
                ApplicationBatch.status == BatchStatus.RUNNING,
                BatchItem.status == BatchItemStatus.PENDING,
            )
            .options(joinedload(BatchItem.batch))
            .order_by(ApplicationBatch.created_at.asc(), BatchItem.sort_order.asc())
        )
        if batch_id:
            stmt = stmt.where(ApplicationBatch.id == uuid.UUID(batch_id))
        item = session.execute(stmt).scalars().first()
        if item is None:
            if batch_id:
                batch = session.get(ApplicationBatch, uuid.UUID(batch_id))
                if batch is not None:
                    _complete_batch_if_done(session, batch)
                    session.commit()
            return {"status": "idle"}
        batch = item.batch
        if batch is None:
            return {"status": "invalid"}
        if redis_control.is_batch_paused(str(batch.id)):
            return {"status": "batch_paused", "batch_id": str(batch.id)}
        if in_quiet_hours(
            start=batch.quiet_hours_start or settings.quiet_hours_start,
            end=batch.quiet_hours_end or settings.quiet_hours_end,
            timezone=settings.quiet_hours_timezone,
        ) and batch.policy.value != "dry_run":
            return {"status": "quiet_hours"}
        holder = redis_control.domain_lock_holder(item.domain)
        if holder is not None:
            return {"status": "domain_locked", "domain": item.domain, "holder": holder}
        from jober_worker.tasks import execute_batch_item

        task = execute_batch_item.delay(str(item.id))
        return {"status": "dispatched", "item_id": str(item.id), "task_id": str(task.id)}
