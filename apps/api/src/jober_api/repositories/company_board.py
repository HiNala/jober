from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.company_board import CompanyBoard
from jober_api.repositories.base import Repository


class CompanyBoardRepository(Repository[CompanyBoard]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, CompanyBoard)

    async def find_by_company_board(self, company_board: str) -> CompanyBoard | None:
        stmt = select(CompanyBoard).where(CompanyBoard.company_board == company_board)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
