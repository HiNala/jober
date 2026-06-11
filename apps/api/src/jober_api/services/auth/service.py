from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.auth.password import hash_password, password_needs_rehash, verify_password
from jober_api.auth.rate_limit import clear_failed_logins, is_locked_out, record_failed_login
from jober_api.auth.sessions import revoke_all_sessions
from jober_api.auth.token_hash import generate_opaque_token, hash_opaque_token
from jober_api.config import settings
from jober_api.models.auth_token import AuthToken
from jober_api.models.enums import AuthTokenType, PlanTier, UserRole, UserStatus
from jober_api.models.tenant import Tenant
from jober_api.models.user import User
from jober_api.schemas.auth import AuthUserResponse
from jober_api.services.analytics.collector import emit_server_event
from jober_api.services.analytics.rollups import server_session_id

GENERIC_AUTH_MESSAGE = "If an account exists for that email, we sent instructions."
INVALID_CREDENTIALS = "Invalid email or password"
INVALID_TOKEN = "Invalid or expired token"


def user_to_response(user: User, tenant: Tenant) -> AuthUserResponse:
    return AuthUserResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        tenant_id=user.tenant_id,
        email_verified=user.email_verified_at is not None,
        status=user.status.value if isinstance(user.status, UserStatus) else str(user.status),
        role=user.role.value if isinstance(user.role, UserRole) else str(user.role),
        plan=tenant.plan.value if isinstance(tenant.plan, PlanTier) else str(tenant.plan),
        last_login_at=user.last_login_at,
    )


async def register_user(
    session: AsyncSession,
    email: str,
    password: str,
    display_name: str | None,
) -> tuple[User, Tenant, str]:
    normalized = email.strip().lower()
    existing = (
        await session.execute(select(User).where(User.email == normalized))
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    tenant = Tenant(
        id=uuid.uuid4(),
        name=display_name or normalized.split("@")[0],
        plan=PlanTier.FREE,
        policy={"default_run_policy": "review_before_submit", "auto_submit_opt_in": False},
    )
    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        email=normalized,
        display_name=display_name,
        password_hash=hash_password(password),
        status=UserStatus.PENDING_VERIFICATION,
        role=UserRole.USER,
    )
    session.add(tenant)
    session.add(user)
    await session.flush()

    raw_token = await _create_auth_token(session, user.id, AuthTokenType.EMAIL_VERIFY, hours=24)
    await emit_server_event(
        session,
        name="signup.complete",
        session_id=server_session_id(user_id=user.id),
        user_id=user.id,
        tenant_id=tenant.id,
        props={"method": "password"},
    )
    await session.commit()
    await session.refresh(user)
    await session.refresh(tenant)
    return user, tenant, raw_token


async def authenticate_user(
    session: AsyncSession,
    email: str,
    password: str,
    client_ip: str,
) -> tuple[User, Tenant]:
    normalized = email.strip().lower()
    if await is_locked_out(normalized):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed attempts. Try again later.",
        )

    stmt = select(User).where(User.email == normalized)
    user = (await session.execute(stmt)).scalar_one_or_none()
    password_hash = user.password_hash if user is not None else None
    if user is None or not password_hash or not verify_password(password, password_hash):
        if user is not None:
            failures = await record_failed_login(normalized)
            if failures >= settings.auth_lockout_threshold:
                user.status = UserStatus.LOCKED
                await session.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS)

    if user.status == UserStatus.LOCKED:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account locked")

    if user.password_hash and password_needs_rehash(user.password_hash):
        user.password_hash = hash_password(password)

    await clear_failed_logins(normalized)
    user.last_login_at = datetime.now(UTC)
    tenant = await session.get(Tenant, user.tenant_id)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS)
    await session.commit()
    return user, tenant


async def verify_email_token(session: AsyncSession, raw_token: str) -> AuthUserResponse:
    user = await _consume_auth_token(session, raw_token, AuthTokenType.EMAIL_VERIFY)
    user.email_verified_at = datetime.now(UTC)
    if user.status == UserStatus.PENDING_VERIFICATION:
        user.status = UserStatus.ACTIVE
    tenant = await session.get(Tenant, user.tenant_id)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    await session.commit()
    return user_to_response(user, tenant)


async def resend_verification_email(session: AsyncSession, user_id: uuid.UUID) -> str | None:
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if user.email_verified_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified",
        )
    raw = await _create_auth_token(session, user.id, AuthTokenType.EMAIL_VERIFY, hours=24)
    await session.commit()
    return raw


async def request_password_reset(session: AsyncSession, email: str) -> str | None:
    normalized = email.strip().lower()
    stmt = select(User).where(User.email == normalized)
    user = (await session.execute(stmt)).scalar_one_or_none()
    if user is None:
        return None
    raw = await _create_auth_token(session, user.id, AuthTokenType.PASSWORD_RESET, hours=1)
    await session.commit()
    return raw


async def reset_password(session: AsyncSession, raw_token: str, new_password: str) -> None:
    user = await _consume_auth_token(session, raw_token, AuthTokenType.PASSWORD_RESET)
    user.password_hash = hash_password(new_password)
    if user.status == UserStatus.LOCKED:
        user.status = UserStatus.ACTIVE
    await clear_failed_logins(user.email)
    await revoke_all_sessions(user.id)
    await session.commit()


async def change_password(
    session: AsyncSession,
    user: User,
    current_password: str,
    new_password: str,
) -> None:
    if not user.password_hash or not verify_password(current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )
    user.password_hash = hash_password(new_password)
    await session.commit()


async def load_user_context(session: AsyncSession, user_id: uuid.UUID) -> AuthUserResponse:
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    tenant = await session.get(Tenant, user.tenant_id)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tenant not found")
    return user_to_response(user, tenant)


async def _create_auth_token(
    session: AsyncSession,
    user_id: uuid.UUID,
    token_type: AuthTokenType,
    *,
    hours: int,
) -> str:
    raw = generate_opaque_token()
    row = AuthToken(
        id=uuid.uuid4(),
        user_id=user_id,
        token_hash=hash_opaque_token(raw),
        token_type=token_type,
        expires_at=datetime.now(UTC) + timedelta(hours=hours),
    )
    session.add(row)
    return raw


async def _consume_auth_token(
    session: AsyncSession,
    raw_token: str,
    token_type: AuthTokenType,
) -> User:
    token_hash = hash_opaque_token(raw_token)
    stmt = select(AuthToken).where(
        AuthToken.token_hash == token_hash,
        AuthToken.token_type == token_type,
    )
    row = (await session.execute(stmt)).scalar_one_or_none()
    if row is None or row.used_at is not None or row.expires_at < datetime.now(UTC):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_TOKEN)
    row.used_at = datetime.now(UTC)
    user = await session.get(User, row.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_TOKEN)
    return user
