from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text

from jober_worker.db import get_sync_session

_OBSERVATION_EVENT_MAP: dict[str, str] = {
    "goto": "browser.navigated",
    "fill_by_label": "browser.action",
    "select_by_label": "browser.action",
    "check_by_label": "browser.action",
    "upload_file": "browser.action",
    "screenshot": "browser.screenshot",
    "request_human_checkpoint": "human.required",
}


def persist_run_event(
    *,
    run_id: uuid.UUID,
    event_type: str,
    message: str,
    level: str = "info",
    payload: dict[str, Any] | None = None,
    screenshot_key: str | None = None,
    attempt_index: int | None = None,
) -> int:
    now = datetime.now(UTC)
    with get_sync_session() as session:
        row = session.execute(
            text(
                """
                SELECT COALESCE(MAX(seq), 0) + 1 AS next_seq
                FROM run_events WHERE run_id = :run_id
                """
            ),
            {"run_id": str(run_id)},
        ).mappings().first()
        seq = int(row["next_seq"]) if row else 1
        session.execute(
            text(
                """
                INSERT INTO run_events (
                    id, run_id, seq, ts, event_type, level, message,
                    payload, screenshot_key, attempt_index
                ) VALUES (
                    gen_random_uuid(), :run_id, :seq, :ts, :event_type, :level, :message,
                    CAST(:payload AS jsonb), :screenshot_key, :attempt_index
                )
                """
            ),
            {
                "run_id": str(run_id),
                "seq": seq,
                "ts": now,
                "event_type": event_type,
                "level": level,
                "message": message,
                "payload": json.dumps(payload or {}),
                "screenshot_key": screenshot_key,
                "attempt_index": attempt_index,
            },
        )
        session.commit()
    return seq


def persist_observation_as_run_event(
    *,
    run_id: uuid.UUID,
    attempt_index: int,
    event_type: str,
    message: str,
    screenshot_key: str | None = None,
    payload: dict[str, Any] | None = None,
) -> int:
    mapped = _OBSERVATION_EVENT_MAP.get(event_type, "browser.action")
    if mapped == "browser.screenshot" and not screenshot_key:
        return 0
    return persist_run_event(
        run_id=run_id,
        event_type=mapped,
        message=message,
        screenshot_key=screenshot_key,
        attempt_index=attempt_index,
        payload={"observation_type": event_type, **(payload or {})},
    )
