import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.enums import JobTargetStatus
from jober_api.models.job_target import JobTarget
from jober_api.repositories.base import Repository


class JobTargetRepository(Repository[JobTarget]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, JobTarget)

    async def find_by_upsert_key(
        self,
        company: str,
        role: str,
        direct_apply_url: str | None,
    ) -> JobTarget | None:
        if direct_apply_url:
            stmt = select(JobTarget).where(
                JobTarget.company == company,
                JobTarget.role == role,
                JobTarget.direct_apply_url == direct_apply_url,
            )
        else:
            stmt = select(JobTarget).where(
                JobTarget.company == company,
                JobTarget.role == role,
                or_(JobTarget.direct_apply_url.is_(None), JobTarget.direct_apply_url == ""),
            )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_filtered(
        self,
        *,
        status: JobTargetStatus | None = None,
        priority: str | None = None,
        company: str | None = None,
        role: str | None = None,
        location: str | None = None,
        limit: int = 500,
        offset: int = 0,
    ) -> list[JobTarget]:
        stmt = select(JobTarget)
        if status is not None:
            stmt = stmt.where(JobTarget.status == status)
        if priority:
            stmt = stmt.where(JobTarget.priority == priority)
        if company:
            stmt = stmt.where(JobTarget.company.ilike(f"%{company}%"))
        if role:
            stmt = stmt.where(JobTarget.role.ilike(f"%{role}%"))
        if location:
            stmt = stmt.where(JobTarget.location_work_style.ilike(f"%{location}%"))
        stmt = (
            stmt.order_by(JobTarget.rank.asc().nulls_last(), JobTarget.company.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update_fields(
        self,
        entity_id: uuid.UUID,
        **fields: object,
    ) -> JobTarget | None:
        instance = await self.get(entity_id)
        if instance is None:
            return None
        for key, value in fields.items():
            setattr(instance, key, value)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

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
