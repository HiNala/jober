import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.resume_asset import ResumeAsset
from jober_api.repositories.base import Repository
from jober_api.repositories.tenant_scope import belongs_to_tenant, scope_stmt


class ResumeAssetRepository(Repository[ResumeAsset]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None = None) -> None:
        super().__init__(session, ResumeAsset)
        self._tenant_id = tenant_id

    async def get(self, entity_id: uuid.UUID) -> ResumeAsset | None:
        row = await super().get(entity_id)
        if not belongs_to_tenant(row, self._tenant_id):
            return None
        return row

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[ResumeAsset]:
        stmt = scope_stmt(select(ResumeAsset), ResumeAsset, self._tenant_id)
        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_active(self) -> list[ResumeAsset]:
        stmt = select(ResumeAsset).where(ResumeAsset.is_active.is_(True))
        stmt = scope_stmt(stmt, ResumeAsset, self._tenant_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_active(self) -> ResumeAsset | None:
        rows = await self.list_active()
        return rows[0] if rows else None

    async def deactivate_except(self, keep_id: uuid.UUID) -> None:
        stmt = update(ResumeAsset).where(ResumeAsset.id != keep_id).values(is_active=False)
        if self._tenant_id is not None:
            stmt = stmt.where(ResumeAsset.tenant_id == self._tenant_id)
        await self._session.execute(stmt)
        await self._session.flush()
