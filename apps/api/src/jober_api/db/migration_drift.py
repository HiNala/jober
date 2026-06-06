"""Compare applied migrations against SQLAlchemy metadata."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.sql.sqltypes import Enum as SAEnum


def flatten_diffs(diffs: list[object]) -> list[tuple[object, ...]]:
    """Alembic may return nested lists; normalize to flat tuples."""
    flat: list[tuple[object, ...]] = []
    for item in diffs:
        if isinstance(item, list):
            flat.extend(entry for entry in item if isinstance(entry, tuple))
        elif isinstance(item, tuple):
            flat.append(item)
    return flat


def is_benign_enum_varchar_drift(diff: tuple[object, ...]) -> bool:
    """Migrations store enums as VARCHAR; ORM metadata may still type them as Enum."""
    if diff[0] != "modify_type":
        return False
    existing, new = diff[5], diff[6]
    return isinstance(existing, String) and isinstance(new, SAEnum)


def material_diffs(diffs: list[object]) -> list[tuple[object, ...]]:
    """Return diffs that represent real schema drift (not VARCHAR/Enum equivalence)."""
    return [diff for diff in flatten_diffs(diffs) if not is_benign_enum_varchar_drift(diff)]
