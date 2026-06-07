"""recovery mission 10

Revision ID: e7f1a2b34c90
Revises: d4e2b9c71a05
Create Date: 2026-06-08

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "e7f1a2b34c90"
down_revision: str | None = "d4e2b9c71a05"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "application_runs",
        sa.Column("checkpoint_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "application_attempts",
        sa.Column("failure_class", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "application_attempts",
        sa.Column(
            "self_assessment",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )
    op.create_table(
        "failure_events",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("job_target_id", sa.UUID(), nullable=False),
        sa.Column("run_id", sa.UUID(), nullable=True),
        sa.Column("platform", sa.String(length=64), nullable=False),
        sa.Column("failure_class", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["job_target_id"], ["job_targets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["run_id"], ["application_runs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_failure_events_platform_class",
        "failure_events",
        ["platform", "failure_class"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_failure_events_platform_class", table_name="failure_events")
    op.drop_table("failure_events")
    op.drop_column("application_attempts", "self_assessment")
    op.drop_column("application_attempts", "failure_class")
    op.drop_column("application_runs", "checkpoint_data")
