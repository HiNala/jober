from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.config import settings
from jober_api.db.session import get_session
from jober_api.models.processed_stripe_event import ProcessedStripeEvent
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
    if not settings.stripe_webhook_secret:
        if settings.jober_env == "production":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Stripe webhooks are not configured",
            )
        data = json.loads(payload)
    else:
        try:
            data = construct_stripe_event(payload, sig)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Stripe signature",
            ) from exc

    event_id = str(data.get("id", ""))
    if event_id:
        existing = (
            await session.execute(
                select(ProcessedStripeEvent).where(ProcessedStripeEvent.event_id == event_id)
            )
        ).scalar_one_or_none()
        if existing is not None:
            return {"status": "duplicate", "event_id": event_id}

    result = await apply_stripe_event(session, data)
    if event_id:
        session.add(
            ProcessedStripeEvent(
                event_id=event_id,
                event_type=str(data.get("type", "")),
                processed_at=datetime.now(UTC),
            )
        )
    await session.commit()
    return result
