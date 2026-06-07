import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.application_run import ApplicationRun
from jober_api.models.enums import CheckpointType, RunStatus
from jober_api.models.human_checkpoint import HumanCheckpoint
from jober_api.repositories.base import Repository
from jober_api.repositories.tenant_scope import belongs_to_tenant


class ApplicationRunRepository(Repository[ApplicationRun]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None = None) -> None:
        super().__init__(session, ApplicationRun)
        self._tenant_id = tenant_id

    async def create(self, **fields: object) -> ApplicationRun:
        if "tenant_id" not in fields and fields.get("job_target_id") is not None:
            from jober_api.models.job_target import JobTarget

            job = await self._session.get(JobTarget, fields["job_target_id"])
            if job is not None:
                fields = {**fields, "tenant_id": job.tenant_id}
        elif "tenant_id" not in fields and self._tenant_id is not None:
            fields = {**fields, "tenant_id": self._tenant_id}
        return await super().create(**fields)

    async def get(self, entity_id: uuid.UUID) -> ApplicationRun | None:
        row = await super().get(entity_id)
        if not belongs_to_tenant(row, self._tenant_id):
            return None
        return row

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

    async def update_fields(
        self,
        entity_id: uuid.UUID,
        **fields: object,
    ) -> ApplicationRun | None:
        instance = await self.get(entity_id)
        if instance is None:
            return None
        for key, value in fields.items():
            setattr(instance, key, value)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    async def create_checkpoint(
        self,
        run_id: uuid.UUID,
        *,
        checkpoint_type: CheckpointType,
        prompt: str,
        options: dict[str, object] | None = None,
    ) -> HumanCheckpoint:
        row = HumanCheckpoint(
            run_id=run_id,
            checkpoint_type=checkpoint_type,
            prompt=prompt,
            options=options,
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return row
