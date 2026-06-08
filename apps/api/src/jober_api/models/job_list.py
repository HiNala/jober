from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from jober_api.db.base import Base
from jober_api.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from jober_api.models.job_target import JobTarget
    from jober_api.models.user import User


class JobList(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "job_lists"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(512))
    archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    items: Mapped[list[JobListItem]] = relationship(
        back_populates="job_list",
        cascade="all, delete-orphan",
        order_by="JobListItem.sort_order",
    )
    user: Mapped[User] = relationship(back_populates="job_lists")


class JobListItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "job_list_items"
    __table_args__ = (
        UniqueConstraint("job_list_id", "job_target_id", name="uq_job_list_items_list_job"),
    )

    job_list_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_lists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_target_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_targets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    job_list: Mapped[JobList] = relationship(back_populates="items")
    job_target: Mapped[JobTarget] = relationship()
