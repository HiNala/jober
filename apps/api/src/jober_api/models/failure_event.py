import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from jober_api.db.base import Base
from jober_api.models.mixins import UUIDPrimaryKeyMixin


class FailureEvent(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "failure_events"
    __table_args__ = (
        Index("ix_failure_events_platform_class", "platform", "failure_class"),
    )

    job_target_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_targets.id", ondelete="CASCADE"),
        nullable=False,
    )
    run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("application_runs.id", ondelete="SET NULL"),
    )
    platform: Mapped[str] = mapped_column(String(64), nullable=False)
    failure_class: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
