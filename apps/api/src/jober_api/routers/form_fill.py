from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.auth.enforcement import RBACRouter
from jober_api.auth.middleware import require_auth
from jober_api.auth.permissions import Permission
from jober_api.auth.tenant_guard import require_job_for_tenant
from jober_api.db.session import get_session
from jober_api.services.form_fill.service import (
    FillBlockedError,
    enqueue_browser_fill,
    fill_from_fixture_html,
)

router = RBACRouter(permission=Permission.AUTHENTICATED, prefix="/job-targets", tags=["form-fill"])


@router.post("/{job_target_id}/fill-form")
async def fill_form(
    request: Request,
    job_target_id: uuid.UUID,
    body: dict[str, object] | None = None,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    auth = require_auth(request)
    await require_job_for_tenant(session, auth.tenant_id, job_target_id)
    payload = body or {}
    fixture_html = payload.get("fixture_html")

    try:
        if fixture_html:
            result = await fill_from_fixture_html(
                session,
                job_target_id=job_target_id,
                fixture_html=str(fixture_html),
            )
            try:
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            return result

        queued = await enqueue_browser_fill(session, job_target_id=job_target_id)
        await session.commit()
        return queued
    except FillBlockedError as exc:
        await session.commit()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Human checkpoint required",
                "gate": exc.gate,
                "run_id": str(exc.run_id),
            },
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
