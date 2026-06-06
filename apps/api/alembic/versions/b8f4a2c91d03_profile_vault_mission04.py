"""profile vault mission 04

Revision ID: b8f4a2c91d03
Revises: 42c29075a206
Create Date: 2026-06-06

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b8f4a2c91d03"
down_revision: str | Sequence[str] | None = "42c29075a206"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("user_profiles", sa.Column("current_title", sa.String(length=255), nullable=True))
    op.add_column("user_profiles", sa.Column("notice_period", sa.String(length=128), nullable=True))
    op.create_table(
        "profile_common_answers",
        sa.Column("user_profile_id", sa.UUID(), nullable=False),
        sa.Column("answer_key", sa.String(length=128), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
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
        sa.ForeignKeyConstraint(["user_profile_id"], ["user_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_profile_id", "answer_key", name="uq_profile_common_answers_key"),
    )


def downgrade() -> None:
    op.drop_table("profile_common_answers")
    op.drop_column("user_profiles", "notice_period")
    op.drop_column("user_profiles", "current_title")
