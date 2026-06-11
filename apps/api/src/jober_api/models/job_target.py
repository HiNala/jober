import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from jober_api.db.base import Base
from jober_api.models.constants import str_enum_column
from jober_api.models.enums import JobTargetStatus
from jober_api.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from jober_api.models.application_run import ApplicationRun
    from jober_api.models.generated_document import GeneratedDocument


class JobTarget(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "job_targets"
    __table_args__ = (
        Index("ix_job_targets_status", "status"),
        Index("ix_job_targets_tenant_id", "tenant_id"),
        Index("ix_job_targets_tenant_status", "tenant_id", "status"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )
    rank: Mapped[int | None] = mapped_column(Integer)
    priority: Mapped[str | None] = mapped_column(String(8))
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(255), nullable=False)
    fit_lane: Mapped[str | None] = mapped_column(String(128))
    stage_signal: Mapped[str | None] = mapped_column(String(255))
    location_work_style: Mapped[str | None] = mapped_column(String(255))
    why_fit: Mapped[str | None] = mapped_column(Text)
    cover_letter_hook: Mapped[str | None] = mapped_column(Text)
    public_contact: Mapped[str | None] = mapped_column(String(320))
    direct_apply_url: Mapped[str | None] = mapped_column(Text)
    company_careers_url: Mapped[str | None] = mapped_column(Text)
    source_note: Mapped[str | None] = mapped_column(Text)
    verified_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[JobTargetStatus] = mapped_column(
        str_enum_column(JobTargetStatus),
        default=JobTargetStatus.NEW,
        nullable=False,
    )
    applied_date: Mapped[date | None] = mapped_column(Date)
    follow_up_date: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
    import_id: Mapped[str | None] = mapped_column(String(128))
    extracted_job_profile: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    platform_detection: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    job_profile_extracted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    job_profile_cache_date: Mapped[date | None] = mapped_column(Date)

    application_runs: Mapped[list["ApplicationRun"]] = relationship(back_populates="job_target")
    generated_documents: Mapped[list["GeneratedDocument"]] = relationship(
        back_populates="job_target"
    )
