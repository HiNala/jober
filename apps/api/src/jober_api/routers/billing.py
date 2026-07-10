from __future__ import annotations

from typing import Any

from fastapi import Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.auth.enforcement import RBACRouter
from jober_api.auth.middleware import require_auth
from jober_api.auth.permissions import Permission
from jober_api.db.session import get_session
from jober_api.services.billing.checkout import (
    billing_status,
    create_checkout_session,
    create_portal_session,
)
from jober_api.services.billing.usage import usage_dashboard

router = RBACRouter(permission=Permission.AUTHENTICATED, prefix="/billing", tags=["billing"])


class CheckoutSessionBody(BaseModel):
    success_url: str = Field(..., min_length=8, max_length=2048)
    cancel_url: str = Field(..., min_length=8, max_length=2048)


class PortalSessionBody(BaseModel):
    return_url: str = Field(..., min_length=8, max_length=2048)


@router.get("/usage")
async def get_usage(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    auth = require_auth(request)
    return await usage_dashboard(session, tenant_id=auth.tenant_id, plan=auth.plan)


@router.get("/status")
async def get_billing_status(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    auth = require_auth(request)
    return await billing_status(session, tenant_id=auth.tenant_id, plan=auth.plan)


@router.post("/checkout-session")
async def post_checkout_session(
    request: Request,
    body: CheckoutSessionBody,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    auth = require_auth(request)
    result = await create_checkout_session(
        session,
        tenant_id=auth.tenant_id,
        user_id=auth.user_id,
        success_url=body.success_url,
        cancel_url=body.cancel_url,
    )
    await session.commit()
    return result


@router.post("/portal-session")
async def post_portal_session(
    request: Request,
    body: PortalSessionBody,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    auth = require_auth(request)
    result = await create_portal_session(
        session,
        tenant_id=auth.tenant_id,
        return_url=body.return_url,
    )
    await session.commit()
    return result
