#!/usr/bin/env python3
"""Exit non-zero when SQLAlchemy models drift from applied migrations."""

from __future__ import annotations

import asyncio
import sys

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy.ext.asyncio import create_async_engine

from jober_api.config import settings
from jober_api.db.base import Base
from jober_api.db.migration_drift import material_diffs
from jober_api.models import (  # noqa: F401 — register metadata
    ApplicationAttempt,
    ApplicationBatch,
    ApplicationRun,
    AuthIdentity,
    AuthToken,
    BatchItem,
    BrowserEvent,
    CompanyBoard,
    CoverLetterAngle,
    FieldMappingMemory,
    FormFieldObservation,
    GeneratedDocument,
    HumanCheckpoint,
    JobList,
    JobListItem,
    JobTarget,
    LlmCall,
    ResumeAsset,
    RunEvent,
    Tenant,
    User,
    UserPreferences,
    UserProfile,
    UserProviderKey,
)


async def main() -> int:
    engine = create_async_engine(settings.database_url, connect_args={"ssl": False})
    async with engine.connect() as connection:

        def _diff(sync_conn):  # type: ignore[no-untyped-def]
            ctx = MigrationContext.configure(sync_conn)
            return compare_metadata(ctx, Base.metadata)

        raw_diffs = await connection.run_sync(_diff)
    await engine.dispose()

    drift = material_diffs(raw_diffs)
    if drift:
        print("Model/migration drift detected:", file=sys.stderr)
        for diff in drift:
            print(f"  {diff}", file=sys.stderr)
        return 1

    print("No model/migration drift detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
