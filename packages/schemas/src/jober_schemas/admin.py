from __future__ import annotations

from pydantic import BaseModel, Field


class AdminUserRead(BaseModel):
    id: str
    email: str
    display_name: str | None
    role: str
    status: str
    tenant_id: str
    plan: str
    last_login_at: str | None


class AdminUserListRead(BaseModel):
    items: list[AdminUserRead]


class AdminRoleUpdate(BaseModel):
    role: str = Field(pattern="^(user|admin)$")


class AdminStatusUpdate(BaseModel):
    status: str = Field(pattern="^(active|suspended)$")


class AdminAuditEntryRead(BaseModel):
    id: str
    actor_user_id: str
    target_user_id: str | None
    action: str
    resource_type: str | None
    resource_id: str | None
    message: str
    created_at: str


class AdminAuditListRead(BaseModel):
    items: list[AdminAuditEntryRead]
