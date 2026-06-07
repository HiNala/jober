from __future__ import annotations

from pydantic import BaseModel, Field

from jober_schemas.common import TimestampedSchema


class PlatformDetectionRead(BaseModel):
    platform: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)


class JobProfileRead(BaseModel):
    title: str
    company: str
    location: str | None = None
    description: str
    responsibilities: list[str] = Field(default_factory=list)
    requirements: list[str] = Field(default_factory=list)
    seniority_signal: str | None = None
    keywords: list[str] = Field(default_factory=list)
    fit_score: float | None = Field(default=None, ge=0.0, le=100.0)
    company_product_summary: str | None = None


class JobExtractionRead(TimestampedSchema):
    job_target_id: str
    platform_detection: PlatformDetectionRead
    job_profile: JobProfileRead
    cached: bool
    extracted_at: str | None
    run_id: str | None = None
