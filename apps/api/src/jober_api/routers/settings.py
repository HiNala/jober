from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.auth.middleware import require_auth
from jober_api.db.session import get_session
from jober_api.models.enums import AuditAction, RunPolicy
from jober_api.models.tenant import Tenant
from jober_api.repositories.user_preferences import UserPreferencesRepository
from jober_api.repositories.user_provider_key import UserProviderKeyRepository
from jober_api.services.audit.service import record_audit
from jober_api.services.preferences.defaults import deep_merge, merged_preferences

router = APIRouter(prefix="/settings", tags=["settings"])

_ALLOWED_PROVIDERS = frozenset({"openai", "anthropic"})

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


@router.get("/preferences")
async def get_preferences(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    auth = require_auth(request)
    repo = UserPreferencesRepository(session)
    row = await repo.get_or_create(auth.user_id)
    return {"preferences": merged_preferences(row.prefs)}


@router.patch("/preferences")
async def patch_preferences(
    request: Request,
    body: dict[str, Any],
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    auth = require_auth(request)
    repo = UserPreferencesRepository(session)
    row = await repo.get_or_create(auth.user_id)
    row.prefs = deep_merge(merged_preferences(row.prefs), body)
    await record_audit(
        session,
        tenant_id=auth.tenant_id,
        user_id=auth.user_id,
        action=AuditAction.POLICY_UPDATE,
        message="User preferences updated",
        details={"keys": list(body.keys())},
    )
    await session.commit()
    return {"preferences": merged_preferences(row.prefs)}


class ProviderKeyUpdate(BaseModel):
    api_key: str = Field(..., min_length=8, max_length=512)


@router.get("/provider-keys")
async def list_provider_keys(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    auth = require_auth(request)
    repo = UserProviderKeyRepository(session)
    rows = await repo.list_for_user(auth.user_id)
    return {
        "items": [
            {
                "provider": row.provider,
                "configured": bool(row.encrypted_api_key),
                "key_hint": row.key_hint,
            }
            for row in rows
        ]
    }


@router.put("/provider-keys/{provider}")
async def upsert_provider_key(
    provider: str,
    request: Request,
    body: ProviderKeyUpdate,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    auth = require_auth(request)
    if provider not in _ALLOWED_PROVIDERS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported provider")
    repo = UserProviderKeyRepository(session)
    row = await repo.get_for_provider(auth.user_id, provider)
    hint = body.api_key[-4:] if len(body.api_key) >= 4 else "****"
    if row is None:
        from jober_api.models.user_provider_key import UserProviderKey

        row = UserProviderKey(
            user_id=auth.user_id,
            provider=provider,
            encrypted_api_key=body.api_key,
            key_hint=hint,
        )
        session.add(row)
    else:
        row.encrypted_api_key = body.api_key
        row.key_hint = hint
    await record_audit(
        session,
        tenant_id=auth.tenant_id,
        user_id=auth.user_id,
        action=AuditAction.POLICY_UPDATE,
        message=f"Provider key updated for {provider}",
        details={"provider": provider},
    )
    await session.commit()
    return {"provider": provider, "configured": True, "key_hint": hint}


@router.delete("/provider-keys/{provider}")
async def delete_provider_key(
    provider: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    auth = require_auth(request)
    repo = UserProviderKeyRepository(session)
    row = await repo.get_for_provider(auth.user_id, provider)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not configured")
    await session.delete(row)
    await session.commit()
    return {"status": "deleted"}
