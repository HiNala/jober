from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, Request, status
from jober_schemas.enums import RunPolicy
from jober_schemas.verification import ReviewPackageRead, SubmitResultRead, VerifyReadyRead
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.auth.enforcement import RBACRouter
from jober_api.auth.middleware import require_auth
from jober_api.auth.permissions import Permission
from jober_api.auth.tenant_guard import require_job_for_tenant, require_run_for_tenant
from jober_api.db.session import get_session
from jober_api.errors import CODE_VERIFICATION_BLOCKED, error_detail
from jober_api.services.verification.service import (
    SubmitPolicyError,
    VerifyBlockedError,
    get_review_package,
    get_review_package_for_job,
    skip_submit,
    submit_application,
    verify_ready_from_fixture,
)

router = RBACRouter(permission=Permission.AUTHENTICATED, tags=["verification"])


@router.post("/job-targets/{job_target_id}/verify-ready", response_model=VerifyReadyRead)
async def verify_ready(
    request: Request,
    job_target_id: uuid.UUID,
    body: dict[str, object] | None = None,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    auth = require_auth(request)
    await require_job_for_tenant(session, auth.tenant_id, job_target_id)
    payload = body or {}
    fixture_html = payload.get("fixture_html")
    if not fixture_html:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="fixture_html is required",
        )

    policy_raw = payload.get("policy")
    policy = RunPolicy(str(policy_raw)) if policy_raw else RunPolicy.REVIEW_BEFORE_SUBMIT
    if policy == RunPolicy.AUTO_SUBMIT and not payload.get("auto_submit_opt_in"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="auto_submit requires explicit per-batch opt-in",
        )

    run_id_raw = payload.get("run_id")
    run_id = uuid.UUID(str(run_id_raw)) if run_id_raw else None
    auto_chain = bool(payload.get("auto_submit_after_verify"))
    refilled = bool(payload.get("refilled", True))

    try:
        result = await verify_ready_from_fixture(
            session,
            job_target_id=job_target_id,
            fixture_html=str(fixture_html),
            run_id=run_id,
            policy=policy,
            auto_submit_after_verify=auto_chain,
            refilled=refilled,
        )
        await session.commit()
        return result
    except VerifyBlockedError as exc:
        await session.commit()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_detail(
                "Readiness verification failed",
                code=CODE_VERIFICATION_BLOCKED,
                reason=exc.reason,
                run_id=str(exc.run_id),
                readiness=exc.readiness,
            ),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get("/job-targets/{job_target_id}/review", response_model=ReviewPackageRead)
async def review_package_for_job(
    request: Request,
    job_target_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    auth = require_auth(request)
    await require_job_for_tenant(session, auth.tenant_id, job_target_id)
    result = await get_review_package_for_job(session, job_target_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No run awaiting review for this job",
        )
    return result


@router.get("/application-runs/{run_id}/review", response_model=ReviewPackageRead)
async def review_package(
    request: Request,
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    auth = require_auth(request)
    await require_run_for_tenant(session, auth.tenant_id, run_id)
    try:
        result = await get_review_package(session, run_id)
        return result
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post("/application-runs/{run_id}/submit", response_model=SubmitResultRead)
async def submit_run(
    request: Request,
    run_id: uuid.UUID,
    body: dict[str, object] | None = None,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    auth = require_auth(request)
    await require_run_for_tenant(session, auth.tenant_id, run_id)
    payload = body or {}
    fixture_html = payload.get("fixture_html")
    try:
        result = await submit_application(
            session,
            run_id=run_id,
            fixture_html=str(fixture_html) if fixture_html else None,
            human_approved=True,
        )
        await session.commit()
        return result
    except SubmitPolicyError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.post("/application-runs/{run_id}/skip-submit")
async def skip_run_submit(
    request: Request,
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    auth = require_auth(request)
    await require_run_for_tenant(session, auth.tenant_id, run_id)
    try:
        result = await skip_submit(session, run_id)
        await session.commit()
        return result
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
