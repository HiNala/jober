from typing import Any
from uuid import UUID

from jober_schemas.common import SchemaBase


class SelfAssessmentRead(SchemaBase):
    attempt_index: int
    strategy_name: str
    failure_class: str
    tried: str
    happened: str
    next_change: str


class FailureReportRead(SchemaBase):
    job_target_id: UUID
    company: str
    role: str
    apply_url: str | None
    failed_step: str
    failure_class: str
    inferred_reason: str
    recommended_manual_action: str
    safe_to_retry: bool
    attempt_count: int
    screenshot_object_key: str | None = None
    trace_object_key: str | None = None
    dom_snapshot_object_key: str | None = None
    attempted_actions: list[str] = []
    self_assessments: list[SelfAssessmentRead] = []


class FailureAnalyticsBucket(SchemaBase):
    platform: str
    failure_class: str
    count: int
    circuit_tripped: bool = False


class FailureAnalyticsRead(SchemaBase):
    buckets: list[FailureAnalyticsBucket]
    alerts: list[dict[str, Any]] = []
