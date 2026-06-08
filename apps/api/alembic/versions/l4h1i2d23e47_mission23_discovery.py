"""mission 23 discovery saved searches

Revision ID: l4h1i2d23e47
Revises: k3g9h0c12d36
Create Date: 2026-06-08

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "l4h1i2d23e47"
down_revision: str | None = "k3g9h0c12d36"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("company_boards", sa.Column("tenant_id", sa.UUID(), nullable=True))
    op.execute(
        sa.text(
            "UPDATE company_boards SET tenant_id = "
            "(SELECT id FROM tenants ORDER BY created_at LIMIT 1) "
            "WHERE tenant_id IS NULL"
        )
    )
    op.alter_column("company_boards", "tenant_id", nullable=False)
    op.create_foreign_key(
        "fk_company_boards_tenant_id",
        "company_boards",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_company_boards_tenant_id", "company_boards", ["tenant_id"])

    op.create_table(
        "saved_searches",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("query", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
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
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_saved_searches_tenant_id", "saved_searches", ["tenant_id"])
    op.create_index("ix_saved_searches_user_id", "saved_searches", ["user_id"])

    op.add_column("job_lists", sa.Column("saved_search_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "fk_job_lists_saved_search_id",
        "job_lists",
        "saved_searches",
        ["saved_search_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_job_lists_saved_search_id", "job_lists", type_="foreignkey")
    op.drop_column("job_lists", "saved_search_id")
    op.drop_index("ix_saved_searches_user_id", table_name="saved_searches")
    op.drop_index("ix_saved_searches_tenant_id", table_name="saved_searches")
    op.drop_table("saved_searches")
    op.drop_index("ix_company_boards_tenant_id", table_name="company_boards")
    op.drop_constraint("fk_company_boards_tenant_id", "company_boards", type_="foreignkey")
    op.drop_column("company_boards", "tenant_id")
