import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.form_field_observation import FormFieldObservation
from jober_api.repositories.base import Repository


class FormFieldObservationRepository(Repository[FormFieldObservation]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, FormFieldObservation)

    async def list_for_attempt(self, attempt_id: uuid.UUID) -> list[FormFieldObservation]:
        stmt = (
            select(FormFieldObservation)
            .where(FormFieldObservation.attempt_id == attempt_id)
            .order_by(FormFieldObservation.field_key)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_for_job_latest(self, job_target_id: uuid.UUID) -> list[FormFieldObservation]:
        from jober_api.models.application_attempt import ApplicationAttempt
        from jober_api.models.application_run import ApplicationRun

        stmt = (
            select(FormFieldObservation)
            .join(ApplicationAttempt, FormFieldObservation.attempt_id == ApplicationAttempt.id)
            .join(ApplicationRun, ApplicationAttempt.run_id == ApplicationRun.id)
            .where(ApplicationRun.job_target_id == job_target_id)
            .order_by(ApplicationRun.created_at.desc(), FormFieldObservation.field_key)
        )
        result = await self._session.execute(stmt)
        rows = list(result.scalars().all())
        if not rows:
            return []
        latest_attempt = rows[0].attempt_id
        return [row for row in rows if row.attempt_id == latest_attempt]
