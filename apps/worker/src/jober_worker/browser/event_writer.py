from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text

from jober_worker.browser.actions import Observation
from jober_worker.db import get_sync_session


def persist_browser_event(
    *,
    attempt_id: uuid.UUID,
    observation: Observation,
    screenshot_key: str | None = None,
    selector: str | None = None,
    level: str = "info",
) -> None:
    now = datetime.now(UTC)
    metadata = observation.metadata or {}
    with get_sync_session() as session:
        session.execute(
            text(
                """
                INSERT INTO browser_events (
                    id, attempt_id, ts, level, event_type, message,
                    selector, url, screenshot_key, metadata
                ) VALUES (
                    gen_random_uuid(), :attempt_id, :ts, :level, :event_type, :message,
                    :selector, :url, :screenshot_key, CAST(:metadata AS jsonb)
                )
                """
            ),
            {
                "attempt_id": str(attempt_id),
                "ts": now,
                "level": level,
                "event_type": observation.event_type,
                "message": observation.message,
                "selector": selector,
                "url": observation.url,
                "screenshot_key": screenshot_key,
                "metadata": _json_dumps(metadata),
            },
        )
        session.commit()


def _json_dumps(payload: dict[str, Any]) -> str:
    import json

    return json.dumps(payload)
