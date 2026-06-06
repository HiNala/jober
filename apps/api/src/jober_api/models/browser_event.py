import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from jober_api.db.base import Base
from jober_api.models.mixins import UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from jober_api.models.application_attempt import ApplicationAttempt
    from jober_api.models.llm_call import LlmCall


class BrowserEvent(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "browser_events"
    __table_args__ = (Index("ix_browser_events_attempt_id", "attempt_id"),)

    attempt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("application_attempts.id", ondelete="CASCADE"),
        nullable=False,
    )
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    level: Mapped[str] = mapped_column(String(16), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    message: Mapped[str | None] = mapped_column(Text)
    selector: Mapped[str | None] = mapped_column(String(512))
    url: Mapped[str | None] = mapped_column(Text)
    screenshot_key: Mapped[str | None] = mapped_column(String(512))
    llm_call_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("llm_calls.id", ondelete="SET NULL"),
    )
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB)

    attempt: Mapped["ApplicationAttempt"] = relationship(back_populates="browser_events")
    llm_call: Mapped["LlmCall | None"] = relationship(back_populates="browser_events")
