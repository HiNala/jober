from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.enums import PlanTier
from jober_api.services.billing.entitlements import entitlements_for
from jober_api.services.billing.usage import tenant_monthly_run_count


class EntitlementExceededError(ValueError):
    pass


async def assert_batch_entitlements(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    plan: PlanTier,
    batch_item_count: int,
) -> None:
    ents = entitlements_for(plan)
    if batch_item_count > ents.max_batch_items:
        msg = (
            f"Plan limit: batches may include at most {ents.max_batch_items} jobs "
            f"({plan.value} plan). Upgrade to Pro for larger batches."
        )
        raise EntitlementExceededError(msg)
    runs = await tenant_monthly_run_count(session, tenant_id)
    if runs + batch_item_count > ents.max_monthly_runs:
        msg = (
            f"Plan limit: {ents.max_monthly_runs} application runs per month "
            f"({plan.value} plan). {runs} already used this month."
        )
        raise EntitlementExceededError(msg)
