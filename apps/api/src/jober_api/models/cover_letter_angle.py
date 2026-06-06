from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from jober_api.db.base import Base
from jober_api.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class CoverLetterAngle(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "cover_letter_angles"

    use_case: Mapped[str] = mapped_column(String(255), nullable=False)
    template: Mapped[str] = mapped_column(Text, nullable=False)
