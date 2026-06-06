from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.cover_letter_angle import CoverLetterAngle
from jober_api.repositories.base import Repository


class CoverLetterAngleRepository(Repository[CoverLetterAngle]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, CoverLetterAngle)

    async def find_by_use_case(self, use_case: str) -> CoverLetterAngle | None:
        stmt = select(CoverLetterAngle).where(CoverLetterAngle.use_case == use_case)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
