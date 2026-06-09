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
    created_at: str | None = None


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


class AdminOverviewRead(BaseModel):
    as_of: str
    active_users: dict[str, object]
    signups: dict[str, int]
    runs: dict[str, object]
    submits_30d: int
    cost: dict[str, object]
    health: dict[str, object]
    attention: list[dict[str, str]]


class AdminRunsSummaryRead(BaseModel):
    range: dict[str, str]
    totals: dict[str, object]
    by_status: dict[str, int]
    failures_by_platform: list[dict[str, object]]
    attention: list[dict[str, str]]


class AdminAcquisitionRead(BaseModel):
    range: dict[str, str]
    signups: int
    funnel_signups: int
    funnel: dict[str, object]
    traffic: dict[str, object]
    utm_sources: list[dict[str, object]]
    geo: list[dict[str, object]]


class AdminSystemRead(BaseModel):
    health: dict[str, object]
    attention: list[dict[str, str]]


class AdminDataRequestEntryRead(BaseModel):
    id: str
    tenant_id: str
    user_id: str | None
    action: str
    message: str
    ts: str


class AdminDataRequestListRead(BaseModel):
    items: list[AdminDataRequestEntryRead]


class AdminUserOperationalRead(BaseModel):
    user: dict[str, object]
    tenant: dict[str, object]
    usage_30d: dict[str, object]
    data_requests: list[dict[str, object]]
    privacy_note: str


class AdminConfigEntryRead(BaseModel):
    key: str
    value: dict[str, object]
    updated_at: str | None


class AdminConfigListRead(BaseModel):
    items: list[AdminConfigEntryRead]


class AdminConfigUpdate(BaseModel):
    value: dict[str, object]
