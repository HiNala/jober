import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from jober_api.db.base import Base
from jober_api.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from jober_api.models.user_profile import UserProfile


class ProfileCommonAnswer(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "profile_common_answers"
    __table_args__ = (
        UniqueConstraint("user_profile_id", "answer_key", name="uq_profile_common_answers_key"),
    )

    user_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    answer_key: Mapped[str] = mapped_column(String(128), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    profile: Mapped["UserProfile"] = relationship(back_populates="common_answers")
