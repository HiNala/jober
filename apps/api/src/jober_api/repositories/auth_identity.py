from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.auth_identity import AuthIdentity
from jober_api.models.enums import AuthProvider
from jober_api.repositories.base import Repository


class AuthIdentityRepository(Repository[AuthIdentity]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, AuthIdentity)

    async def find_by_provider_subject(
        self,
        provider: AuthProvider,
        provider_user_id: str,
    ) -> AuthIdentity | None:
        stmt = select(AuthIdentity).where(
            AuthIdentity.provider == provider,
            AuthIdentity.provider_user_id == provider_user_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: uuid.UUID) -> list[AuthIdentity]:
        stmt = (
            select(AuthIdentity)
            .where(AuthIdentity.user_id == user_id)
            .order_by(AuthIdentity.created_at.asc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def delete_for_user_provider(
        self,
        user_id: uuid.UUID,
        provider: AuthProvider,
    ) -> bool:
        stmt = select(AuthIdentity).where(
            AuthIdentity.user_id == user_id,
            AuthIdentity.provider == provider,
        )
        row = (await self._session.execute(stmt)).scalar_one_or_none()
        if row is None:
            return False
        await self.delete(row)
        return True
