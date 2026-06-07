import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.user_profile import UserProfile
from jober_api.repositories.base import Repository
from jober_api.repositories.tenant_scope import scope_stmt


class UserProfileRepository(Repository[UserProfile]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None = None) -> None:
        super().__init__(session, UserProfile)
        self._tenant_id = tenant_id

    async def get_for_tenant(self) -> UserProfile | None:
        stmt = (
            scope_stmt(select(UserProfile), UserProfile, self._tenant_id)
            .order_by(UserProfile.created_at.asc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create_for_tenant(self) -> UserProfile:
        profile = await self.get_for_tenant()
        if profile is not None:
            return profile
        fields: dict[str, object] = {}
        if self._tenant_id is not None:
            fields["tenant_id"] = self._tenant_id
        return await self.create(**fields)

    async def get_singleton(self) -> UserProfile | None:
        return await self.get_for_tenant()

    async def get_or_create_singleton(self) -> UserProfile:
        return await self.get_or_create_for_tenant()

    async def update_fields(self, profile: UserProfile, **fields: object) -> UserProfile:
        for key, value in fields.items():
            setattr(profile, key, value)
        await self._session.flush()
        await self._session.refresh(profile)
        return profile
