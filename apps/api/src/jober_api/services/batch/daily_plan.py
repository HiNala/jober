from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.config import settings
from jober_api.services.batch.cost_governor import budget_status
from jober_api.services.batch.service import preview_batch


async def generate_daily_plan(session: AsyncSession, tenant_id: uuid.UUID) -> dict[str, Any]:
    filters: dict[str, Any] = {"priority": "A", "status": "new", "limit": 200}
    preview = await preview_batch(session, filters, tenant_id)
    included = preview["included"]
    domains = preview["domain_count"]
    jobs = len(included)
    est_cost = float(preview["estimated_cost_usd"])
    max_conc = settings.batch_max_concurrency
    cooldown = settings.batch_site_cooldown_seconds
    est_minutes = int((jobs / max(max_conc, 1)) * cooldown / 60) if jobs else 0
    budget = await budget_status(session)
    summary = (
        f"{jobs} Priority A across {domains} domains, "
        f"~${est_cost:.2f} est., ~{est_minutes} min paced"
    )
    return {
        "summary": summary,
        "proposed_filters": filters,
        "preview": preview,
        "budget": budget,
        "recommended_policy": "review_before_submit",
        "pacing_note": (
            "Per-site cooldown spaces requests for server-friendliness — "
            "stay in the loop for review-before-submit checkpoints."
        ),
    }
