"""pack 08 pro waitlist

Revision ID: q9r0s1t32u63
Revises: p8q9r0s31t62
Create Date: 2026-06-11

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "q9r0s1t32u63"
down_revision: str | None = "p8q9r0s31t62"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "pro_waitlist_entries",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("consent_contact", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_pro_waitlist_email"),
    )


def downgrade() -> None:
    op.drop_table("pro_waitlist_entries")
