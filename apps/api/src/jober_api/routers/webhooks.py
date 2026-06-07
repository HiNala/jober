from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.config import settings
from jober_api.db.session import get_session
from jober_api.services.billing.stripe_verify import construct_stripe_event
from jober_api.services.billing.stripe_webhook import apply_stripe_event

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    payload = await request.body()
    sig = request.headers.get("Stripe-Signature", "")
    if settings.stripe_webhook_secret:
        try:
            data = construct_stripe_event(payload, sig)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Stripe signature",
            ) from exc
    else:
        data = json.loads(payload)

    result = await apply_stripe_event(session, data)
    await session.commit()
    return result
