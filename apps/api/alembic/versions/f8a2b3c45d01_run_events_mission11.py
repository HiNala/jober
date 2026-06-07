"""run events mission 11

Revision ID: f8a2b3c45d01
Revises: e7f1a2b34c90
Create Date: 2026-06-08

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "f8a2b3c45d01"
down_revision: str | None = "e7f1a2b34c90"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "run_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("seq", sa.BigInteger(), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("level", sa.String(length=16), nullable=False, server_default="info"),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("screenshot_key", sa.String(length=512), nullable=True),
        sa.Column("attempt_index", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["run_id"], ["application_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("run_id", "seq", name="uq_run_events_run_seq"),
    )
    op.create_index("ix_run_events_run_id_seq", "run_events", ["run_id", "seq"])


def downgrade() -> None:
    op.drop_index("ix_run_events_run_id_seq", table_name="run_events")
    op.drop_table("run_events")
