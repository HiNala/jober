import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from jober_api.db.base import Base
from jober_api.models.constants import str_enum_column
from jober_api.models.enums import AttemptStatus
from jober_api.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from jober_api.models.application_run import ApplicationRun
    from jober_api.models.browser_event import BrowserEvent
    from jober_api.models.form_field_observation import FormFieldObservation


class ApplicationAttempt(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "application_attempts"

    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("application_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    attempt_index: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[AttemptStatus] = mapped_column(
        str_enum_column(AttemptStatus),
        default=AttemptStatus.PENDING,
        nullable=False,
    )
    platform_detected: Mapped[str | None] = mapped_column(String(64))
    strategy_name: Mapped[str | None] = mapped_column(String(128))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    trace_object_key: Mapped[str | None] = mapped_column(String(512))
    video_object_key: Mapped[str | None] = mapped_column(String(512))
    final_screenshot_object_key: Mapped[str | None] = mapped_column(String(512))
    dom_snapshot_object_key: Mapped[str | None] = mapped_column(String(512))
    error_summary: Mapped[str | None] = mapped_column(Text)

    run: Mapped["ApplicationRun"] = relationship(back_populates="attempts")
    browser_events: Mapped[list["BrowserEvent"]] = relationship(back_populates="attempt")
    field_observations: Mapped[list["FormFieldObservation"]] = relationship(
        back_populates="attempt"
    )
