from __future__ import annotations

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.auth.enforcement import RBACRouter
from jober_api.auth.middleware import require_auth
from jober_api.auth.permissions import Permission
from jober_api.db.session import get_session
from jober_api.services.onboarding.demo_workspace import DemoWorkspaceError, seed_demo_workspace

router = RBACRouter(
    permission=Permission.AUTHENTICATED,
    prefix="/onboarding",
    tags=["onboarding"],
)


@router.post("/demo-workspace")
async def create_demo_workspace(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, int]:
    """Load sanitized sample jobs and profile for evaluators / first-run exploration."""
    auth = require_auth(request)
    try:
        return await seed_demo_workspace(
            session,
            tenant_id=auth.tenant_id,
            user_id=auth.user_id,
        )
    except DemoWorkspaceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
