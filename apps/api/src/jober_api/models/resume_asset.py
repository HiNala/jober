from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from jober_api.db.base import Base
from jober_api.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from jober_api.models.user_profile import UserProfile


class ResumeAsset(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "resume_assets"

    object_key: Mapped[str] = mapped_column(String(512), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    extracted_text: Mapped[str | None] = mapped_column(Text)
    skills_index: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    embedding_id: Mapped[str | None] = mapped_column(String(128))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    profiles_as_default: Mapped[list["UserProfile"]] = relationship(
        back_populates="default_resume_asset",
        foreign_keys="UserProfile.default_resume_asset_id",
    )
