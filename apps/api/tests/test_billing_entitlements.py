from __future__ import annotations

import os

import pytest

from jober_api.auth.constants import DEFAULT_DEV_TENANT_ID
from jober_api.models.enums import JobTargetStatus, PlanTier
from jober_api.models.tenant import Tenant
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.services.batch.service import BatchValidationError, create_batch

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres",
)


@pytest.mark.asyncio
async def test_free_plan_blocks_oversized_batch(db_session, truncate_tables) -> None:
    tenant = await db_session.get(Tenant, DEFAULT_DEV_TENANT_ID)
    assert tenant is not None
    tenant.plan = PlanTier.FREE
    jobs = JobTargetRepository(db_session, DEFAULT_DEV_TENANT_ID)
    for index in range(6):
        await jobs.create(
            company=f"Co {index}",
            role="Eng",
            status=JobTargetStatus.NEW,
            priority="A",
            direct_apply_url=f"http://fixtures.local/apply/{index}",
        )
    await db_session.commit()

    with pytest.raises(BatchValidationError, match="at most 5"):
        await create_batch(
            db_session,
            tenant_id=DEFAULT_DEV_TENANT_ID,
            plan=PlanTier.FREE,
            name="Too big",
            policy="review_before_submit",
            filters={"priority": "A"},
        )


@pytest.mark.asyncio
async def test_pro_plan_allows_larger_batch(db_session, truncate_tables) -> None:
    tenant = await db_session.get(Tenant, DEFAULT_DEV_TENANT_ID)
    assert tenant is not None
    tenant.plan = PlanTier.PRO
    jobs = JobTargetRepository(db_session, DEFAULT_DEV_TENANT_ID)
    for index in range(6):
        await jobs.create(
            company=f"Co {index}",
            role="Eng",
            status=JobTargetStatus.NEW,
            priority="A",
            direct_apply_url=f"http://fixtures.local/apply/{index}",
        )
    await db_session.commit()

    batch = await create_batch(
        db_session,
        tenant_id=DEFAULT_DEV_TENANT_ID,
        plan=PlanTier.PRO,
        name="Pro batch",
        policy="review_before_submit",
        filters={"priority": "A"},
    )
    assert batch.id is not None


@pytest.mark.asyncio
async def test_stripe_subscription_active_upgrades_plan(db_session, truncate_tables) -> None:
    from jober_api.models.enums import PlanTier
    from jober_api.services.billing.stripe_webhook import apply_stripe_event

    tenant = await db_session.get(Tenant, DEFAULT_DEV_TENANT_ID)
    assert tenant is not None
    tenant.plan = PlanTier.FREE
    tenant.stripe_customer_id = "cus_test_123"
    await db_session.commit()

    await apply_stripe_event(
        db_session,
        {
            "type": "customer.subscription.updated",
            "data": {
                "object": {
                    "id": "sub_test",
                    "customer": "cus_test_123",
                    "status": "active",
                    "current_period_end": 1893456000,
                }
            },
        },
    )
    await db_session.commit()
    await db_session.refresh(tenant)
    assert tenant.plan == PlanTier.PRO


@pytest.mark.asyncio
async def test_checkout_completed_upgrades_via_tenant_metadata(
    db_session, truncate_tables
) -> None:
    from jober_api.services.billing.stripe_webhook import apply_stripe_event

    tenant = await db_session.get(Tenant, DEFAULT_DEV_TENANT_ID)
    assert tenant is not None
    tenant.plan = PlanTier.FREE
    tenant.stripe_customer_id = None
    await db_session.commit()

    await apply_stripe_event(
        db_session,
        {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "customer": "cus_from_checkout",
                    "metadata": {"tenant_id": str(DEFAULT_DEV_TENANT_ID)},
                }
            },
        },
    )
    await db_session.commit()
    await db_session.refresh(tenant)
    assert tenant.plan == PlanTier.PRO
    assert tenant.stripe_customer_id == "cus_from_checkout"
