from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.auth.oauth.pkce import code_challenge, generate_code_verifier, generate_state
from jober_api.auth.oauth.registry import get_oauth_provider
from jober_api.auth.oauth.state_store import (
    PendingOAuthLink,
    StoredOAuthState,
    delete_pending_link,
    fetch_pending_link,
    new_link_token,
    save_oauth_state,
    save_pending_link,
)
from jober_api.auth.oauth.types import OAuthIntent, OAuthProfile, OAuthStart
from jober_api.auth.password import verify_password
from jober_api.models.auth_identity import AuthIdentity
from jober_api.models.enums import AuthProvider, PlanTier, UserRole, UserStatus
from jober_api.models.tenant import Tenant
from jober_api.models.user import User
from jober_api.services.analytics.collector import emit_server_event
from jober_api.services.analytics.rollups import server_session_id
from jober_api.repositories.auth_identity import AuthIdentityRepository
from jober_api.schemas.auth import AuthIdentityResponse, AuthUserResponse
from jober_api.services.auth.service import user_to_response


async def start_oauth_flow(
    provider: AuthProvider,
    *,
    intent: OAuthIntent,
    link_user_id: uuid.UUID | None = None,
    next_path: str = "/dashboard",
) -> OAuthStart:
    client = get_oauth_provider(provider)
    state = generate_state()
    verifier = generate_code_verifier()
    await save_oauth_state(
        state,
        StoredOAuthState(
            code_verifier=verifier,
            intent=intent,
            link_user_id=str(link_user_id) if link_user_id else None,
            next_path=next_path,
        ),
    )
    url = client.authorization_url(state=state, code_challenge=code_challenge(verifier))
    return OAuthStart(authorization_url=url, state=state)


async def complete_oauth_callback(
    session: AsyncSession,
    provider: AuthProvider,
    *,
    code: str,
    stored: StoredOAuthState,
) -> tuple[AuthUserResponse | None, str, str | None]:
    """Return signed-in user, redirect path, and optional pending link token."""
    client = get_oauth_provider(provider)
    profile = await client.exchange_code(code=code, code_verifier=stored.code_verifier)

    if stored.intent == OAuthIntent.LINK:
        if stored.link_user_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid link state",
            )
        user_id = uuid.UUID(stored.link_user_id)
        user = await session.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        await _attach_identity(session, user, provider, profile)
        await session.commit()
        tenant = await session.get(Tenant, user.tenant_id)
        if tenant is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tenant not found")
        return user_to_response(user, tenant), stored.next_path, None

    return await _sign_in_with_profile(session, provider, profile, stored.next_path)


async def confirm_oauth_link(
    session: AsyncSession,
    *,
    link_token: str,
    password: str,
) -> AuthUserResponse:
    pending = await fetch_pending_link(link_token)
    if pending is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired link token",
        )

    user = await session.get(User, uuid.UUID(pending.existing_user_id))
    if user is None or not user.password_hash or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password confirmation failed",
        )

    await delete_pending_link(link_token)

    provider = AuthProvider(pending.provider)
    profile = OAuthProfile(
        provider_user_id=pending.provider_user_id,
        email=pending.provider_email,
        email_verified=True,
        display_name=pending.display_name,
        avatar_url=pending.avatar_url,
    )
    await _attach_identity(session, user, provider, profile)
    user.last_login_at = datetime.now(UTC)
    await session.commit()
    tenant = await session.get(Tenant, user.tenant_id)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tenant not found")
    return user_to_response(user, tenant)


async def list_identities(session: AsyncSession, user_id: uuid.UUID) -> list[AuthIdentityResponse]:
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    repo = AuthIdentityRepository(session)
    rows = await repo.list_for_user(user_id)
    items = [
        AuthIdentityResponse(
            provider=row.provider.value,
            provider_email=row.provider_email,
            display_name=row.display_name,
            linked_at=row.created_at,
        )
        for row in rows
    ]
    if user.password_hash:
        items.insert(
            0,
            AuthIdentityResponse(
                provider="native",
                provider_email=user.email,
                display_name=user.display_name,
                linked_at=user.created_at,
            ),
        )
    return items


async def unlink_provider(
    session: AsyncSession,
    user_id: uuid.UUID,
    provider: AuthProvider,
) -> None:
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    repo = AuthIdentityRepository(session)
    identities = await repo.list_for_user(user_id)
    has_password = bool(user.password_hash)
    if not has_password and len(identities) <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot unlink your only sign-in method",
        )

    removed = await repo.delete_for_user_provider(user_id, provider)
    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not linked")
    await session.commit()


