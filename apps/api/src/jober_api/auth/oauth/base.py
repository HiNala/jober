from __future__ import annotations

from typing import Protocol

from jober_api.auth.oauth.types import OAuthProfile
from jober_api.models.enums import AuthProvider


class OAuthProviderClient(Protocol):
    provider: AuthProvider

    def authorization_url(self, *, state: str, code_challenge: str) -> str: ...

    async def exchange_code(self, *, code: str, code_verifier: str) -> OAuthProfile: ...
