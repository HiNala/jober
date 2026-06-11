"""pack 20 queue and tenant-status composite indexes

Revision ID: r1a2b3c34d65
Revises: q9r0s1t32u63
Create Date: 2026-06-11

"""

from collections.abc import Sequence

from alembic import op

revision: str = "r1a2b3c34d65"
down_revision: str | None = "q9r0s1t32u63"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_job_targets_tenant_status",
        "job_targets",
        ["tenant_id", "status"],
        unique=False,
    )
    op.create_index(
        "ix_application_runs_tenant_status",
        "application_runs",
        ["tenant_id", "status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_application_runs_tenant_status", table_name="application_runs")
    op.drop_index("ix_job_targets_tenant_status", table_name="job_targets")
