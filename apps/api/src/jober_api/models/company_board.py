from datetime import date

from sqlalchemy import Date, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from jober_api.db.base import Base
from jober_api.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class CompanyBoard(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "company_boards"

    priority: Mapped[str | None] = mapped_column(String(8))
    company_board: Mapped[str] = mapped_column(String(255), nullable=False)
    representative_roles: Mapped[str | None] = mapped_column(Text)
    stage_signal: Mapped[str | None] = mapped_column(String(255))
    why_save: Mapped[str | None] = mapped_column(Text)
    company_careers_url: Mapped[str | None] = mapped_column(Text)
    last_checked: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
