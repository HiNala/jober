from typing import Any
from uuid import UUID

from jober_schemas.common import SchemaBase
from jober_schemas.enums import RunStatus


class ReadinessCheckRead(SchemaBase):
    check_id: str
    passed: bool
    reason: str
    evidence: dict[str, Any] | None = None


class ReadinessReportRead(SchemaBase):
    passed: bool
    checks: list[ReadinessCheckRead]


class VerifyReadyRead(SchemaBase):
    run_id: UUID
    status: RunStatus
    readiness: ReadinessReportRead
    human_summary: str | None = None
    gate: str | None = None


class FillDiffItemRead(SchemaBase):
    field_key: str
    label: str | None
    proposed_redacted: str | None = None
    actual_redacted: str | None = None
    matched: bool | None = None
    locator_strategy: str | None = None


class ReviewCoverLetterRead(SchemaBase):
    id: UUID
    text: str
    ats_score: float | None = None
    keyword_coverage: dict[str, Any] | None = None
    template_style: str | None = None
    voice_preset: str | None = None
    locked_paragraphs: list[int] = []
    pdf_download_path: str | None = None


class ReviewPackageRead(SchemaBase):
    run_id: UUID
    job_target_id: UUID
    company: str
    role: str
    status: RunStatus
    human_summary: str
    readiness: ReadinessReportRead
    fill_diffs: list[FillDiffItemRead]
    screenshot_object_key: str | None = None
    resume_filename: str | None = None
    cover_letter_preview: str | None = None
    cover_letter: ReviewCoverLetterRead | None = None
    checkpoint_id: UUID | None = None
    policy: str


class SubmitResultRead(SchemaBase):
    run_id: UUID
    outcome: str
    confirmation_text: str | None = None
    final_url: str | None = None
    note: str | None = None
    job_target_status: str | None = None
