from __future__ import annotations

import uuid
from copy import deepcopy

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.user_preferences import UserPreferences
from jober_api.repositories.base import Repository
from jober_api.services.preferences.defaults import DEFAULT_USER_PREFERENCES


class UserPreferencesRepository(Repository[UserPreferences]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UserPreferences)

    async def get_for_user(self, user_id: uuid.UUID) -> UserPreferences | None:
        stmt = select(UserPreferences).where(UserPreferences.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create(self, user_id: uuid.UUID) -> UserPreferences:
        row = await self.get_for_user(user_id)
        if row is not None:
            return row
        row = UserPreferences(user_id=user_id, prefs=deepcopy(DEFAULT_USER_PREFERENCES))
        self._session.add(row)
        await self._session.flush()
        return row
