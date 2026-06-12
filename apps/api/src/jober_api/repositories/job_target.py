import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.enums import JobTargetStatus
from jober_api.models.job_target import JobTarget
from jober_api.repositories.base import Repository
from jober_api.repositories.tenant_scope import belongs_to_tenant, scope_stmt


class JobTargetRepository(Repository[JobTarget]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None = None) -> None:
        super().__init__(session, JobTarget)
        self._tenant_id = tenant_id

    async def get(self, entity_id: uuid.UUID) -> JobTarget | None:
        row = await super().get(entity_id)
        if not belongs_to_tenant(row, self._tenant_id):
            return None
        return row

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
        stmt = scope_stmt(stmt, JobTarget, self._tenant_id)
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
        stmt = scope_stmt(select(JobTarget), JobTarget, self._tenant_id)
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

    async def count_filtered(
        self,
        *,
        status: JobTargetStatus | None = None,
        priority: str | None = None,
        company: str | None = None,
        role: str | None = None,
        location: str | None = None,
        exclude_statuses: tuple[JobTargetStatus, ...] = (),
    ) -> int:
        stmt = select(func.count()).select_from(JobTarget)
        if self._tenant_id is not None:
            stmt = stmt.where(JobTarget.tenant_id == self._tenant_id)
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
        if exclude_statuses:
            stmt = stmt.where(JobTarget.status.notin_(exclude_statuses))
        result = await self._session.execute(stmt)
        return int(result.scalar_one())

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
            scope_stmt(
                select(JobTarget).where(JobTarget.status == status),
                JobTarget,
                self._tenant_id,
            )
            .order_by(JobTarget.rank.asc().nulls_last())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
