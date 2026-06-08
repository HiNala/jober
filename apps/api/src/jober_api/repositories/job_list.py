from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from jober_api.models.job_list import JobList, JobListItem
from jober_api.repositories.base import Repository
from jober_api.repositories.tenant_scope import belongs_to_tenant, scope_stmt


class JobListRepository(Repository[JobList]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None = None) -> None:
        super().__init__(session, JobList)
        self._tenant_id = tenant_id

    async def get(self, entity_id: uuid.UUID) -> JobList | None:
        stmt = (
            select(JobList)
            .where(JobList.id == entity_id)
            .options(selectinload(JobList.items).selectinload(JobListItem.job_target))
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        if not belongs_to_tenant(row, self._tenant_id):
            return None
        return row

    async def list_for_user(
        self,
        user_id: uuid.UUID,
        *,
        include_archived: bool = False,
    ) -> list[JobList]:
        stmt = (
            select(JobList)
            .where(JobList.user_id == user_id)
            .options(selectinload(JobList.items).selectinload(JobListItem.job_target))
            .order_by(JobList.updated_at.desc())
        )
        stmt = scope_stmt(stmt, JobList, self._tenant_id)
        if not include_archived:
            stmt = stmt.where(JobList.archived.is_(False))
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
