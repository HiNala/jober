import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from jober_api.models.application_batch import ApplicationBatch
from jober_api.models.batch_item import BatchItem
from jober_api.models.enums import BatchItemStatus, BatchStatus
from jober_api.repositories.base import Repository
from jober_api.repositories.tenant_scope import belongs_to_tenant, scope_stmt


class ApplicationBatchRepository(Repository[ApplicationBatch]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None = None) -> None:
        super().__init__(session, ApplicationBatch)
        self._tenant_id = tenant_id

    async def get(self, entity_id: uuid.UUID) -> ApplicationBatch | None:
        row = await super().get(entity_id)
        if not belongs_to_tenant(row, self._tenant_id):
            return None
        return row

    async def get_with_items(self, batch_id: uuid.UUID) -> ApplicationBatch | None:
        stmt = (
            scope_stmt(select(ApplicationBatch), ApplicationBatch, self._tenant_id)
            .where(ApplicationBatch.id == batch_id)
            .options(selectinload(ApplicationBatch.items).selectinload(BatchItem.job_target))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_recent(self, limit: int = 20) -> list[ApplicationBatch]:
        stmt = (
            scope_stmt(select(ApplicationBatch), ApplicationBatch, self._tenant_id)
            .order_by(ApplicationBatch.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_running(self) -> list[ApplicationBatch]:
        stmt = scope_stmt(select(ApplicationBatch), ApplicationBatch, self._tenant_id).where(
            ApplicationBatch.status.in_([BatchStatus.RUNNING, BatchStatus.SCHEDULED])
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())


class BatchItemRepository(Repository[BatchItem]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, BatchItem)

    async def list_for_batch(self, batch_id: uuid.UUID) -> list[BatchItem]:
        stmt = (
            select(BatchItem)
            .where(BatchItem.batch_id == batch_id)
            .order_by(BatchItem.sort_order.asc(), BatchItem.created_at.asc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def next_pending(self, batch_id: uuid.UUID) -> BatchItem | None:
        stmt = (
            select(BatchItem)
            .where(
                BatchItem.batch_id == batch_id,
                BatchItem.status == BatchItemStatus.PENDING,
            )
            .order_by(BatchItem.sort_order.asc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_by_status(self, batch_id: uuid.UUID) -> dict[str, int]:
        stmt = (
            select(BatchItem.status, func.count())
            .where(BatchItem.batch_id == batch_id)
            .group_by(BatchItem.status)
        )
        rows = await self._session.execute(stmt)
        return {status.value: int(count) for status, count in rows.all()}
