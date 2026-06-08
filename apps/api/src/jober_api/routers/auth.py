from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.auth.cookies import clear_auth_cookies, set_auth_cookies
from jober_api.auth.csrf import verify_csrf
from jober_api.auth.middleware import require_auth
from jober_api.auth.oauth.state_store import consume_oauth_state
from jober_api.auth.oauth.types import OAuthIntent
from jober_api.auth.rate_limit import check_rate_limit
from jober_api.auth.sessions import (
    create_session,
    list_active_sessions,
    load_session,
    refresh_session,
    revoke_all_sessions,
    revoke_session,
)
from jober_api.config import settings
from jober_api.db.session import get_session
from jober_api.models.enums import AuthProvider
from jober_api.models.user import User
from jober_api.schemas.auth import (
    AuthMessageResponse,
    AuthUserResponse,
    ChangePasswordRequest,
    ConfirmOAuthLinkRequest,
    ForgotPasswordRequest,
    IdentityListResponse,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    SessionListResponse,
    TotpSetupResponse,
    VerifyEmailRequest,
)
from jober_api.services.auth import oauth_service
from jober_api.services.auth import service as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


async def _require_rate_limit(request: Request) -> None:
    ip = _client_ip(request)
    if not await check_rate_limit(f"{request.url.path}:{ip}"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests",
        )


async def _session_from_request(request: Request) -> tuple[str, str] | None:
    session_id = request.cookies.get(settings.session_cookie_name)
    if not session_id:
        return None
    data = await load_session(session_id)
    if data is None:
        return None
    return session_id, data.csrf_token


@router.post("/register", response_model=AuthUserResponse)
async def register(
    body: RegisterRequest,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(_require_rate_limit),
) -> AuthUserResponse:
    user, tenant, verify_token = await auth_service.register_user(
        session,
        body.email,
        body.password,
        body.display_name,
    )
    session_id, refresh_id, csrf = await create_session(user.id, tenant.id)
    set_auth_cookies(response, session_id, refresh_id, csrf)
    result = auth_service.user_to_response(user, tenant)
    if settings.jober_env == "development":
        response.headers["X-Jober-Verify-Token"] = verify_token
    return result


@router.post("/login", response_model=AuthUserResponse)
async def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(_require_rate_limit),
) -> AuthUserResponse:
    user, tenant = await auth_service.authenticate_user(
        session,
        body.email,
        body.password,
        _client_ip(request),
    )
    session_id, refresh_id, csrf = await create_session(user.id, tenant.id)
    set_auth_cookies(response, session_id, refresh_id, csrf)
    return auth_service.user_to_response(user, tenant)


@router.post("/logout", response_model=AuthMessageResponse)
async def logout(request: Request, response: Response) -> AuthMessageResponse:
    pair = await _session_from_request(request)
    if pair:
        verify_csrf(request, pair[1])
        await revoke_session(pair[0])
    clear_auth_cookies(response)
    return AuthMessageResponse(message="Signed out")


