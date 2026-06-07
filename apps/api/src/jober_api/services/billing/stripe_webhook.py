from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.enums import AuditAction, PlanTier
from jober_api.models.tenant import Tenant
from jober_api.services.audit.service import record_audit


async def apply_stripe_event(session: AsyncSession, event: dict[str, Any]) -> dict[str, str]:
    event_type = str(event.get("type", ""))
    data_object = (event.get("data") or {}).get("object") or {}

    if event_type == "customer.subscription.updated":
        return await _subscription_updated(session, data_object)
    if event_type == "customer.subscription.deleted":
        return await _subscription_deleted(session, data_object)
    if event_type == "checkout.session.completed":
        return await _checkout_completed(session, data_object)
    return {"status": "ignored", "type": event_type}


async def _tenant_by_stripe_customer(session: AsyncSession, customer_id: str) -> Tenant | None:
    stmt = select(Tenant).where(Tenant.stripe_customer_id == customer_id)
    return (await session.execute(stmt)).scalar_one_or_none()


async def _subscription_updated(session: AsyncSession, sub: dict[str, Any]) -> dict[str, str]:
    customer_id = str(sub.get("customer", ""))
    tenant = await _tenant_by_stripe_customer(session, customer_id)
    if tenant is None:
        return {"status": "tenant_not_found"}
    status = str(sub.get("status", ""))
    tenant.stripe_subscription_id = str(sub.get("id", ""))
    if status in ("active", "trialing"):
        tenant.plan = PlanTier.PRO
    elif status in ("canceled", "unpaid", "past_due"):
        tenant.plan = PlanTier.FREE
    period_end = sub.get("current_period_end")
    if period_end:
        tenant.subscription_ends_at = datetime.fromtimestamp(int(period_end), tz=UTC)
    await record_audit(
        session,
        tenant_id=tenant.id,
        user_id=None,
        action=AuditAction.SUBSCRIPTION_CHANGED,
        message=f"Stripe subscription {status}",
        details={"subscription_id": tenant.stripe_subscription_id, "plan": tenant.plan.value},
    )
    await session.flush()
    return {"status": "updated", "plan": tenant.plan.value}


async def _subscription_deleted(session: AsyncSession, sub: dict[str, Any]) -> dict[str, str]:
    customer_id = str(sub.get("customer", ""))
    tenant = await _tenant_by_stripe_customer(session, customer_id)
    if tenant is None:
        return {"status": "tenant_not_found"}
    tenant.plan = PlanTier.FREE
    tenant.stripe_subscription_id = None
    await record_audit(
        session,
        tenant_id=tenant.id,
        user_id=None,
        action=AuditAction.SUBSCRIPTION_CHANGED,
        message="Stripe subscription deleted — downgraded to free",
    )
    await session.flush()
    return {"status": "downgraded"}


async def _checkout_completed(session: AsyncSession, checkout: dict[str, Any]) -> dict[str, str]:
    customer_id = str(checkout.get("customer", ""))
    tenant_raw = (checkout.get("metadata") or {}).get("tenant_id")
    if tenant_raw:
        tenant = await session.get(Tenant, uuid.UUID(str(tenant_raw)))
    else:
        tenant = await _tenant_by_stripe_customer(session, customer_id)
    if tenant is None:
        return {"status": "tenant_not_found"}
    tenant.stripe_customer_id = customer_id or tenant.stripe_customer_id
    tenant.plan = PlanTier.PRO
    await record_audit(
        session,
        tenant_id=tenant.id,
        user_id=None,
        action=AuditAction.SUBSCRIPTION_CHANGED,
        message="Checkout completed — upgraded to pro",
    )
    await session.flush()
    return {"status": "upgraded", "plan": tenant.plan.value}
