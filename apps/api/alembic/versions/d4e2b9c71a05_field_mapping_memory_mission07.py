"""field mapping memory mission 07

Revision ID: d4e2b9c71a05
Revises: c3a1f8e20b14
Create Date: 2026-06-07

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d4e2b9c71a05"
down_revision: str | None = "c3a1f8e20b14"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "field_mapping_memory",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("platform", sa.String(length=64), nullable=False),
        sa.Column("label_normalized", sa.String(length=512), nullable=False),
        sa.Column("mapped_profile_field", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("platform", "label_normalized", name="uq_field_mapping_platform_label"),
    )


def downgrade() -> None:
    op.drop_table("field_mapping_memory")
