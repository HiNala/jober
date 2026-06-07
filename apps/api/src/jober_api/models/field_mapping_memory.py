from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from jober_api.db.base import Base
from jober_api.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class FieldMappingMemory(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "field_mapping_memory"
    __table_args__ = (
        UniqueConstraint("platform", "label_normalized", name="uq_field_mapping_platform_label"),
    )

    platform: Mapped[str] = mapped_column(String(64), nullable=False)
    label_normalized: Mapped[str] = mapped_column(String(512), nullable=False)
    mapped_profile_field: Mapped[str] = mapped_column(String(128), nullable=False)
