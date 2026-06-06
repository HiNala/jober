from datetime import datetime
from uuid import UUID

from jober_schemas.common import SchemaBase, TimestampedSchema
from jober_schemas.enums import RunPolicy, RunStatus


class ApplicationRunCreate(SchemaBase):
    job_target_id: UUID
    policy: RunPolicy = RunPolicy.REVIEW_BEFORE_SUBMIT


class ApplicationRunRead(TimestampedSchema):
    job_target_id: UUID
    status: RunStatus
    current_step: RunStatus | None
    policy: RunPolicy
    attempt_count: int
    started_at: datetime | None
    completed_at: datetime | None
    browser_session_id: str | None
    final_url: str | None
    submission_confirmation_text: str | None
    failure_reason: str | None
    human_review_required_reason: str | None
