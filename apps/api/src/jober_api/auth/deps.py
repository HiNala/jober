from __future__ import annotations

import uuid

import jwt
from fastapi import HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.auth.constants import DEFAULT_DEV_TENANT_ID, DEFAULT_DEV_USER_ID
from jober_api.auth.context import AuthContext
from jober_api.config import settings
from jober_api.models.tenant import Tenant
from jober_api.models.user import User

PUBLIC_API_PREFIXES = (
    "/api/webhooks/",
    "/api/health",
)


async def get_auth_context(
    request: Request,
    session: AsyncSession,
) -> AuthContext:
    if settings.auth_mode == "clerk" and settings.clerk_jwt_issuer:
        return await _auth_from_clerk_jwt(request, session)
    return await _auth_from_dev_headers(request, session)


async def _auth_from_dev_headers(request: Request, session: AsyncSession) -> AuthContext:
    tenant_raw = request.headers.get("X-Jober-Tenant-Id") or str(DEFAULT_DEV_TENANT_ID)
    user_raw = request.headers.get("X-Jober-User-Id") or str(DEFAULT_DEV_USER_ID)
    try:
        tenant_id = uuid.UUID(tenant_raw)
        user_id = uuid.UUID(user_raw)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid tenant or user id header",
        ) from exc

    user = await session.get(User, user_id)
    if user is None or user.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown user")
    tenant = await session.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown tenant")
    return AuthContext(
        user_id=user.id,
        tenant_id=tenant.id,
        email=user.email,
        plan=tenant.plan,
    )


async def _auth_from_clerk_jwt(request: Request, session: AsyncSession) -> AuthContext:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = auth_header.removeprefix("Bearer ").strip()
    try:
        payload = jwt.decode(
            token,
            settings.clerk_jwt_secret or settings.secret_key,
            algorithms=["HS256", "RS256"],
            issuer=settings.clerk_jwt_issuer,
            options={"verify_aud": False},
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid auth token",
        ) from exc

    clerk_user_id = str(payload.get("sub", ""))
    email = str(payload.get("email") or payload.get("primary_email") or "")
    if not clerk_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
        )

    stmt = select(User).where(User.clerk_user_id == clerk_user_id)
    user = (await session.execute(stmt)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not provisioned")
    tenant = await session.get(Tenant, user.tenant_id)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tenant missing")
    return AuthContext(
        user_id=user.id,
        tenant_id=tenant.id,
        email=user.email or email,
        plan=tenant.plan,
    )
