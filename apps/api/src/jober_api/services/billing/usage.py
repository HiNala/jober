from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.application_run import ApplicationRun
from jober_api.models.enums import PlanTier, RunStatus
from jober_api.models.generated_document import GeneratedDocument
from jober_api.models.job_target import JobTarget
from jober_api.models.llm_call import LlmCall
from jober_api.services.billing.entitlements import entitlements_for


def _month_start() -> datetime:
    return datetime.now(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)


async def tenant_monthly_llm_spend(session: AsyncSession, tenant_id: uuid.UUID) -> float:
    month_start = _month_start()
    stmt = (
        select(func.coalesce(func.sum(LlmCall.cost_usd), 0.0))
        .join(ApplicationRun, LlmCall.run_id == ApplicationRun.id)
        .where(
            ApplicationRun.tenant_id == tenant_id,
            LlmCall.created_at >= month_start,
        )
    )
    value = (await session.execute(stmt)).scalar_one()
    return float(value or 0.0)


async def tenant_monthly_run_count(session: AsyncSession, tenant_id: uuid.UUID) -> int:
    month_start = _month_start()
    stmt = (
        select(func.count())
        .select_from(ApplicationRun)
        .where(
            ApplicationRun.tenant_id == tenant_id,
            ApplicationRun.created_at >= month_start,
            ApplicationRun.status.notin_([RunStatus.SKIPPED]),
        )
    )
    return int((await session.execute(stmt)).scalar_one())


async def tenant_document_count(session: AsyncSession, tenant_id: uuid.UUID) -> int:
    month_start = _month_start()
    stmt = (
        select(func.count())
        .select_from(GeneratedDocument)
        .join(JobTarget, GeneratedDocument.job_target_id == JobTarget.id)
        .where(
            JobTarget.tenant_id == tenant_id,
            GeneratedDocument.created_at >= month_start,
        )
    )
    return int((await session.execute(stmt)).scalar_one())


async def usage_dashboard(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    plan: PlanTier,
) -> dict[str, object]:
    ents = entitlements_for(plan)
    runs = await tenant_monthly_run_count(session, tenant_id)
    llm_spend = await tenant_monthly_llm_spend(session, tenant_id)
    documents = await tenant_document_count(session, tenant_id)
    return {
        "plan": plan.value,
        "limits": {
            "max_batch_items": ents.max_batch_items,
            "max_monthly_runs": ents.max_monthly_runs,
            "max_llm_budget_usd": ents.max_llm_budget_usd,
        },
        "usage": {
            "monthly_runs": runs,
            "documents_generated": documents,
            "llm_cost_usd": round(llm_spend, 4),
        },
        "remaining": {
            "monthly_runs": max(0, ents.max_monthly_runs - runs),
            "llm_budget_usd": round(max(0.0, ents.max_llm_budget_usd - llm_spend), 4),
        },
    }
