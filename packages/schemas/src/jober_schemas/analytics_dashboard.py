from __future__ import annotations

from pydantic import BaseModel, Field


class DateRangeRead(BaseModel):
    start: str
    end: str


class FunnelStepRead(BaseModel):
    step: str
    event_name: str
    event_count: int
    unique_sessions: int
    drop_off_sessions: int
    drop_off_rate: float


class FunnelDashboardRead(BaseModel):
    range: DateRangeRead
    steps: list[FunnelStepRead]
    previous_steps: list[FunnelStepRead] | None = None


class UserSummaryRead(BaseModel):
    applications_sent: int
    responses_tracked: int
    letters_generated: int
    llm_cost_usd: float
    llm_budget_usd: float
    budget_used_ratio: float


class UserAnalyticsRead(BaseModel):
    range: DateRangeRead
    summary: UserSummaryRead
    activity: list[dict[str, object]]
    cost_series: list[dict[str, object]]
    attention: list[dict[str, str]]
    previous: UserSummaryRead | None = None
