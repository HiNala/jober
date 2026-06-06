import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from jober_api.db.base import Base
from jober_api.models.constants import str_enum_column
from jober_api.models.enums import CheckpointStatus, CheckpointType
from jober_api.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from jober_api.models.application_run import ApplicationRun


class HumanCheckpoint(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "human_checkpoints"

    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("application_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    checkpoint_type: Mapped[CheckpointType] = mapped_column(
        str_enum_column(CheckpointType), nullable=False
    )
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    resolved_value: Mapped[str | None] = mapped_column(Text)
    status: Mapped[CheckpointStatus] = mapped_column(
        str_enum_column(CheckpointStatus),
        default=CheckpointStatus.OPEN,
        nullable=False,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    run: Mapped["ApplicationRun"] = relationship(back_populates="checkpoints")
