"""mission 32 performance indexes

Revision ID: p8q9r0s31t62
Revises: o7c5p6q28b60
Create Date: 2026-06-10

"""

from collections.abc import Sequence

from alembic import op

revision: str = "p8q9r0s31t62"
down_revision: str | None = "o7c5p6q28b60"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_analytics_events_tenant_ts",
        "analytics_events",
        ["tenant_id", "ts"],
        unique=False,
    )
    op.create_index(
        "ix_batch_items_batch_status",
        "batch_items",
        ["batch_id", "status"],
        unique=False,
    )
    op.create_index(
        "ix_llm_calls_created_at",
        "llm_calls",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_llm_calls_created_at", table_name="llm_calls")
    op.drop_index("ix_batch_items_batch_status", table_name="batch_items")
    op.drop_index("ix_analytics_events_tenant_ts", table_name="analytics_events")
