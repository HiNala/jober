"""stripe webhook idempotency and tenant stripe index

Revision ID: s1t2r3i4p5e67
Revises: r1a2b3c34d65
Create Date: 2026-06-22

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "s1t2r3i4p5e67"
down_revision: str | None = "r1a2b3c34d65"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "processed_stripe_events",
        sa.Column("event_id", sa.String(length=255), nullable=False),
        sa.Column("event_type", sa.String(length=128), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("event_id"),
    )
    op.create_index(
        "ix_tenants_stripe_customer_id",
        "tenants",
        ["stripe_customer_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_tenants_stripe_customer_id", table_name="tenants")
    op.drop_table("processed_stripe_events")
