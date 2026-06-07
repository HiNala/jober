"""mission 15 tenancy

Revision ID: h0c5d6e67f03
Revises: g9b3c4d56e02
Create Date: 2026-06-07

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "h0c5d6e67f03"
down_revision: str | None = "g9b3c4d56e02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

DEFAULT_TENANT_ID = "00000000-0000-4000-8000-000000000001"
DEFAULT_USER_ID = "00000000-0000-4000-8000-000000000002"
DEFAULT_TENANT_POLICY = (
    '{"default_run_policy":"review_before_submit","auto_submit_opt_in":false}'
)


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("plan", sa.String(length=32), nullable=False, server_default="free"),
        sa.Column("stripe_customer_id", sa.String(length=255), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(length=255), nullable=True),
        sa.Column("policy", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("retention_days", sa.Integer(), nullable=True),
        sa.Column("subscription_ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("clerk_user_id", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("clerk_user_id", name="uq_users_clerk_user_id"),
    )
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])
    op.create_table(
        "audit_log_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_log_entries_tenant_id", "audit_log_entries", ["tenant_id"])

    op.execute(
        sa.text(
            """
            INSERT INTO tenants (id, name, plan, policy, created_at, updated_at)
            VALUES (CAST(:tid AS uuid), 'Local Dev', 'pro', CAST(:policy AS jsonb), now(), now())
            ON CONFLICT (id) DO NOTHING
            """
        ).bindparams(tid=DEFAULT_TENANT_ID, policy=DEFAULT_TENANT_POLICY)
    )

    for table in (
        "user_profiles",
        "job_targets",
        "resume_assets",
        "application_batches",
        "application_runs",
    ):
        op.add_column(
            table,
            sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True),
        )
        op.execute(
            sa.text(f"UPDATE {table} SET tenant_id = CAST(:tid AS uuid)").bindparams(
                tid=DEFAULT_TENANT_ID
            )
        )
        op.alter_column(table, "tenant_id", nullable=False)
        op.create_foreign_key(
            f"fk_{table}_tenant_id_tenants",
            table,
            "tenants",
            ["tenant_id"],
            ["id"],
            ondelete="CASCADE",
        )
        op.create_index(f"ix_{table}_tenant_id", table, ["tenant_id"])

    op.execute(
        sa.text(
            """
            INSERT INTO users (id, tenant_id, email, display_name, created_at, updated_at)
            VALUES (CAST(:uid AS uuid), CAST(:tid AS uuid), 'dev@jober.local', 'Local Dev',
                    now(), now())
            ON CONFLICT DO NOTHING
            """
        ).bindparams(uid=DEFAULT_USER_ID, tid=DEFAULT_TENANT_ID)
    )


def downgrade() -> None:
    for table in (
        "application_runs",
        "application_batches",
        "resume_assets",
        "job_targets",
        "user_profiles",
    ):
        op.drop_index(f"ix_{table}_tenant_id", table_name=table)
        op.drop_constraint(f"fk_{table}_tenant_id_tenants", table, type_="foreignkey")
        op.drop_column(table, "tenant_id")
    op.drop_index("ix_audit_log_entries_tenant_id", table_name="audit_log_entries")
    op.drop_table("audit_log_entries")
    op.drop_index("ix_users_tenant_id", table_name="users")
    op.drop_table("users")
    op.drop_table("tenants")
