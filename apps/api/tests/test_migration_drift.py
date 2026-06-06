"""Regression tests for migration drift detection helpers."""

from sqlalchemy import String
from sqlalchemy.sql.sqltypes import Enum as SAEnum

from jober_api.db.migration_drift import (
    flatten_diffs,
    is_benign_enum_varchar_drift,
    material_diffs,
)
from jober_api.models.enums import AttemptStatus


def test_flatten_diffs_unwraps_nested_lists() -> None:
    inner = ("add_column", None, "t", "c")
    assert flatten_diffs([[inner]]) == [inner]
    assert flatten_diffs([inner]) == [inner]


def test_benign_enum_varchar_drift_filters_varchar_to_enum() -> None:
    diff = (
        "modify_type",
        None,
        "application_attempts",
        "status",
        {},
        String(32),
        SAEnum(AttemptStatus, native_enum=False, length=32),
    )
    assert is_benign_enum_varchar_drift(diff) is True
    assert material_diffs([[diff]]) == []


def test_material_diffs_keeps_real_column_adds() -> None:
    diff = ("add_column", None, "job_targets", "new_col")
    assert material_diffs([diff]) == [diff]
