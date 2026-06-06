from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.enums import JobTargetStatus
from jober_api.models.job_target import JobTarget
from jober_api.repositories.base import Repository


class JobTargetRepository(Repository[JobTarget]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, JobTarget)

    async def list_by_status(
        self,
        status: JobTargetStatus,
        limit: int = 100,
    ) -> list[JobTarget]:
        stmt = (
            select(JobTarget)
            .where(JobTarget.status == status)
            .order_by(JobTarget.rank.asc().nulls_last())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
