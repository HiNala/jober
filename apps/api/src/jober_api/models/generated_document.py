import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from jober_api.db.base import Base
from jober_api.models.constants import str_enum_column
from jober_api.models.enums import DocumentType
from jober_api.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from jober_api.models.application_run import ApplicationRun
    from jober_api.models.job_target import JobTarget


class GeneratedDocument(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "generated_documents"

    job_target_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_targets.id", ondelete="CASCADE"),
        nullable=False,
    )
    run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("application_runs.id", ondelete="SET NULL"),
    )
    document_type: Mapped[DocumentType] = mapped_column(
        str_enum_column(DocumentType), nullable=False
    )
    object_key_pdf: Mapped[str | None] = mapped_column(String(512))
    object_key_docx: Mapped[str | None] = mapped_column(String(512))
    text: Mapped[str | None] = mapped_column(Text)
    keyword_coverage: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    ats_score: Mapped[float | None] = mapped_column(Float)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    job_target: Mapped["JobTarget"] = relationship(back_populates="generated_documents")
    run: Mapped["ApplicationRun | None"] = relationship(back_populates="generated_documents")
