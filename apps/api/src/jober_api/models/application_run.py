import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from jober_api.db.base import Base
from jober_api.models.constants import str_enum_column
from jober_api.models.enums import RunPolicy, RunStatus
from jober_api.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from jober_api.models.application_attempt import ApplicationAttempt
    from jober_api.models.generated_document import GeneratedDocument
    from jober_api.models.human_checkpoint import HumanCheckpoint
    from jober_api.models.job_target import JobTarget
    from jober_api.models.llm_call import LlmCall


class ApplicationRun(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "application_runs"
    __table_args__ = (Index("ix_application_runs_status", "status"),)

    job_target_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_targets.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[RunStatus] = mapped_column(
        str_enum_column(RunStatus), default=RunStatus.QUEUED, nullable=False
    )
    current_step: Mapped[RunStatus | None] = mapped_column(str_enum_column(RunStatus))
    policy: Mapped[RunPolicy] = mapped_column(
        str_enum_column(RunPolicy),
        default=RunPolicy.REVIEW_BEFORE_SUBMIT,
        nullable=False,
    )
    attempt_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    browser_session_id: Mapped[str | None] = mapped_column(String(128))
    final_url: Mapped[str | None] = mapped_column(Text)
    submission_confirmation_text: Mapped[str | None] = mapped_column(Text)
    failure_reason: Mapped[str | None] = mapped_column(Text)
    human_review_required_reason: Mapped[str | None] = mapped_column(Text)
    checkpoint_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    job_target: Mapped["JobTarget"] = relationship(back_populates="application_runs")
    attempts: Mapped[list["ApplicationAttempt"]] = relationship(back_populates="run")
    checkpoints: Mapped[list["HumanCheckpoint"]] = relationship(back_populates="run")
    llm_calls: Mapped[list["LlmCall"]] = relationship(back_populates="run")
    generated_documents: Mapped[list["GeneratedDocument"]] = relationship(back_populates="run")
