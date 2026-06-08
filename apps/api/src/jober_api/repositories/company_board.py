from __future__ import annotations

import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.company_board import CompanyBoard
from jober_api.repositories.base import Repository
from jober_api.repositories.tenant_scope import scope_stmt


class CompanyBoardRepository(Repository[CompanyBoard]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None = None) -> None:
        super().__init__(session, CompanyBoard)
        self._tenant_id = tenant_id

    async def find_by_company_board(self, company_board: str) -> CompanyBoard | None:
        stmt = select(CompanyBoard).where(CompanyBoard.company_board == company_board)
        stmt = scope_stmt(stmt, CompanyBoard, self._tenant_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_filtered(
        self,
        *,
        role: str = "",
        stage: str = "",
        location: str = "",
        limit: int = 200,
    ) -> list[CompanyBoard]:
        stmt = scope_stmt(select(CompanyBoard), CompanyBoard, self._tenant_id)
        if role:
            pattern = f"%{role}%"
            stmt = stmt.where(
                or_(
                    CompanyBoard.company_board.ilike(pattern),
                    CompanyBoard.representative_roles.ilike(pattern),
                )
            )
        if stage:
            stmt = stmt.where(CompanyBoard.stage_signal.ilike(f"%{stage}%"))
        if location:
            stmt = stmt.where(CompanyBoard.notes.ilike(f"%{location}%"))
        stmt = stmt.order_by(CompanyBoard.company_board.asc()).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
