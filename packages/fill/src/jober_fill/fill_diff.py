from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from jober_forms.redact import redact_value


@dataclass(frozen=True)
class FillDiff:
    proposed_redacted: str | None
    actual_redacted: str | None
    locator_strategy: str | None
    matched: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_compare(value: str | None) -> str:
    if not value:
        return ""
    return "".join(value.split()).casefold()


def build_fill_diff(
    *,
    proposed: object | None,
    actual: object | None,
    field_type: str | None,
    locator_strategy: str | None,
) -> FillDiff:
    proposed_text = str(proposed).strip() if proposed is not None else None
    actual_text = str(actual).strip() if actual is not None else None
    return FillDiff(
        proposed_redacted=redact_value(proposed_text, field_type=field_type),
        actual_redacted=redact_value(actual_text, field_type=field_type),
        locator_strategy=locator_strategy,
        matched=_normalize_compare(proposed_text) == _normalize_compare(actual_text),
    )
