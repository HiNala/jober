"""mission 25 in-house analytics foundation

Revision ID: m5a2n3l25y48
Revises: l4h1i2d23e47
Create Date: 2026-06-09

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "m5a2n3l25y48"
down_revision: str | None = "l4h1i2d23e47"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "analytics_events",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("tenant_id", sa.UUID(), nullable=True),
        sa.Column("anon_id", sa.String(length=64), nullable=True),
        sa.Column("session_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column(
            "props",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("page", sa.String(length=2048), nullable=True),
        sa.Column("referrer", sa.String(length=2048), nullable=True),
        sa.Column("utm_source", sa.String(length=255), nullable=True),
        sa.Column("utm_medium", sa.String(length=255), nullable=True),
        sa.Column("utm_campaign", sa.String(length=255), nullable=True),
        sa.Column("utm_term", sa.String(length=255), nullable=True),
        sa.Column("utm_content", sa.String(length=255), nullable=True),
        sa.Column("geo_country", sa.String(length=2), nullable=True),
        sa.Column("geo_region", sa.String(length=64), nullable=True),
        sa.Column("user_agent_family", sa.String(length=64), nullable=True),
        sa.Column("source", sa.String(length=16), nullable=False, server_default="client"),
        sa.Column("is_bot", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_internal", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_analytics_events_ts", "analytics_events", ["ts"])
    op.create_index("ix_analytics_events_name_ts", "analytics_events", ["name", "ts"])
    op.create_index("ix_analytics_events_session_ts", "analytics_events", ["session_id", "ts"])
    op.create_index("ix_analytics_events_user_ts", "analytics_events", ["user_id", "ts"])

    op.create_table(
        "analytics_daily_funnel",
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("step", sa.String(length=64), nullable=False),
        sa.Column("event_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unique_users", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unique_sessions", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("day", "step"),
        sa.UniqueConstraint("day", "step", name="uq_analytics_daily_funnel_day_step"),
    )

    op.create_table(
        "analytics_daily_page",
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("page", sa.String(length=2048), nullable=False),
        sa.Column("page_views", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unique_sessions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_time_on_page_sec", sa.Float(), nullable=False, server_default="0"),
        sa.Column("bounces", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("day", "page"),
        sa.UniqueConstraint("day", "page", name="uq_analytics_daily_page_day_page"),
    )

    op.create_table(
        "analytics_daily_active_users",
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("dau", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("wau", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("mau", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("day"),
    )

    op.create_table(
        "analytics_daily_cost",
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("agent_role", sa.String(length=64), nullable=False),
        sa.Column("model", sa.String(length=128), nullable=False),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completion_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cost_usd", sa.Float(), nullable=False, server_default="0"),
        sa.Column("llm_call_count", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("day", "tenant_id", "agent_role", "model"),
        sa.UniqueConstraint(
            "day",
            "tenant_id",
            "agent_role",
            "model",
            name="uq_analytics_daily_cost_day_tenant_agent_model",
        ),
    )


def downgrade() -> None:
    op.drop_table("analytics_daily_cost")
    op.drop_table("analytics_daily_active_users")
    op.drop_table("analytics_daily_page")
    op.drop_table("analytics_daily_funnel")
    op.drop_index("ix_analytics_events_user_ts", table_name="analytics_events")
    op.drop_index("ix_analytics_events_session_ts", table_name="analytics_events")
    op.drop_index("ix_analytics_events_name_ts", table_name="analytics_events")
    op.drop_index("ix_analytics_events_ts", table_name="analytics_events")
    op.drop_table("analytics_events")
