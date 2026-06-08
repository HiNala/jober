from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    display_name: str | None = Field(default=None, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=10, max_length=128)


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=10, max_length=128)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class VerifyEmailRequest(BaseModel):
    token: str


class AuthUserResponse(BaseModel):
    id: uuid.UUID
    email: str
    display_name: str | None
    tenant_id: uuid.UUID
    email_verified: bool
    status: str
    role: str
    plan: str
    last_login_at: datetime | None


class AuthMessageResponse(BaseModel):
    message: str


class SessionListResponse(BaseModel):
    active_sessions: int
    session_ids: list[str]


class TotpSetupResponse(BaseModel):
    enabled: bool
    message: str
