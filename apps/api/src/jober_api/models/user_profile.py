import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from jober_api.config import settings
from jober_api.crypto.encrypted import EncryptedText
from jober_api.db.base import Base
from jober_api.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from jober_api.models.profile_common_answer import ProfileCommonAnswer
    from jober_api.models.resume_asset import ResumeAsset


class UserProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "user_profiles"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str | None] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(320))
    phone: Mapped[str | None] = mapped_column(String(64))
    location: Mapped[str | None] = mapped_column(String(255))
    current_title: Mapped[str | None] = mapped_column(String(255))
    notice_period: Mapped[str | None] = mapped_column(String(128))
    links: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    work_authorization: Mapped[str | None] = mapped_column(Text)
    relocation_pref: Mapped[bool | None] = mapped_column()
    onsite_pref: Mapped[bool | None] = mapped_column()
    hybrid_pref: Mapped[bool | None] = mapped_column()
    salary_prefs: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    sensitive_eeo_answers: Mapped[str | None] = mapped_column(
        EncryptedText(lambda: settings.vault_encryption_key)
    )
    default_resume_asset_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resume_assets.id", ondelete="SET NULL"),
    )
    cover_letter_style_prefs: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    profile_completeness_score: Mapped[float | None] = mapped_column(Float)
    field_consent: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    default_resume_asset: Mapped["ResumeAsset | None"] = relationship(
        back_populates="profiles_as_default",
        foreign_keys=[default_resume_asset_id],
    )
    common_answers: Mapped[list["ProfileCommonAnswer"]] = relationship(
        back_populates="profile",
        cascade="all, delete-orphan",
    )
