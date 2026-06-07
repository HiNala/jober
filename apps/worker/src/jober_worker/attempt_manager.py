from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any

from jober_recover.budget import AttemptBudget
from jober_recover.failure_report import FailureReport
from jober_recover.self_assessment import SelfAssessment
from jober_recover.taxonomy import FailureClass
from sqlalchemy import text

from jober_worker.db import get_sync_session


def persist_checkpoint(
    *,
    run_id: uuid.UUID,
    step: str,
    data: dict[str, Any],
) -> None:
    now = datetime.now(UTC)
    payload = json.dumps({"step": step, **data})
    with get_sync_session() as session:
        session.execute(
            text(
                """
                UPDATE application_runs
                SET checkpoint_data = CAST(:payload AS jsonb),
                    current_step = :step,
                    updated_at = :now
                WHERE id = :run_id
                """
            ),
            {"payload": payload, "step": step, "now": now, "run_id": str(run_id)},
        )
        session.commit()


def load_checkpoint(run_id: uuid.UUID) -> dict[str, Any]:
    with get_sync_session() as session:
        row = session.execute(
            text("SELECT checkpoint_data FROM application_runs WHERE id = :run_id"),
            {"run_id": str(run_id)},
        ).mappings().first()
    if not row or not row.get("checkpoint_data"):
        return {}
    data = row["checkpoint_data"]
    return dict(data) if isinstance(data, dict) else {}


def create_attempt(
    *,
    run_id: uuid.UUID,
    attempt_index: int,
    strategy_name: str,
) -> uuid.UUID:
    now = datetime.now(UTC)
    attempt_id = uuid.uuid4()
    with get_sync_session() as session:
        session.execute(
            text(
                """
                INSERT INTO application_attempts (
                    id, run_id, attempt_index, status, strategy_name,
                    started_at, created_at, updated_at
                ) VALUES (
                    :id, :run_id, :attempt_index, 'running', :strategy_name,
                    :now, :now, :now
                )
                """
            ),
            {
                "id": str(attempt_id),
                "run_id": str(run_id),
                "attempt_index": attempt_index,
                "strategy_name": strategy_name,
                "now": now,
            },
        )
        session.execute(
            text(
                """
                UPDATE application_runs
                SET attempt_count = :attempt_index,
                    status = 'fill_form',
                    current_step = 'fill_form',
                    updated_at = :now
                WHERE id = :run_id
                """
            ),
            {"attempt_index": attempt_index, "now": now, "run_id": str(run_id)},
        )
        session.commit()
    return attempt_id


def persist_attempt_failure(
    *,
    run_id: uuid.UUID,
    attempt_id: uuid.UUID,
    failure_class: FailureClass,
    error_message: str,
    assessment: SelfAssessment,
    artifact_keys: dict[str, str],
    budget: AttemptBudget | None = None,
) -> str:
    budget = budget or AttemptBudget()
    now = datetime.now(UTC)
    with get_sync_session() as session:
        attempt_row = session.execute(
            text("SELECT attempt_index FROM application_attempts WHERE id = :id"),
            {"id": str(attempt_id)},
        ).mappings().first()
        attempt_index = int(attempt_row["attempt_index"]) if attempt_row else 1
        run_status = budget.next_status(attempt_index, failure_class=failure_class)

        session.execute(
            text(
                """
                UPDATE application_attempts
                SET status = 'failed',
                    failure_class = :failure_class,
                    error_summary = :error_summary,
                    self_assessment = CAST(:assessment AS jsonb),
                    final_screenshot_object_key = :screenshot,
                    dom_snapshot_object_key = :dom,
                    completed_at = :now,
                    updated_at = :now
                WHERE id = :attempt_id
                """
            ),
            {
                "failure_class": failure_class.value,
                "error_summary": error_message[:2000],
                "assessment": json.dumps(assessment.to_dict()),
                "screenshot": artifact_keys.get("screenshot"),
                "dom": artifact_keys.get("dom"),
                "now": now,
                "attempt_id": str(attempt_id),
            },
        )
        session.execute(
            text(
                """
                UPDATE application_runs
                SET status = :status,
                    failure_reason = :reason,
                    human_review_required_reason = :reason,
                    updated_at = :now
                WHERE id = :run_id
                """
            ),
            {
                "status": run_status,
                "reason": error_message[:1000],
                "now": now,
                "run_id": str(run_id),
            },
        )
        session.commit()
    return run_status


def persist_attempt_success(
    *,
    run_id: uuid.UUID,
    attempt_id: uuid.UUID,
    artifact_keys: dict[str, str],
) -> None:
    now = datetime.now(UTC)
    with get_sync_session() as session:
        session.execute(
            text(
                """
                UPDATE application_attempts
                SET status = 'succeeded',
                    final_screenshot_object_key = :screenshot,
                    dom_snapshot_object_key = :dom,
                    completed_at = :now,
                    updated_at = :now
                WHERE id = :attempt_id
                """
            ),
            {
                "screenshot": artifact_keys.get("screenshot"),
                "dom": artifact_keys.get("dom"),
                "now": now,
                "attempt_id": str(attempt_id),
            },
        )
        session.execute(
            text(
                """
                UPDATE application_runs
                SET status = 'fill_form',
                    current_step = 'fill_form',
                    failure_reason = NULL,
                    updated_at = :now
                WHERE id = :run_id
                """
            ),
            {"now": now, "run_id": str(run_id)},
        )
        session.commit()


def persist_final_failure_report(
    *,
    run_id: uuid.UUID,
    report: FailureReport,
) -> None:
    now = datetime.now(UTC)
    with get_sync_session() as session:
        session.execute(
            text(
                """
                UPDATE application_runs
                SET status = 'failed_final',
                    failure_reason = :reason,
                    checkpoint_data = COALESCE(checkpoint_data, '{}'::jsonb)
                        || CAST(:report AS jsonb),
                    completed_at = :now,
                    updated_at = :now
                WHERE id = :run_id
                """
            ),
            {
                "reason": report.inferred_reason[:1000],
                "report": json.dumps({"failure_report": report.to_dict()}),
                "now": now,
                "run_id": str(run_id),
            },
        )
        session.commit()
