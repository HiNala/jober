from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import CITEXT, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from jober_api.db.base import Base
from jober_api.models.enums import UserRole, UserStatus
from jober_api.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from jober_api.models.auth_identity import AuthIdentity
    from jober_api.models.auth_token import AuthToken
    from jober_api.models.job_list import JobList
    from jober_api.models.saved_search import SavedSearch
    from jober_api.models.tenant import Tenant
    from jober_api.models.user_preferences import UserPreferences
    from jober_api.models.user_provider_key import UserProviderKey


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("clerk_user_id", name="uq_users_clerk_user_id"),
        UniqueConstraint("email", name="uq_users_email"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    clerk_user_id: Mapped[str | None] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(CITEXT, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255))
    password_hash: Mapped[str | None] = mapped_column(String(255))
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[UserStatus] = mapped_column(
        String(32),
        nullable=False,
        default=UserStatus.PENDING_VERIFICATION,
    )
    role: Mapped[UserRole] = mapped_column(String(32), nullable=False, default=UserRole.USER)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    totp_secret: Mapped[str | None] = mapped_column(String(255))

    tenant: Mapped[Tenant] = relationship(back_populates="users")
    auth_tokens: Mapped[list[AuthToken]] = relationship(back_populates="user")
    auth_identities: Mapped[list[AuthIdentity]] = relationship(back_populates="user")
    preferences: Mapped[UserPreferences | None] = relationship(
        back_populates="user",
        uselist=False,
    )
    provider_keys: Mapped[list[UserProviderKey]] = relationship(back_populates="user")
    job_lists: Mapped[list[JobList]] = relationship(back_populates="user")
    saved_searches: Mapped[list[SavedSearch]] = relationship(back_populates="user")
