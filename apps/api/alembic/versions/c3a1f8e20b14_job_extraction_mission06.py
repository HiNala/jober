"""job extraction mission 06

Revision ID: c3a1f8e20b14
Revises: b8f4a2c91d03
Create Date: 2026-06-07

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "c3a1f8e20b14"
down_revision: str | None = "b8f4a2c91d03"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "job_targets",
        sa.Column("extracted_job_profile", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "job_targets",
        sa.Column("platform_detection", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "job_targets",
        sa.Column("job_profile_extracted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column("job_targets", sa.Column("job_profile_cache_date", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("job_targets", "job_profile_cache_date")
    op.drop_column("job_targets", "job_profile_extracted_at")
    op.drop_column("job_targets", "platform_detection")
    op.drop_column("job_targets", "extracted_job_profile")
