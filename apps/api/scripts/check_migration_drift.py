#!/usr/bin/env python3
"""Exit non-zero when SQLAlchemy models drift from applied migrations."""

from __future__ import annotations

import asyncio
import sys

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import String
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql.sqltypes import Enum as SAEnum

from jober_api.config import settings
from jober_api.db.base import Base
from jober_api.models import (  # noqa: F401 — register metadata
    ApplicationAttempt,
    ApplicationRun,
    BrowserEvent,
    CompanyBoard,
    CoverLetterAngle,
    FormFieldObservation,
    GeneratedDocument,
    HumanCheckpoint,
    JobTarget,
    LlmCall,
    ResumeAsset,
    UserProfile,
)


def _flatten_diffs(diffs: list[object]) -> list[tuple[object, ...]]:
    flat: list[tuple[object, ...]] = []
    for item in diffs:
        if isinstance(item, list):
            flat.extend(entry for entry in item if isinstance(entry, tuple))
        elif isinstance(item, tuple):
            flat.append(item)
    return flat


def _benign_type_drift(diff: tuple[object, ...]) -> bool:
    """Migrations store enums as VARCHAR; ORM may still type them as Enum."""
    if diff[0] != "modify_type":
        return False
    existing, new = diff[5], diff[6]
    return isinstance(existing, String) and isinstance(new, SAEnum)


async def main() -> int:
    engine = create_async_engine(settings.database_url, connect_args={"ssl": False})
    async with engine.connect() as connection:

        def _diff(sync_conn):  # type: ignore[no-untyped-def]
            ctx = MigrationContext.configure(sync_conn)
            return compare_metadata(ctx, Base.metadata)

        raw_diffs = await connection.run_sync(_diff)
    await engine.dispose()

    diffs = _flatten_diffs(raw_diffs)
    material = [diff for diff in diffs if not _benign_type_drift(diff)]
    if material:
        print("Model/migration drift detected:", file=sys.stderr)
        for diff in material:
            print(f"  {diff}", file=sys.stderr)
        return 1

    print("No model/migration drift detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
