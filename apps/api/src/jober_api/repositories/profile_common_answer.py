import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.profile_common_answer import ProfileCommonAnswer
from jober_api.repositories.base import Repository


class ProfileCommonAnswerRepository(Repository[ProfileCommonAnswer]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ProfileCommonAnswer)

    async def list_for_profile(self, profile_id: uuid.UUID) -> list[ProfileCommonAnswer]:
        stmt = (
            select(ProfileCommonAnswer)
            .where(ProfileCommonAnswer.user_profile_id == profile_id)
            .order_by(ProfileCommonAnswer.label.asc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def upsert(
        self,
        profile_id: uuid.UUID,
        answer_key: str,
        *,
        label: str,
        body: str,
    ) -> ProfileCommonAnswer:
        stmt = select(ProfileCommonAnswer).where(
            ProfileCommonAnswer.user_profile_id == profile_id,
            ProfileCommonAnswer.answer_key == answer_key,
        )
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing is None:
            return await self.create(
                user_profile_id=profile_id,
                answer_key=answer_key,
                label=label,
                body=body,
            )
        existing.label = label
        existing.body = body
        await self._session.flush()
        await self._session.refresh(existing)
        return existing
