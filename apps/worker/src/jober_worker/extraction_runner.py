from __future__ import annotations

import json
import uuid
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from jober_extraction.gates import GateKind, detect_access_gates
from jober_extraction.intelligence import build_job_profile
from jober_extraction.platform import detect_platform

from jober_worker.browser.checkpoints import gate_checkpoint
from jober_worker.browser.session import browser_session
from jober_worker.db import get_sync_session
from jober_worker.storage import ObjectStorage


def _attempt_keys(run_id: uuid.UUID, attempt_index: int) -> dict[str, str]:
    base = f"runs/{run_id}/attempts/{attempt_index}"
    return {
        "trace": f"{base}/trace.zip",
        "video": f"{base}/video.webm",
        "screenshot": f"{base}/screenshot.png",
        "dom": f"{base}/dom.json",
    }


def run_browser_extraction(
    *,
    run_id: uuid.UUID,
    job_target_id: uuid.UUID,
    url: str,
    company_hint: str,
    resume_skills: list[str] | None,
) -> dict[str, Any]:
    attempt_index = 1
    keys = _attempt_keys(run_id, attempt_index)
    storage = ObjectStorage()

    with browser_session(run_id=run_id, attempt_index=attempt_index) as session:
        actions = session.actions
        actions.goto(url)
        actions.wait_for_network_idle(timeout_ms=20000)
        html = actions.content_html()
        visible = actions.get_visible_text()
        a11y = actions.extract_accessibility_tree()

        gates = detect_access_gates(html, visible)
        if gates:
            gate = gates[0]
            checkpoint = actions.request_human_checkpoint(
                gate_checkpoint(gate),
                f"Resolve {gate.value} before continuing.",
            )
            screenshot = actions.screenshot()
            storage.put_bytes(keys["screenshot"], screenshot, "image/png")
            if session.trace_path and session.trace_path.exists():
                storage.put_bytes(keys["trace"], session.trace_path.read_bytes(), "application/zip")
            _persist_checkpoint(
                run_id=run_id,
                gate=gate,
                prompt=checkpoint["prompt"],
                keys=keys,
            )
            return {
                "status": "needs_human",
                "gate": gate.value,
                "checkpoint": checkpoint,
                "artifact_keys": keys,
            }

        platform = detect_platform(url, html)
        profile = build_job_profile(
            html=html,
            visible_text=visible,
            accessibility_tree=a11y,
            company_hint=company_hint,
            resume_skills=resume_skills,
        )
        screenshot = actions.screenshot()
        storage.put_bytes(keys["screenshot"], screenshot, "image/png")
        dom_payload = json.dumps({"html_len": len(html), "a11y_roles": len(str(a11y))}).encode()
        storage.put_bytes(keys["dom"], dom_payload, "application/json")
        if session.trace_path and session.trace_path.exists():
            storage.put_bytes(keys["trace"], session.trace_path.read_bytes(), "application/zip")
        video_files = list((session.video_dir or Path()).glob("*.webm"))
        if video_files:
            storage.put_bytes(keys["video"], video_files[0].read_bytes(), "video/webm")

        _persist_to_db(
            run_id=run_id,
            job_target_id=job_target_id,
            url=url,
            platform=platform.model_dump(),
            profile=profile.model_dump(),
            keys=keys,
        )
        return {
            "status": "succeeded",
            "platform": platform.model_dump(),
            "job_profile": profile.model_dump(),
            "artifact_keys": keys,
        }


def _persist_checkpoint(
    *,
    run_id: uuid.UUID,
    gate: GateKind,
    prompt: str,
    keys: dict[str, str],
) -> None:
    from sqlalchemy import text

    now = datetime.now(UTC)
    checkpoint_type = {
        GateKind.LOGIN: "login",
        GateKind.CAPTCHA: "captcha",
        GateKind.TWO_FACTOR: "two_factor",
    }[gate]
    with get_sync_session() as session:
        session.execute(
            text(
                """
                UPDATE application_runs
                SET status = 'needs_human',
                    human_review_required_reason = :reason,
                    updated_at = :now
                WHERE id = :run_id
                """
            ),
            {"reason": gate.value, "now": now, "run_id": str(run_id)},
        )
        session.execute(
            text(
                """
                INSERT INTO human_checkpoints (
                    id, run_id, checkpoint_type, prompt, status, created_at, updated_at
                ) VALUES (
                    gen_random_uuid(), :run_id, :ctype, :prompt, 'open', :now, :now
                )
                """
            ),
            {
                "run_id": str(run_id),
                "ctype": checkpoint_type,
                "prompt": prompt,
                "now": now,
            },
        )
        session.execute(
            text(
                """
                INSERT INTO application_attempts (
                    id, run_id, attempt_index, status,
                    trace_object_key, final_screenshot_object_key,
                    started_at, completed_at, created_at, updated_at
                ) VALUES (
                    gen_random_uuid(), :run_id, 1, 'failed',
                    :trace, :screenshot, :now, :now, :now, :now
                )
                """
            ),
            {
                "run_id": str(run_id),
                "trace": keys["trace"],
                "screenshot": keys["screenshot"],
                "now": now,
            },
        )
        session.commit()


def _persist_to_db(
    *,
    run_id: uuid.UUID,
    job_target_id: uuid.UUID,
    url: str,
    platform: dict[str, Any],
    profile: dict[str, Any],
    keys: dict[str, str],
) -> None:
    from sqlalchemy import text

    now = datetime.now(UTC)
    today = date.today()
    with get_sync_session() as session:
        session.execute(
            text(
                """
                UPDATE job_targets
                SET extracted_job_profile = :profile::jsonb,
                    platform_detection = :platform::jsonb,
                    job_profile_extracted_at = :now,
                    job_profile_cache_date = :today,
                    updated_at = :now
                WHERE id = :job_id
                """
            ),
            {
                "profile": json.dumps(profile),
                "platform": json.dumps(platform),
                "now": now,
                "today": today,
                "job_id": str(job_target_id),
            },
        )
        session.execute(
            text(
                """
                UPDATE application_runs
                SET status = 'succeeded', current_step = 'extract_job',
                    final_url = :url, completed_at = :now, updated_at = :now
                WHERE id = :run_id
                """
            ),
            {"url": url, "now": now, "run_id": str(run_id)},
        )
        session.execute(
            text(
                """
                INSERT INTO application_attempts (
                    id, run_id, attempt_index, status, platform_detected,
                    trace_object_key, video_object_key, final_screenshot_object_key,
                    dom_snapshot_object_key, started_at, completed_at, created_at, updated_at
                ) VALUES (
                    gen_random_uuid(), :run_id, 1, 'succeeded', :platform,
                    :trace, :video, :screenshot, :dom, :now, :now, :now, :now
                )
                """
            ),
            {
                "run_id": str(run_id),
                "platform": platform.get("platform"),
                "trace": keys["trace"],
                "video": keys.get("video"),
                "screenshot": keys["screenshot"],
                "dom": keys["dom"],
                "now": now,
            },
        )
        session.commit()
