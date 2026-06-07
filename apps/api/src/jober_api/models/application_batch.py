from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from jober_api.db.base import Base
from jober_api.models.constants import str_enum_column
from jober_api.models.enums import BatchStatus, RunPolicy
from jober_api.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from jober_api.models.application_run import ApplicationRun
    from jober_api.models.batch_item import BatchItem


class ApplicationBatch(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "application_batches"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[BatchStatus] = mapped_column(
        str_enum_column(BatchStatus), default=BatchStatus.DRAFT, nullable=False
    )
    policy: Mapped[RunPolicy] = mapped_column(
        str_enum_column(RunPolicy),
        default=RunPolicy.REVIEW_BEFORE_SUBMIT,
        nullable=False,
    )
    filters: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    quiet_hours_start: Mapped[str | None] = mapped_column(String(8))
    quiet_hours_end: Mapped[str | None] = mapped_column(String(8))
    max_concurrency: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    site_cooldown_seconds: Mapped[float] = mapped_column(Float, default=30.0, nullable=False)
    action_delay_ms: Mapped[int] = mapped_column(Integer, default=500, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)

    items: Mapped[list["BatchItem"]] = relationship(back_populates="batch")
    runs: Mapped[list["ApplicationRun"]] = relationship(back_populates="batch")
