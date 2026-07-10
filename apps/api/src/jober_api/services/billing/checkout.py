from __future__ import annotations

import uuid
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.config import settings
from jober_api.models.enums import PlanTier
from jober_api.models.tenant import Tenant
from jober_api.models.user import User


def stripe_enabled() -> bool:
    """True when Checkout can be started (secret key + Pro price configured)."""
    return bool(settings.stripe_secret_key.strip() and settings.stripe_price_pro_monthly.strip())


def _require_stripe() -> None:
    if not settings.stripe_secret_key.strip():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe billing is not configured",
        )
    if not settings.stripe_price_pro_monthly.strip():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe Pro price is not configured",
        )


def _stripe_client() -> Any:
    import stripe

    stripe.api_key = settings.stripe_secret_key
    return stripe


async def ensure_stripe_customer(
    session: AsyncSession,
    *,
    tenant: Tenant,
    user_email: str | None,
) -> str:
    if tenant.stripe_customer_id:
        return tenant.stripe_customer_id

    stripe = _stripe_client()
    customer = stripe.Customer.create(
        email=user_email or None,
        name=tenant.name,
        metadata={"tenant_id": str(tenant.id)},
    )
    customer_id = str(customer["id"] if isinstance(customer, dict) else customer.id)
    tenant.stripe_customer_id = customer_id
    await session.flush()
    return customer_id


async def create_checkout_session(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    success_url: str,
    cancel_url: str,
) -> dict[str, str]:
    _require_stripe()
    tenant = await session.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")

    user = await session.get(User, user_id)
    email = user.email if user is not None else None
    customer_id = await ensure_stripe_customer(session, tenant=tenant, user_email=email)

    stripe = _stripe_client()
    checkout = stripe.checkout.Session.create(
        mode="subscription",
        customer=customer_id,
        line_items=[{"price": settings.stripe_price_pro_monthly, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        client_reference_id=str(tenant_id),
        metadata={"tenant_id": str(tenant_id), "user_id": str(user_id)},
        subscription_data={"metadata": {"tenant_id": str(tenant_id)}},
        allow_promotion_codes=True,
    )
    url = checkout.get("url") if isinstance(checkout, dict) else getattr(checkout, "url", None)
    if not url:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Stripe did not return a checkout URL",
        )
    return {"url": str(url)}


async def create_portal_session(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    return_url: str,
) -> dict[str, str]:
    _require_stripe()
    tenant = await session.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    if not tenant.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No billing customer on file — upgrade first",
        )

    stripe = _stripe_client()
    portal = stripe.billing_portal.Session.create(
        customer=tenant.stripe_customer_id,
        return_url=return_url,
    )
    url = portal.get("url") if isinstance(portal, dict) else getattr(portal, "url", None)
    if not url:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Stripe did not return a portal URL",
        )
    return {"url": str(url)}


async def billing_status(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    plan: PlanTier,
) -> dict[str, Any]:
    tenant = await session.get(Tenant, tenant_id)
    return {
        "stripe_enabled": stripe_enabled(),
        "plan": plan.value if tenant is None else tenant.plan.value,
        "has_stripe_customer": bool(tenant and tenant.stripe_customer_id),
        "subscription_ends_at": (
            tenant.subscription_ends_at.isoformat()
            if tenant and tenant.subscription_ends_at
            else None
        ),
    }