async def _sign_in_with_profile(
    session: AsyncSession,
    provider: AuthProvider,
    profile: OAuthProfile,
    next_path: str,
) -> tuple[AuthUserResponse | None, str, str | None]:
    repo = AuthIdentityRepository(session)
    existing_identity = await repo.find_by_provider_subject(provider, profile.provider_user_id)
    if existing_identity is not None:
        user = await session.get(User, existing_identity.user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        await _refresh_identity_fields(existing_identity, profile)
        user.last_login_at = datetime.now(UTC)
        await session.commit()
        tenant = await session.get(Tenant, user.tenant_id)
        if tenant is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tenant not found")
        return user_to_response(user, tenant), next_path, None

    if not profile.email_verified or not profile.email:
        user, tenant = await _create_oauth_user(session, provider, profile)
        return user_to_response(user, tenant), next_path, None

    stmt = select(User).where(User.email == profile.email.lower())
    matched = (await session.execute(stmt)).scalar_one_or_none()
    if matched is not None and matched.email_verified_at is not None:
        token = new_link_token()
        await save_pending_link(
            token,
            PendingOAuthLink(
                provider=provider.value,
                provider_user_id=profile.provider_user_id,
                provider_email=profile.email,
                display_name=profile.display_name,
                avatar_url=profile.avatar_url,
                existing_user_id=str(matched.id),
            ),
        )
        return None, f"/link-google?token={token}", token

    user, tenant = await _create_oauth_user(session, provider, profile)
    return user_to_response(user, tenant), next_path, None


async def _resolve_oauth_email(
    session: AsyncSession,
    provider: AuthProvider,
    profile: OAuthProfile,
) -> str:
    """Pick a unique login email; unverified Google emails never claim an existing address."""
    preferred = (profile.email or f"{profile.provider_user_id}@{provider.value}.oauth").lower()
    if profile.email_verified:
        return preferred
    taken = (
        await session.execute(select(User.id).where(User.email == preferred).limit(1))
    ).scalar_one_or_none()
    if taken is None:
        return preferred
    return f"{profile.provider_user_id}@{provider.value}.oauth"


async def _create_oauth_user(
    session: AsyncSession,
    provider: AuthProvider,
    profile: OAuthProfile,
) -> tuple[User, Tenant]:
    email = await _resolve_oauth_email(session, provider, profile)
    existing = (await session.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    tenant = Tenant(
        id=uuid.uuid4(),
        name=profile.display_name or email.split("@")[0],
        plan=PlanTier.FREE,
        policy={"default_run_policy": "review_before_submit", "auto_submit_opt_in": False},
    )
    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        email=email,
        display_name=profile.display_name,
        password_hash=None,
        email_verified_at=datetime.now(UTC) if profile.email_verified else None,
        status=UserStatus.ACTIVE if profile.email_verified else UserStatus.PENDING_VERIFICATION,
        role=UserRole.USER,
        last_login_at=datetime.now(UTC),
    )
    session.add(tenant)
    session.add(user)
    await session.flush()
    await _attach_identity(session, user, provider, profile)
    await emit_server_event(
        session,
        name="signup.complete",
        session_id=server_session_id(user_id=user.id),
        user_id=user.id,
        tenant_id=tenant.id,
        props={"method": "oauth"},
    )
    await session.commit()
    await session.refresh(user)
    await session.refresh(tenant)
    return user, tenant


async def _attach_identity(
    session: AsyncSession,
    user: User,
    provider: AuthProvider,
    profile: OAuthProfile,
) -> AuthIdentity:
    repo = AuthIdentityRepository(session)
    existing = await repo.find_by_provider_subject(provider, profile.provider_user_id)
    if existing is not None and existing.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This provider account is linked to another user",
        )
    if existing is not None:
        await _refresh_identity_fields(existing, profile)
        return existing

    row = AuthIdentity(
        id=uuid.uuid4(),
        user_id=user.id,
        provider=provider,
        provider_user_id=profile.provider_user_id,
        provider_email=profile.email,
        display_name=profile.display_name,
        avatar_url=profile.avatar_url,
    )
    session.add(row)
    await session.flush()
    return row


async def _refresh_identity_fields(identity: AuthIdentity, profile: OAuthProfile) -> None:
    identity.provider_email = profile.email
    identity.display_name = profile.display_name
    identity.avatar_url = profile.avatar_url
