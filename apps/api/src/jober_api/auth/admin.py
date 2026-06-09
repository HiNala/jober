from __future__ import annotations

from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.auth.context import AuthContext
from jober_api.auth.middleware import require_auth
from jober_api.models.enums import UserRole
from jober_api.models.user import User


async def require_admin(request: Request, session: AsyncSession) -> AuthContext:
    auth = require_auth(request)
    user = await session.get(User, auth.user_id)
    if user is None or user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return auth
