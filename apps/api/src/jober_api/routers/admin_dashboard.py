from __future__ import annotations

import uuid
from datetime import date, datetime

from fastapi import Depends, HTTPException, Query, Request, status
from jober_schemas.admin import (
    AdminAcquisitionRead,
    AdminConfigListRead,
    AdminConfigUpdate,
    AdminDataRequestListRead,
    AdminOverviewRead,
    AdminRunsSummaryRead,
    AdminSystemRead,
    AdminUserOperationalRead,
)
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.auth.enforcement import RBACRouter, requires
from jober_api.auth.middleware import require_auth
from jober_api.auth.permissions import Permission
from jober_api.db.session import get_session
from jober_api.services.admin.acquisition import get_admin_acquisition
from jober_api.services.admin.audit_list import list_data_requests
from jober_api.services.admin.config import list_product_config, set_config_value
from jober_api.services.admin.overview import get_admin_overview
from jober_api.services.admin.runs import get_admin_runs_summary
from jober_api.services.admin.support import get_user_operational_view
from jober_api.services.analytics.dashboard import get_admin_cost
from jober_api.services.ops.alerting import RUNBOOK_UPTIME, dispatch_ops_alerts, ops_attention

router = RBACRouter(prefix="/admin", tags=["admin-dashboard"], permission=Permission.ADMIN_OPS_READ)


@router.get("/overview", response_model=AdminOverviewRead)
@requires(Permission.ADMIN_OPS_READ)
async def admin_overview(session: AsyncSession = Depends(get_session)) -> dict[str, object]:
    return await get_admin_overview(session)


@router.get("/runs", response_model=AdminRunsSummaryRead)
@requires(Permission.ADMIN_OPS_READ)
async def admin_runs(
    session: AsyncSession = Depends(get_session),
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
) -> dict[str, object]:
    start_dt = datetime.combine(start, datetime.min.time()) if start else None
    end_dt = datetime.combine(end, datetime.min.time()) if end else None
    return await get_admin_runs_summary(session, start=start_dt, end=end_dt)


@router.get("/acquisition", response_model=AdminAcquisitionRead)
@requires(Permission.ADMIN_ANALYTICS_READ)
async def admin_acquisition(
    session: AsyncSession = Depends(get_session),
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
) -> dict[str, object]:
    start_dt = datetime.combine(start, datetime.min.time()) if start else None
    end_dt = datetime.combine(end, datetime.min.time()) if end else None
    return await get_admin_acquisition(session, start=start_dt, end=end_dt)


@router.get("/cost")
@requires(Permission.ADMIN_ANALYTICS_READ)
async def admin_cost_dashboard(
    session: AsyncSession = Depends(get_session),
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
) -> dict[str, object]:
    return await get_admin_cost(session, start=start, end=end)


@router.post("/ops/test-alert")
@requires(Permission.ADMIN_OPS_READ)
async def admin_test_alert() -> dict[str, bool]:
    """Fire a test webhook alert (verifies OPS_ALERT_WEBHOOK_URL wiring)."""
    sent = await dispatch_ops_alerts(
        "admin_test",
        [
            ops_attention(
                "warn",
                "Test alert from Jober admin (ops/test-alert).",
                runbook=RUNBOOK_UPTIME,
            )
        ],
        force=True,
    )
    return {"sent": sent}


@router.get("/system", response_model=AdminSystemRead)
@requires(Permission.ADMIN_OPS_READ)
async def admin_system(session: AsyncSession = Depends(get_session)) -> dict[str, object]:
    overview = await get_admin_overview(session)
    return {
        "health": overview["health"],
        "attention": overview["attention"],
    }


@router.get("/data-requests", response_model=AdminDataRequestListRead)
@requires(Permission.ADMIN_OPS_READ)
async def admin_data_requests(
    session: AsyncSession = Depends(get_session),
    limit: int = Query(default=50, ge=1, le=200),
) -> dict[str, object]:
    items = await list_data_requests(session, limit=limit)
    return {"items": items}


@router.get("/users/{user_id}/operational", response_model=AdminUserOperationalRead)
@requires(Permission.ADMIN_USERS_MANAGE)
async def admin_user_operational(
    user_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    auth = require_auth(request)
    try:
        payload = await get_user_operational_view(
            session,
            actor_user_id=auth.user_id,
            target_user_id=user_id,
        )
        await session.commit()
    except LookupError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        ) from None
    return payload


config_router = RBACRouter(
    prefix="/admin/config",
    tags=["admin-config"],
    permission=Permission.ADMIN_CONFIG_MANAGE,
)


@config_router.get("/", response_model=AdminConfigListRead)
@requires(Permission.ADMIN_CONFIG_MANAGE)
async def admin_list_config(session: AsyncSession = Depends(get_session)) -> dict[str, object]:
    items = await list_product_config(session)
    return {"items": items}


@config_router.patch("/{key}")
@requires(Permission.ADMIN_CONFIG_MANAGE)
async def admin_update_config(
    key: str,
    body: AdminConfigUpdate,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    auth = require_auth(request)
    row = await set_config_value(
        session,
        key=key,
        value=body.value,
        actor_user_id=auth.user_id,
    )
    await session.commit()
    return {
        "key": row.key,
        "value": row.value,
        "updated_at": row.updated_at.isoformat(),
    }
