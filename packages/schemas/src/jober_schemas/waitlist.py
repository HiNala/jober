from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class ProWaitlistRequest(BaseModel):
    email: EmailStr
    consent_contact: bool = Field(
        ...,
        description="User consents to be contacted when Pro billing launches.",
    )
    source: str = Field(default="pricing", max_length=64)


class ProWaitlistResponse(BaseModel):
    status: Literal["created", "already_registered"]
