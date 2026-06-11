from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from jober_schemas.waitlist import ProWaitlistRequest, ProWaitlistResponse
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.auth.rate_limit import check_rate_limit
from jober_api.db.session import get_session
from jober_api.services.marketing.waitlist import register_pro_waitlist

router = APIRouter(prefix="/waitlist", tags=["waitlist"])


async def _require_rate_limit(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    if not await check_rate_limit(f"waitlist:{ip}"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Try again later.",
        )


@router.post("/pro", response_model=ProWaitlistResponse)
async def join_pro_waitlist(
    body: ProWaitlistRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(_require_rate_limit),
) -> ProWaitlistResponse:
    if not body.consent_contact:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Consent is required to join the Pro waitlist.",
        )
    status_value = await register_pro_waitlist(
        session,
        email=str(body.email),
        consent_contact=body.consent_contact,
        source=body.source,
    )
    return ProWaitlistResponse(status=status_value)