@router.post("/logout-all", response_model=AuthMessageResponse)
async def logout_all(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> AuthMessageResponse:
    auth = require_auth(request)
    pair = await _session_from_request(request)
    if pair:
        verify_csrf(request, pair[1])
    user = await session.get(User, auth.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    await revoke_all_sessions(auth.user_id)
    clear_auth_cookies(response)
    return AuthMessageResponse(message="Signed out everywhere")


@router.get("/me", response_model=AuthUserResponse)
async def me(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> AuthUserResponse:
    auth = require_auth(request)
    return await auth_service.load_user_context(session, auth.user_id)


@router.post("/refresh", response_model=AuthMessageResponse)
async def refresh(request: Request, response: Response) -> AuthMessageResponse:
    refresh_id = request.cookies.get(settings.refresh_cookie_name)
    if not refresh_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")
    rotated = await refresh_session(refresh_id)
    if rotated is None:
        clear_auth_cookies(response)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
    session_id, new_refresh, csrf = rotated
    set_auth_cookies(response, session_id, new_refresh, csrf)
    return AuthMessageResponse(message="Session refreshed")


@router.post("/verify-email", response_model=AuthUserResponse)
async def verify_email(
    body: VerifyEmailRequest,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(_require_rate_limit),
) -> AuthUserResponse:
    return await auth_service.verify_email_token(session, body.token)


@router.post("/forgot-password", response_model=AuthMessageResponse)
async def forgot_password(
    body: ForgotPasswordRequest,
    response: Response,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(_require_rate_limit),
) -> AuthMessageResponse:
    raw = await auth_service.request_password_reset(session, body.email)
    if raw and settings.jober_env == "development":
        response.headers["X-Jober-Reset-Token"] = raw
    return AuthMessageResponse(message=auth_service.GENERIC_AUTH_MESSAGE)


@router.post("/reset-password", response_model=AuthMessageResponse)
async def reset_password(
    body: ResetPasswordRequest,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(_require_rate_limit),
) -> AuthMessageResponse:
    await auth_service.reset_password(session, body.token, body.new_password)
    return AuthMessageResponse(message="Password updated")


@router.post("/change-password", response_model=AuthMessageResponse)
async def change_password(
    body: ChangePasswordRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> AuthMessageResponse:
    auth = require_auth(request)
    pair = await _session_from_request(request)
    if pair:
        verify_csrf(request, pair[1])
    user = await session.get(User, auth.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    await auth_service.change_password(session, user, body.current_password, body.new_password)
    return AuthMessageResponse(message="Password changed")


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(request: Request) -> SessionListResponse:
    auth = require_auth(request)
    ids = await list_active_sessions(auth.user_id)
    return SessionListResponse(active_sessions=len(ids), session_ids=ids)


@router.get("/totp/setup", response_model=TotpSetupResponse)
async def totp_setup() -> TotpSetupResponse:
    return TotpSetupResponse(
        enabled=False,
        message="TOTP 2FA scaffolding — enable in a future mission",
    )


def _web_redirect(path: str) -> str:
    base = settings.web_app_url.rstrip("/")
    if not path.startswith("/"):
        path = f"/{path}"
    return f"{base}{path}"


async def _issue_session(response: Response, user_id: uuid.UUID, tenant_id: uuid.UUID) -> None:
    session_id, refresh_id, csrf = await create_session(user_id, tenant_id)
    set_auth_cookies(response, session_id, refresh_id, csrf)


@router.get("/google/start")
async def google_oauth_start(
    request: Request,
    next_path: str = Query("/dashboard"),
    _: None = Depends(_require_rate_limit),
) -> RedirectResponse:
    start = await oauth_service.start_oauth_flow(
        AuthProvider.GOOGLE,
        intent=OAuthIntent.SIGN_IN,
        next_path=next_path,
    )
    return RedirectResponse(start.authorization_url, status_code=status.HTTP_302_FOUND)


@router.get("/google/link/start")
async def google_link_start(
    request: Request,
    next_path: str = Query("/settings"),
) -> RedirectResponse:
    auth = require_auth(request)
    start = await oauth_service.start_oauth_flow(
        AuthProvider.GOOGLE,
        intent=OAuthIntent.LINK,
        link_user_id=auth.user_id,
        next_path=next_path,
    )
    return RedirectResponse(start.authorization_url, status_code=status.HTTP_302_FOUND)


@router.get("/google/callback")
async def google_oauth_callback(
    code: str = Query(...),
    state: str = Query(...),
    session: AsyncSession = Depends(get_session),
) -> RedirectResponse:
    stored = await consume_oauth_state(state)
    if stored is None:
        return RedirectResponse(
            _web_redirect("/login?error=oauth_state"),
            status_code=status.HTTP_302_FOUND,
        )

    response = RedirectResponse(
        _web_redirect(stored.next_path),
        status_code=status.HTTP_302_FOUND,
    )
    try:
        user_response, redirect_path, _pending = await oauth_service.complete_oauth_callback(
            session,
            AuthProvider.GOOGLE,
            code=code,
            stored=stored,
        )
    except HTTPException as exc:
        detail = exc.detail if isinstance(exc.detail, str) else "oauth_failed"
        return RedirectResponse(
            _web_redirect(f"/login?error={detail}"),
            status_code=status.HTTP_302_FOUND,
        )

    if user_response is None:
        return RedirectResponse(_web_redirect(redirect_path), status_code=status.HTTP_302_FOUND)

    await _issue_session(response, user_response.id, user_response.tenant_id)
    response.headers["location"] = _web_redirect(redirect_path)
    return response


@router.post("/google/confirm-link", response_model=AuthUserResponse)
async def google_confirm_link(
    body: ConfirmOAuthLinkRequest,
    response: Response,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(_require_rate_limit),
) -> AuthUserResponse:
    user_response = await oauth_service.confirm_oauth_link(
        session,
        link_token=body.token,
        password=body.password,
    )
    await _issue_session(response, user_response.id, user_response.tenant_id)
    return user_response


@router.get("/identities", response_model=IdentityListResponse)
async def list_identities(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> IdentityListResponse:
    auth = require_auth(request)
    items = await oauth_service.list_identities(session, auth.user_id)
    return IdentityListResponse(items=items)


@router.delete("/identities/{provider}", response_model=AuthMessageResponse)
async def unlink_identity(
    provider: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> AuthMessageResponse:
    auth = require_auth(request)
    pair = await _session_from_request(request)
    if pair:
        verify_csrf(request, pair[1])
    if provider == "native":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Native password cannot be unlinked here",
        )
    try:
        provider_enum = AuthProvider(provider)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unknown provider",
        ) from exc
    await oauth_service.unlink_provider(session, auth.user_id, provider_enum)
    return AuthMessageResponse(message="Provider unlinked")
