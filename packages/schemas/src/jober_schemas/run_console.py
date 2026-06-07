from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class RunEventType(StrEnum):
    RUN_STARTED = "run.started"
    STATE_CHANGED = "state.changed"
    BROWSER_NAVIGATED = "browser.navigated"
    BROWSER_ACTION = "browser.action"
    BROWSER_SCREENSHOT = "browser.screenshot"
    FORM_DISCOVERED = "form.discovered"
    FIELD_FILLED = "field.filled"
    DOCUMENT_GENERATED = "document.generated"
    VERIFICATION_WARNING = "verification.warning"
    HUMAN_REQUIRED = "human.required"
    ATTEMPT_FAILED = "attempt.failed"
    ATTEMPT_RETRYING = "attempt.retrying"
    RUN_SUCCEEDED = "run.succeeded"
    RUN_FAILED = "run.failed"


class RunEventRead(BaseModel):
    id: str
    seq: int
    ts: str
    event_type: str
    level: str = "info"
    message: str
    payload: dict[str, Any] = Field(default_factory=dict)
    screenshot_key: str | None = None
    screenshot_url: str | None = None
    attempt_index: int | None = None


class RunConsoleSnapshotRead(BaseModel):
    run_id: str
    job_target_id: str
    company: str
    role: str
    status: str
    current_step: str | None = None
    attempt_count: int = 0
    latest_screenshot_url: str | None = None
    latest_screenshot_key: str | None = None
    open_checkpoint: dict[str, Any] | None = None
    timeline: list[dict[str, Any]] = Field(default_factory=list)
    artifacts: list[dict[str, Any]] = Field(default_factory=list)
    last_event_seq: int = 0
    events: list[RunEventRead] = Field(default_factory=list)


class CheckpointResolveRequest(BaseModel):
    action: str = Field(description="approve | deny | edit | skip")
    value: str | None = None


class CheckpointResolveRead(BaseModel):
    checkpoint_id: str
    status: str
    run_status: str
    action: str
