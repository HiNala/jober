from __future__ import annotations

from dataclasses import dataclass

from jober_api.models.enums import PlanTier


@dataclass(frozen=True)
class PlanEntitlements:
    max_batch_items: int
    max_monthly_runs: int
    max_llm_budget_usd: float


PLAN_ENTITLEMENTS: dict[PlanTier, PlanEntitlements] = {
    PlanTier.FREE: PlanEntitlements(
        max_batch_items=5,
        max_monthly_runs=20,
        max_llm_budget_usd=5.0,
    ),
    PlanTier.PRO: PlanEntitlements(
        max_batch_items=100,
        max_monthly_runs=500,
        max_llm_budget_usd=50.0,
    ),
}


def entitlements_for(plan: PlanTier) -> PlanEntitlements:
    return PLAN_ENTITLEMENTS.get(plan, PLAN_ENTITLEMENTS[PlanTier.FREE])
