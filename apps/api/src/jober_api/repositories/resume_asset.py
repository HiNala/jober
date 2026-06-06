from sqlalchemy import select
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
