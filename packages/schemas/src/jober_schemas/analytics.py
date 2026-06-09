from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AnalyticsEventInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    ts: datetime | None = None
    anon_id: str | None = Field(default=None, max_length=64)
    session_id: str = Field(..., min_length=8, max_length=64)
    page: str | None = Field(default=None, max_length=2048)
    referrer: str | None = Field(default=None, max_length=2048)
    utm_source: str | None = Field(default=None, max_length=255)
    utm_medium: str | None = Field(default=None, max_length=255)
    utm_campaign: str | None = Field(default=None, max_length=255)
    utm_term: str | None = Field(default=None, max_length=255)
    utm_content: str | None = Field(default=None, max_length=255)
    props: dict[str, Any] = Field(default_factory=dict)


class AnalyticsBatchRequest(BaseModel):
    events: list[AnalyticsEventInput] = Field(..., min_length=1, max_length=50)
