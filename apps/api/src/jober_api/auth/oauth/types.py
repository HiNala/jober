from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class OAuthIntent(StrEnum):
    SIGN_IN = "sign_in"
    LINK = "link"


@dataclass(frozen=True)
class OAuthProfile:
    provider_user_id: str
    email: str | None
    email_verified: bool
    display_name: str | None
    avatar_url: str | None


@dataclass(frozen=True)
class OAuthStart:
    authorization_url: str
    state: str
