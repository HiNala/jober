import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from jober_api.db.base import Base
from jober_api.models.mixins import UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from jober_api.models.application_run import ApplicationRun
    from jober_api.models.browser_event import BrowserEvent


class LlmCall(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "llm_calls"
    __table_args__ = (Index("ix_llm_calls_created_at", "created_at"),)

    run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("application_runs.id", ondelete="SET NULL"),
    )
    agent_role: Mapped[str] = mapped_column(String(64), nullable=False)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer)
    completion_tokens: Mapped[int | None] = mapped_column(Integer)
    cost_usd: Mapped[float | None] = mapped_column(Float)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    redacted_prompt: Mapped[str | None] = mapped_column(Text)
    redacted_response: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    run: Mapped["ApplicationRun | None"] = relationship(back_populates="llm_calls")
    browser_events: Mapped[list["BrowserEvent"]] = relationship(back_populates="llm_call")
