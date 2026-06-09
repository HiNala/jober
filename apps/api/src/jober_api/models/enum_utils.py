from __future__ import annotations

from enum import StrEnum


def enum_value(value: StrEnum | str) -> str:
    """Serialize a StrEnum member or a plain DB string to its wire value."""
    if isinstance(value, StrEnum):
        return value.value
    return str(value)
