from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.user_profile import UserProfile
from jober_api.repositories.base import Repository


class UserProfileRepository(Repository[UserProfile]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UserProfile)

    async def get_singleton(self) -> UserProfile | None:
        stmt = select(UserProfile).order_by(UserProfile.created_at.asc()).limit(1)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create_singleton(self) -> UserProfile:
        profile = await self.get_singleton()
        if profile is not None:
            return profile
        return await self.create()

    async def update_fields(self, profile: UserProfile, **fields: object) -> UserProfile:
        for key, value in fields.items():
            setattr(profile, key, value)
        await self._session.flush()
        await self._session.refresh(profile)
        return profile
