from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from jober_schemas.admin import (
    AdminAuditListRead,
    AdminRoleUpdate,
    AdminStatusUpdate,
    AdminUserListRead,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.auth.enforcement import RBACRouter, require_permission, requires
from jober_api.auth.middleware import require_auth
from jober_api.auth.permissions import Permission
from jober_api.db.session import get_session
from jober_api.models.admin_audit_log import AdminAuditLog
from jober_api.models.enum_utils import enum_value
from jober_api.models.enums import UserRole, UserStatus
from jober_api.services.admin.bootstrap import BootstrapError, promote_user_to_admin
from jober_api.services.admin.users import list_users_for_admin, set_user_status

router = RBACRouter(prefix="/admin", tags=["admin"], permission=Permission.ADMIN_USERS_MANAGE)


@router.get("/users", response_model=AdminUserListRead)
@requires(Permission.ADMIN_USERS_MANAGE)
async def admin_list_users(
    session: AsyncSession = Depends(get_session),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> dict[str, object]:
    items = await list_users_for_admin(session, limit=limit, offset=offset)
    return {"items": items}


@router.patch("/users/{user_id}/role")
@requires(Permission.ADMIN_USERS_MANAGE)
async def admin_update_role(
    user_id: uuid.UUID,
    body: AdminRoleUpdate,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    auth = require_auth(request)
    role = UserRole(body.role)
    try:
        user = await promote_user_to_admin(
            session,
            actor_user_id=auth.user_id,
            target_user_id=user_id,
            role=role,
        )
        await session.commit()
    except LookupError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        ) from None
    except BootstrapError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {"role": enum_value(user.role)}


@router.patch("/users/{user_id}/status")
@requires(Permission.ADMIN_USERS_MANAGE)
async def admin_update_status(
    user_id: uuid.UUID,
    body: AdminStatusUpdate,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    auth = require_auth(request)
    status_value = UserStatus.ACTIVE if body.status == "active" else UserStatus.SUSPENDED
    try:
        user = await set_user_status(
            session,
            actor_user_id=auth.user_id,
            target_user_id=user_id,
            status=status_value,
        )
        await session.commit()
    except LookupError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        ) from None
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {"status": enum_value(user.status)}


audit_router = APIRouter(prefix="/admin", tags=["admin"])


@audit_router.get(
    "/audit-log",
    response_model=AdminAuditListRead,
    dependencies=[Depends(require_permission(Permission.ADMIN_AUDIT_READ))],
)
@requires(Permission.ADMIN_AUDIT_READ)
async def admin_audit_log(
    session: AsyncSession = Depends(get_session),
    limit: int = Query(default=50, ge=1, le=200),
) -> dict[str, object]:
    stmt = select(AdminAuditLog).order_by(AdminAuditLog.created_at.desc()).limit(limit)
    rows = (await session.execute(stmt)).scalars().all()
    return {
        "items": [
            {
                "id": str(row.id),
                "actor_user_id": str(row.actor_user_id),
                "target_user_id": str(row.target_user_id) if row.target_user_id else None,
                "action": enum_value(row.action),
                "resource_type": row.resource_type,
                "resource_id": row.resource_id,
                "message": row.message,
                "created_at": row.created_at.isoformat(),
            }
            for row in rows
        ]
    }
