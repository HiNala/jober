from __future__ import annotations

import json
import uuid
from datetime import UTC, date, datetime
from typing import Any

from jober_verify.idempotency import detect_already_applied_on_page, has_prior_successful_run
from jober_verify.submission import SubmissionOutcome, classify_submission
from sqlalchemy import text

from jober_worker.browser.session import browser_session
from jober_worker.browser.typed_actions import TypedBrowserActions
from jober_worker.db import get_sync_session
from jober_worker.fill_runner import _attempt_keys
from jober_worker.storage import ObjectStorage


def run_fixture_submit(
    *,
    run_id: uuid.UUID,
    attempt_id: uuid.UUID,
    job_target_id: uuid.UUID,
    fixture_html: str,
) -> dict[str, Any]:
    attempt_index = 1
    keys = _attempt_keys(run_id, attempt_index)
    storage = ObjectStorage()

    with browser_session(run_id=run_id, attempt_index=attempt_index) as session:
        actions = TypedBrowserActions(
            session.page,
            attempt_id=attempt_id,
            run_id=run_id,
            attempt_index=attempt_index,
            storage=storage,
        )
        session.page.set_content(fixture_html, wait_until="domcontentloaded")
        actions.wait_for_network_idle(timeout_ms=5000)

        before_url = session.page.url
        html = actions.content_html()
        visible = actions.get_visible_text()

        if detect_already_applied_on_page(html=html, visible_text=visible):
            return {
                "outcome": SubmissionOutcome.ALREADY_APPLIED.value,
                "confirmation_text": "Already applied detected on page",
                "final_url": before_url,
                "submit_clicked": False,
            }

        submit_clicked = False
        for selector in (
            "#submit-btn",
            'button:has-text("Submit")',
            'button[type="submit"]',
            'input[type="submit"]',
        ):
            loc = session.page.locator(selector)
            if loc.count() > 0 and loc.first.is_visible() and not loc.first.is_disabled():
                loc.first.click()
                submit_clicked = True
                break

        session.page.wait_for_timeout(300)
        final_url = session.page.url
        html_after = actions.content_html()
        visible_after = actions.get_visible_text()

        verification = classify_submission(
            html=html_after,
            visible_text=visible_after,
            final_url=final_url,
            before_url=before_url,
            submit_clicked=submit_clicked,
        )
        screenshot = actions.screenshot()
        storage.put_bytes(keys["screenshot"], screenshot, "image/png")

        return {
            **verification.to_dict(),
            "artifact_keys": keys,
            "job_target_id": str(job_target_id),
        }


def persist_submit_result(
    *,
    run_id: uuid.UUID,
    job_target_id: uuid.UUID,
    verification: dict[str, Any],
    prior_runs: list[Any] | None = None,
) -> None:
    outcome = verification.get("outcome")
    now = datetime.now(UTC)
    today = date.today()

    if prior_runs and has_prior_successful_run(prior_runs):
        outcome = SubmissionOutcome.ALREADY_APPLIED.value
        verification = {
            **verification,
            "outcome": outcome,
            "note": "Prior successful run exists for this job",
        }

    if outcome == SubmissionOutcome.SUCCESS.value:
        run_status = "succeeded"
        job_status = "applied"
    elif outcome == SubmissionOutcome.ALREADY_APPLIED.value:
        run_status = "skipped"
        job_status = "applied"
    elif outcome == SubmissionOutcome.UNCERTAIN.value:
        run_status = "verify_submission"
        job_status = "in_progress"
    else:
        run_status = "needs_human"
        job_status = "in_progress"

    with get_sync_session() as session:
        session.execute(
            text(
                """
                UPDATE application_runs
                SET status = :status,
                    current_step = :step,
                    final_url = :final_url,
                    submission_confirmation_text = :confirmation,
                    completed_at = :now,
                    human_review_required_reason = :reason,
                    updated_at = :now
                WHERE id = :run_id
                """
            ),
            {
                "status": run_status,
                "step": run_status,
                "final_url": verification.get("final_url"),
                "confirmation": verification.get("confirmation_text"),
                "reason": verification.get("note")
                if run_status in ("verify_submission", "needs_human")
                else None,
                "now": now,
                "run_id": str(run_id),
            },
        )
        if outcome == SubmissionOutcome.UNCERTAIN.value:
            session.execute(
                text(
                    """
                    INSERT INTO human_checkpoints (
                        id, run_id, checkpoint_type, prompt, options, status,
                        created_at, updated_at
                    ) VALUES (
                        gen_random_uuid(), :run_id, 'manual_intervention', :prompt,
                        CAST(:options AS jsonb), 'open', :now, :now
                    )
                    """
                ),
                {
                    "run_id": str(run_id),
                    "prompt": "Confirm whether the application was submitted successfully.",
                    "options": json.dumps(verification),
                    "now": now,
                },
            )
        if run_status in ("succeeded", "skipped") and outcome in (
            SubmissionOutcome.SUCCESS.value,
            SubmissionOutcome.ALREADY_APPLIED.value,
        ):
            session.execute(
                text(
                    """
                    UPDATE job_targets
                    SET status = :job_status,
                        applied_date = COALESCE(applied_date, :today),
                        updated_at = :now
                    WHERE id = :job_id
                    """
                ),
                {
                    "job_status": job_status,
                    "today": today,
                    "now": now,
                    "job_id": str(job_target_id),
                },
            )
        session.execute(
            text(
                """
                UPDATE human_checkpoints
                SET status = 'resolved', resolved_at = :now, updated_at = :now
                WHERE run_id = :run_id AND checkpoint_type = 'review_submit'
                  AND status = 'open'
                """
            ),
            {"now": now, "run_id": str(run_id)},
        )
        session.commit()
