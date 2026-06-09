from __future__ import annotations

from datetime import date

from fastapi import Depends, Query, Request, Response
from jober_schemas.analytics_dashboard import FunnelDashboardRead, UserAnalyticsRead
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.auth.enforcement import RBACRouter, require_permission, requires
from jober_api.auth.middleware import require_auth
from jober_api.auth.permissions import Permission
from jober_api.db.session import get_session
from jober_api.services.analytics.dashboard import (
    get_admin_cost,
    get_admin_funnel,
    get_admin_traffic,
    get_user_analytics,
    rows_to_csv,
)

router = RBACRouter(
    prefix="/analytics", tags=["analytics-dashboard"], permission=Permission.AUTHENTICATED
)


def _parse_date(value: date | None) -> date | None:
    return value


@router.get("/me", response_model=UserAnalyticsRead)
@requires(Permission.AUTHENTICATED)
async def user_analytics(
    request: Request,
    session: AsyncSession = Depends(get_session),
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    compare_previous: bool = Query(default=False),
) -> dict[str, object]:
    auth = require_auth(request)
    return await get_user_analytics(
        session,
        tenant_id=auth.tenant_id,
        plan=auth.plan,
        start=_parse_date(start),
        end=_parse_date(end),
        compare_previous=compare_previous,
    )


@router.get("/me/export.csv")
@requires(Permission.AUTHENTICATED)
async def export_user_analytics_csv(
    request: Request,
    session: AsyncSession = Depends(get_session),
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
) -> Response:
    auth = require_auth(request)
    data = await get_user_analytics(
        session,
        tenant_id=auth.tenant_id,
        plan=auth.plan,
        start=_parse_date(start),
        end=_parse_date(end),
    )
    rows = [
        {"metric": "applications_sent", "value": data["summary"]["applications_sent"]},
        {"metric": "letters_generated", "value": data["summary"]["letters_generated"]},
        {"metric": "llm_cost_usd", "value": data["summary"]["llm_cost_usd"]},
        *[
            {"metric": f"runs_{row['day']}", "value": row["runs"]}
            for row in data.get("activity", [])
        ],
    ]
    body = rows_to_csv(rows)
    return Response(
        content=body,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=user-analytics.csv"},
    )


@router.get(
    "/admin/funnel",
    response_model=FunnelDashboardRead,
    dependencies=[Depends(require_permission(Permission.ADMIN_ANALYTICS_READ))],
)
@requires(Permission.ADMIN_ANALYTICS_READ)
async def admin_funnel(
    session: AsyncSession = Depends(get_session),
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    compare_previous: bool = Query(default=False),
) -> dict[str, object]:
    return await get_admin_funnel(
        session,
        start=_parse_date(start),
        end=_parse_date(end),
        compare_previous=compare_previous,
    )


@router.get(
    "/admin/funnel/export.csv",
    dependencies=[Depends(require_permission(Permission.ADMIN_ANALYTICS_READ))],
)
@requires(Permission.ADMIN_ANALYTICS_READ)
async def export_admin_funnel_csv(
    session: AsyncSession = Depends(get_session),
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
) -> Response:
    data = await get_admin_funnel(session, start=_parse_date(start), end=_parse_date(end))
    body = rows_to_csv(data["steps"])
    return Response(
        content=body,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=funnel.csv"},
    )


@router.get(
    "/admin/traffic",
    dependencies=[Depends(require_permission(Permission.ADMIN_ANALYTICS_READ))],
)
@requires(Permission.ADMIN_ANALYTICS_READ)
async def admin_traffic(
    session: AsyncSession = Depends(get_session),
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
) -> dict[str, object]:
    return await get_admin_traffic(session, start=_parse_date(start), end=_parse_date(end))


@router.get(
    "/admin/traffic/export.csv",
    dependencies=[Depends(require_permission(Permission.ADMIN_ANALYTICS_READ))],
)
@requires(Permission.ADMIN_ANALYTICS_READ)
async def export_admin_traffic_csv(
    session: AsyncSession = Depends(get_session),
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
) -> Response:
    data = await get_admin_traffic(session, start=_parse_date(start), end=_parse_date(end))
    body = rows_to_csv(data["pages"])
    return Response(
        content=body,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=traffic.csv"},
    )


@router.get(
    "/admin/cost",
    dependencies=[Depends(require_permission(Permission.ADMIN_ANALYTICS_READ))],
)
@requires(Permission.ADMIN_ANALYTICS_READ)
async def admin_cost(
    session: AsyncSession = Depends(get_session),
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
) -> dict[str, object]:
    return await get_admin_cost(session, start=_parse_date(start), end=_parse_date(end))


@router.get(
    "/admin/cost/export.csv",
    dependencies=[Depends(require_permission(Permission.ADMIN_ANALYTICS_READ))],
)
@requires(Permission.ADMIN_ANALYTICS_READ)
async def export_admin_cost_csv(
    session: AsyncSession = Depends(get_session),
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
) -> Response:
    data = await get_admin_cost(session, start=_parse_date(start), end=_parse_date(end))
    body = rows_to_csv(data["rows"])
    return Response(
        content=body,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=cost.csv"},
    )
