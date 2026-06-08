from __future__ import annotations

from fastapi import HTTPException, status

from jober_api.auth.oauth.base import OAuthProviderClient
from jober_api.auth.oauth.google import GoogleOAuthProvider
from jober_api.models.enums import AuthProvider

_PROVIDERS: dict[AuthProvider, OAuthProviderClient] = {
    AuthProvider.GOOGLE: GoogleOAuthProvider(),
}


def get_oauth_provider(provider: AuthProvider) -> OAuthProviderClient:
    client = _PROVIDERS.get(provider)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OAuth provider '{provider.value}' is not supported",
        )
    return client
