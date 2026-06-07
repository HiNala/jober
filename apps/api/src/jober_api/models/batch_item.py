import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from jober_api.db.base import Base
from jober_api.models.constants import str_enum_column
from jober_api.models.enums import BatchItemStatus
from jober_api.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from jober_api.models.application_batch import ApplicationBatch
    from jober_api.models.application_run import ApplicationRun
    from jober_api.models.job_target import JobTarget


class BatchItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "batch_items"
    __table_args__ = (
        UniqueConstraint("batch_id", "job_target_id", name="uq_batch_items_batch_job"),
    )

    batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("application_batches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_target_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_targets.id", ondelete="CASCADE"),
        nullable=False,
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[BatchItemStatus] = mapped_column(
        str_enum_column(BatchItemStatus), default=BatchItemStatus.PENDING, nullable=False
    )
    domain: Mapped[str] = mapped_column(String(255), nullable=False)
    run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("application_runs.id", ondelete="SET NULL"),
    )
    skip_reason: Mapped[str | None] = mapped_column(String(512))

    batch: Mapped["ApplicationBatch"] = relationship(back_populates="items")
    job_target: Mapped["JobTarget"] = relationship()
    run: Mapped["ApplicationRun | None"] = relationship(foreign_keys=[run_id])
