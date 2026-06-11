from __future__ import annotations

from sqlalchemy import Boolean, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from jober_api.db.base import Base
from jober_api.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class ProWaitlistEntry(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Pro plan interest capture from public pricing — not tied to a user account."""

    __tablename__ = "pro_waitlist_entries"
    __table_args__ = (UniqueConstraint("email", name="uq_pro_waitlist_email"),)

    email: Mapped[str] = mapped_column(String(320), nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False, default="pricing")
    consent_contact: Mapped[bool] = mapped_column(Boolean, nullable=False)
