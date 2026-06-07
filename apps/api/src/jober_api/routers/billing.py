from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.auth.middleware import require_auth
from jober_api.db.session import get_session
from jober_api.services.billing.usage import usage_dashboard

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/usage")
async def get_usage(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    auth = require_auth(request)
    return await usage_dashboard(session, tenant_id=auth.tenant_id, plan=auth.plan)
