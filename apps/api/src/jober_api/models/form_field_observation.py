import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from jober_api.db.base import Base
from jober_api.models.constants import str_enum_column
from jober_api.models.enums import FieldObservationStatus
from jober_api.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from jober_api.models.application_attempt import ApplicationAttempt


class FormFieldObservation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "form_field_observations"

    attempt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("application_attempts.id", ondelete="CASCADE"),
        nullable=False,
    )
    field_key: Mapped[str] = mapped_column(String(255), nullable=False)
    label: Mapped[str | None] = mapped_column(String(512))
    field_type: Mapped[str | None] = mapped_column(String(64))
    required: Mapped[bool] = mapped_column(default=False, nullable=False)
    options: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    mapped_profile_field: Mapped[str | None] = mapped_column(String(128))
    proposed_value_redacted: Mapped[str | None] = mapped_column(String(512))
    confidence: Mapped[float | None] = mapped_column(Float)
    status: Mapped[FieldObservationStatus] = mapped_column(
        str_enum_column(FieldObservationStatus),
        default=FieldObservationStatus.SKIPPED,
        nullable=False,
    )
    evidence: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    attempt: Mapped["ApplicationAttempt"] = relationship(back_populates="field_observations")
