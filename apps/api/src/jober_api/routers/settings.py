from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.auth.middleware import require_auth
from jober_api.db.session import get_session
from jober_api.models.enums import AuditAction, RunPolicy
from jober_api.models.tenant import Tenant
from jober_api.services.audit.service import record_audit

router = APIRouter(prefix="/settings", tags=["settings"])

_USAGE_GUIDANCE = {
    "apply_only_chosen_jobs": (
        "Only apply to jobs you explicitly select. Jober assists your applications — "
        "it does not spray applications without your direction."
    ),
    "respect_site_terms": "Follow each employer's and ATS provider's terms of service.",
    "no_captcha_bypass": (
        "CAPTCHA, login, and 2FA require your action. Jober will pause and hand off — "
        "never bypass security challenges."
    ),
    "sensitive_fields": (
        "EEO, veteran status, and similar fields require your explicit entry and consent."
    ),
    "auto_submit_disclosure": (
        "auto_submit is opt-in only. When enabled, Jober may click submit after you review "
        "the filled form — it does not hide automation from you or the employer."
    ),
}


class PolicyUpdate(BaseModel):
    default_run_policy: RunPolicy = RunPolicy.REVIEW_BEFORE_SUBMIT
    auto_submit_opt_in: bool = False
    retention_days: int | None = Field(default=None, ge=1, le=3650)


@router.get("/policy")
async def get_policy(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    auth = require_auth(request)
    tenant = await session.get(Tenant, auth.tenant_id)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    policy = tenant.policy or {}
    return {
        "plan": tenant.plan.value,
        "policy": {
            "default_run_policy": policy.get(
                "default_run_policy", RunPolicy.REVIEW_BEFORE_SUBMIT.value
            ),
            "auto_submit_opt_in": bool(policy.get("auto_submit_opt_in", False)),
            "retention_days": tenant.retention_days,
        },
        "usage_guidance": _USAGE_GUIDANCE,
    }


@router.put("/policy")
async def update_policy(
    request: Request,
    body: PolicyUpdate,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    auth = require_auth(request)
    tenant = await session.get(Tenant, auth.tenant_id)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    if body.auto_submit_opt_in and body.default_run_policy != RunPolicy.AUTO_SUBMIT:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="auto_submit_opt_in requires default_run_policy=auto_submit",
        )
    tenant.policy = {
        "default_run_policy": body.default_run_policy.value,
        "auto_submit_opt_in": body.auto_submit_opt_in,
    }
    tenant.retention_days = body.retention_days
    await record_audit(
        session,
        tenant_id=auth.tenant_id,
        user_id=auth.user_id,
        action=AuditAction.POLICY_UPDATE,
        message="Tenant policy updated",
        details=tenant.policy,
    )
    if body.auto_submit_opt_in:
        await record_audit(
            session,
            tenant_id=auth.tenant_id,
            user_id=auth.user_id,
            action=AuditAction.AUTO_SUBMIT_OPT_IN,
            message="User opted in to auto_submit policy",
        )
    await session.commit()
    return {"status": "updated", "policy": tenant.policy, "retention_days": tenant.retention_days}
