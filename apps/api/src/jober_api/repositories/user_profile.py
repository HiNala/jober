from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.user_profile import UserProfile
from jober_api.repositories.base import Repository


class UserProfileRepository(Repository[UserProfile]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UserProfile)
