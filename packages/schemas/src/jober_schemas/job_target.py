from datetime import date
from uuid import UUID

from jober_schemas.common import SchemaBase, TimestampedSchema
from jober_schemas.enums import JobTargetStatus


class JobTargetCreate(SchemaBase):
    rank: int | None = None
    priority: str | None = None
    company: str
    role: str
    fit_lane: str | None = None
    stage_signal: str | None = None
    location_work_style: str | None = None
    why_fit: str | None = None
    cover_letter_hook: str | None = None
    public_contact: str | None = None
    direct_apply_url: str | None = None
    company_careers_url: str | None = None
    source_note: str | None = None
    verified_date: date | None = None
    status: JobTargetStatus = JobTargetStatus.NEW
    notes: str | None = None
    import_id: str | None = None


class JobTargetRead(TimestampedSchema):
    rank: int | None
    priority: str | None
    company: str
    role: str
    fit_lane: str | None
    stage_signal: str | None
    location_work_style: str | None
    why_fit: str | None
    cover_letter_hook: str | None
    public_contact: str | None
    direct_apply_url: str | None
    company_careers_url: str | None
    source_note: str | None
    verified_date: date | None
    status: JobTargetStatus
    applied_date: date | None
    follow_up_date: date | None
    notes: str | None
    import_id: str | None


class JobTargetUpdate(SchemaBase):
    status: JobTargetStatus | None = None
    applied_date: date | None = None
    follow_up_date: date | None = None
    notes: str | None = None
