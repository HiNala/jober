from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.application_run import ApplicationRun
from jober_api.models.enums import RunStatus
from jober_api.repositories.base import Repository


class ApplicationRunRepository(Repository[ApplicationRun]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ApplicationRun)

    async def list_for_job(self, job_target_id: UUID) -> list[ApplicationRun]:
        stmt = (
            select(ApplicationRun)
            .where(ApplicationRun.job_target_id == job_target_id)
            .order_by(ApplicationRun.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_status(self, status: RunStatus, limit: int = 50) -> list[ApplicationRun]:
        stmt = (
            select(ApplicationRun)
            .where(ApplicationRun.status == status)
            .order_by(ApplicationRun.updated_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
