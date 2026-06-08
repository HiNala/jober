from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from jober_api.config import settings
from jober_api.crypto.encrypted import EncryptedText
from jober_api.db.base import Base
from jober_api.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from jober_api.models.user import User


class UserProviderKey(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "user_provider_keys"
    __table_args__ = (
        UniqueConstraint("user_id", "provider", name="uq_user_provider_keys_user_provider"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    encrypted_api_key: Mapped[str | None] = mapped_column(
        EncryptedText(lambda: settings.vault_encryption_key)
    )
    key_hint: Mapped[str | None] = mapped_column(String(8))

    user: Mapped[User] = relationship(back_populates="provider_keys")
