from __future__ import annotations

from urllib.parse import urlencode

import httpx
from fastapi import HTTPException, status

from jober_api.auth.oauth.types import OAuthProfile
from jober_api.config import settings
from jober_api.models.enums import AuthProvider

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"
GOOGLE_SCOPES = ("openid", "email", "profile")


class GoogleOAuthProvider:
    provider = AuthProvider.GOOGLE

    def authorization_url(self, *, state: str, code_challenge: str) -> str:
        if not settings.google_client_id or not settings.google_redirect_uri:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google sign-in is not configured",
            )
        params = {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": " ".join(GOOGLE_SCOPES),
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "access_type": "online",
            "prompt": "select_account",
        }
        return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

    async def exchange_code(self, *, code: str, code_verifier: str) -> OAuthProfile:
        if not settings.google_client_id or not settings.google_client_secret:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google sign-in is not configured",
            )
        async with httpx.AsyncClient(timeout=15.0) as client:
            token_res = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "code": code,
                    "code_verifier": code_verifier,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.google_redirect_uri,
                },
                headers={"Accept": "application/json"},
            )
            if token_res.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Google authorization failed",
                )
            access_token = token_res.json().get("access_token")
            if not access_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Google authorization failed",
                )

            profile_res = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if profile_res.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not load Google profile",
                )
            data = profile_res.json()

        sub = str(data.get("sub") or "")
        if not sub:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google profile missing subject",
            )
        email = str(data.get("email")).lower() if data.get("email") else None
        return OAuthProfile(
            provider_user_id=sub,
            email=email,
            email_verified=bool(data.get("email_verified")),
            display_name=data.get("name"),
            avatar_url=data.get("picture"),
        )
