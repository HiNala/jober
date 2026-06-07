from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.config import settings
from jober_api.models.application_run import ApplicationRun
from jober_api.models.llm_call import LlmCall
from jober_api.services.llm.gateway import BudgetExceededError, monthly_llm_spend


async def batch_llm_spend(session: AsyncSession, batch_id: uuid.UUID) -> float:
    stmt = (
        select(func.coalesce(func.sum(LlmCall.cost_usd), 0.0))
        .join(ApplicationRun, LlmCall.run_id == ApplicationRun.id)
        .where(ApplicationRun.batch_id == batch_id)
    )
    result = await session.execute(stmt)
    return float(result.scalar_one() or 0.0)


async def budget_status(
    session: AsyncSession,
    *,
    projected_cost: float = 0.0,
) -> dict[str, Any]:
    budget = settings.llm_monthly_budget_usd
    spent = await monthly_llm_spend(session)
    projected_total = spent + projected_cost
    soft_threshold = budget * settings.llm_budget_soft_warn_ratio
    return {
        "monthly_budget_usd": budget,
        "spent_usd": round(spent, 4),
        "projected_total_usd": round(projected_total, 4),
        "soft_warn": budget > 0 and projected_total >= soft_threshold,
        "hard_stop": budget > 0 and projected_total > budget,
    }


async def assert_generation_budget(
    session: AsyncSession, projected_cost: float = 0.0
) -> dict[str, Any]:
    status = await budget_status(session, projected_cost=projected_cost)
    if status["hard_stop"]:
        msg = (
            f"LLM monthly budget exceeded (${status['spent_usd']:.2f} spent, "
            f"${status['monthly_budget_usd']:.2f} cap). Generation blocked."
        )
        raise BudgetExceededError(msg)
    return status
