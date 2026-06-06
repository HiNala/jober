import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.resume_asset import ResumeAsset
from jober_api.repositories.base import Repository


class ResumeAssetRepository(Repository[ResumeAsset]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ResumeAsset)

    async def list_active(self) -> list[ResumeAsset]:
        stmt = select(ResumeAsset).where(ResumeAsset.is_active.is_(True))
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_active(self) -> ResumeAsset | None:
        rows = await self.list_active()
        return rows[0] if rows else None

    async def deactivate_except(self, keep_id: uuid.UUID) -> None:
        stmt = update(ResumeAsset).where(ResumeAsset.id != keep_id).values(is_active=False)
        await self._session.execute(stmt)
        await self._session.flush()
