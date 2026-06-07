"""batch ops mission 13

Revision ID: g9b3c4d56e02
Revises: f8a2b3c45d01
Create Date: 2026-06-07

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "g9b3c4d56e02"
down_revision: str | None = "f8a2b3c45d01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "application_batches",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("policy", sa.String(length=32), nullable=False, server_default="review_before_submit"),
        sa.Column("filters", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("quiet_hours_start", sa.String(length=8), nullable=True),
        sa.Column("quiet_hours_end", sa.String(length=8), nullable=True),
        sa.Column("max_concurrency", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("site_cooldown_seconds", sa.Float(), nullable=False, server_default="30"),
        sa.Column("action_delay_ms", sa.Integer(), nullable=False, server_default="500"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "batch_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("batch_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_target_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("domain", sa.String(length=255), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("skip_reason", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["batch_id"], ["application_batches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_target_id"], ["job_targets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["run_id"], ["application_runs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("batch_id", "job_target_id", name="uq_batch_items_batch_job"),
    )
    op.create_index("ix_batch_items_batch_id", "batch_items", ["batch_id"])
    op.add_column(
        "application_runs",
        sa.Column("batch_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_application_runs_batch_id",
        "application_runs",
        "application_batches",
        ["batch_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_application_runs_batch_id", "application_runs", ["batch_id"])


def downgrade() -> None:
    op.drop_index("ix_application_runs_batch_id", table_name="application_runs")
    op.drop_constraint("fk_application_runs_batch_id", "application_runs", type_="foreignkey")
    op.drop_column("application_runs", "batch_id")
    op.drop_index("ix_batch_items_batch_id", table_name="batch_items")
    op.drop_table("batch_items")
    op.drop_table("application_batches")
