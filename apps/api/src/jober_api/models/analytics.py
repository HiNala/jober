from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from jober_api.db.base import Base
from jober_api.models.mixins import UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    pass


class AnalyticsEvent(Base, UUIDPrimaryKeyMixin):
    """Append-only first-party analytics events. No raw IP is ever stored."""

    __tablename__ = "analytics_events"
    __table_args__ = (
        Index("ix_analytics_events_ts", "ts"),
        Index("ix_analytics_events_name_ts", "name", "ts"),
        Index("ix_analytics_events_session_ts", "session_id", "ts"),
        Index("ix_analytics_events_user_ts", "user_id", "ts"),
        Index("ix_analytics_events_tenant_ts", "tenant_id", "ts"),
    )

    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="SET NULL"),
        nullable=True,
    )
    anon_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    session_id: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    props: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    page: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    referrer: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    utm_source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    utm_medium: Mapped[str | None] = mapped_column(String(255), nullable=True)
    utm_campaign: Mapped[str | None] = mapped_column(String(255), nullable=True)
    utm_term: Mapped[str | None] = mapped_column(String(255), nullable=True)
    utm_content: Mapped[str | None] = mapped_column(String(255), nullable=True)
    geo_country: Mapped[str | None] = mapped_column(String(2), nullable=True)
    geo_region: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent_family: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source: Mapped[str] = mapped_column(String(16), nullable=False, default="client")
    is_bot: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_internal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class AnalyticsDailyFunnel(Base):
    __tablename__ = "analytics_daily_funnel"

    day: Mapped[date] = mapped_column(Date, primary_key=True)
    step: Mapped[str] = mapped_column(String(64), primary_key=True)
    event_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unique_users: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unique_sessions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class AnalyticsDailyPage(Base):
    __tablename__ = "analytics_daily_page"

    day: Mapped[date] = mapped_column(Date, primary_key=True)
    page: Mapped[str] = mapped_column(String(2048), primary_key=True)
    page_views: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unique_sessions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_time_on_page_sec: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    bounces: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class AnalyticsDailyActiveUsers(Base):
    __tablename__ = "analytics_daily_active_users"

    day: Mapped[date] = mapped_column(Date, primary_key=True)
    dau: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    wau: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    mau: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class AnalyticsDailyCost(Base):
    __tablename__ = "analytics_daily_cost"

    day: Mapped[date] = mapped_column(Date, primary_key=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        primary_key=True,
    )
    agent_role: Mapped[str] = mapped_column(String(64), primary_key=True)
    model: Mapped[str] = mapped_column(String(128), primary_key=True)
    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cost_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    llm_call_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
