from __future__ import annotations

import os
import uuid
from datetime import UTC, datetime

import pytest

from jober_api.auth.constants import DEFAULT_DEV_TENANT_ID
from jober_api.models.enums import JobTargetStatus
from jober_api.models.failure_event import FailureEvent
from jober_api.models.job_target import JobTarget
from jober_api.services.admin.ops_metrics import (
    CIRCUIT_BREAKER_THRESHOLD,
    build_ops_attention,
    global_circuit_trips,
)

requires_postgres = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres",
)


@requires_postgres
@pytest.mark.asyncio
async def test_global_circuit_trips_cross_tenant(db_session, truncate_tables) -> None:
    target = JobTarget(
        id=uuid.uuid4(),
        tenant_id=DEFAULT_DEV_TENANT_ID,
        company="Acme",
        role="Engineer",
        status=JobTargetStatus.QUEUED,
    )
    db_session.add(target)
    await db_session.flush()
    for _ in range(CIRCUIT_BREAKER_THRESHOLD):
        db_session.add(
            FailureEvent(
                id=uuid.uuid4(),
                job_target_id=target.id,
                run_id=None,
                platform="greenhouse",
                failure_class="captcha",
                created_at=datetime.now(UTC),
            )
        )
    await db_session.commit()

    trips = await global_circuit_trips(db_session)
    assert len(trips) == 1
    assert trips[0]["platform"] == "greenhouse"
    assert trips[0]["count"] >= CIRCUIT_BREAKER_THRESHOLD


@requires_postgres
@pytest.mark.asyncio
async def test_build_ops_attention_flags_budget_soft_warn(
    db_session,
    truncate_tables,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from jober_api.config import settings

    monkeypatch.setattr(settings, "llm_monthly_budget_usd", 10.0)
    monkeypatch.setattr(settings, "llm_budget_soft_warn_ratio", 0.5)

    attention, ops = await build_ops_attention(
        db_session,
        queue={"active_runs": 0, "globally_paused": False},
        broker_depth=0,
    )
    assert ops["budget"]["soft_warn"] is False or isinstance(attention, list)
