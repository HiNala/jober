from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.user_provider_key import UserProviderKey
from jober_api.repositories.base import Repository


class UserProviderKeyRepository(Repository[UserProviderKey]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UserProviderKey)

    async def list_for_user(self, user_id: uuid.UUID) -> list[UserProviderKey]:
        stmt = select(UserProviderKey).where(UserProviderKey.user_id == user_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_for_provider(self, user_id: uuid.UUID, provider: str) -> UserProviderKey | None:
        stmt = select(UserProviderKey).where(
            UserProviderKey.user_id == user_id,
            UserProviderKey.provider == provider,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
