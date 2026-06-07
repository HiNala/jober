from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from jober_fill.fill_diff import FillDiff, build_fill_diff


class FillActions(Protocol):
    def fill_by_label(self, label: str, value: str) -> tuple[str, str | None]: ...
    def select_by_label(self, label: str, value: str) -> tuple[str, str | None]: ...
    def check_by_label(self, label: str, *, checked: bool = True) -> tuple[str, str | None]: ...
    def upload_file(
        self, control: str, file_path: str, *, field_key: str | None = None
    ) -> tuple[str, str | None]: ...
    def read_value_by_label(self, label: str) -> str | None: ...


UPLOAD_FIELDS = frozenset({"resume_upload", "cover_letter_upload"})


@dataclass
class FieldFillOutcome:
    field_key: str
    status: str
    locator_strategy: str | None = None
    fill_diff: FillDiff | None = None
    error: str | None = None
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ObservationInput:
    field_key: str
    label: str | None
    field_type: str | None
    mapped_profile_field: str | None
    status: str
    is_sensitive: bool = False


def _is_eligible(obs: ObservationInput) -> bool:
    if obs.status == "skipped":
        return True
    if obs.mapped_profile_field in UPLOAD_FIELDS and obs.status == "needs_review":
        return True
    return False


def run_fill_loop(
    observations: list[ObservationInput],
    values: dict[str, Any],
    file_paths: dict[str, str],
    actions: FillActions,
) -> list[FieldFillOutcome]:
    outcomes: list[FieldFillOutcome] = []
    for obs in observations:
        if obs.is_sensitive and obs.status == "needs_review":
            outcomes.append(
                FieldFillOutcome(
                    field_key=obs.field_key,
                    status="needs_review",
                    error="sensitive_field_checkpoint",
                    evidence={"reason": "sensitive_needs_human"},
                )
            )
            continue
        if not _is_eligible(obs):
            continue

        mapped = obs.mapped_profile_field
        if not mapped:
            outcomes.append(
                FieldFillOutcome(
                    field_key=obs.field_key,
                    status="failed",
                    error="unmapped_field",
                )
            )
            continue

        if mapped in UPLOAD_FIELDS:
            path = file_paths.get(mapped)
            if not path:
                outcomes.append(
                    FieldFillOutcome(
                        field_key=obs.field_key,
                        status="failed",
                        error="missing_upload_file",
                    )
                )
                continue
            control = obs.label or obs.field_key
            try:
                strategy, _ = actions.upload_file(control, path, field_key=obs.field_key)
                actual = actions.read_value_by_label(control) if obs.label else None
                diff = build_fill_diff(
                    proposed="[file upload]",
                    actual=actual or "[attached]",
                    field_type="file",
                    locator_strategy=strategy,
                )
                outcomes.append(
                    FieldFillOutcome(
                        field_key=obs.field_key,
                        status="filled",
                        locator_strategy=strategy,
                        fill_diff=diff,
                        evidence={"fill_diff": diff.to_dict()},
                    )
                )
            except Exception as exc:  # noqa: BLE001 — collect per-field failures
                outcomes.append(
                    FieldFillOutcome(
                        field_key=obs.field_key,
                        status="failed",
                        error=str(exc),
                    )
                )
            continue

        value = values.get(mapped)
        if value in (None, ""):
            outcomes.append(
                FieldFillOutcome(
                    field_key=obs.field_key,
                    status="failed",
                    error="no_value",
                )
            )
            continue

        label = obs.label or obs.field_key
        ftype = (obs.field_type or "text").lower()
        try:
            if ftype == "select":
                strategy, _ = actions.select_by_label(label, str(value))
            elif ftype == "checkbox":
                strategy, _ = actions.check_by_label(label, checked=bool(value))
            else:
                strategy, _ = actions.fill_by_label(label, str(value))
            actual = actions.read_value_by_label(label)
            diff = build_fill_diff(
                proposed=value,
                actual=actual,
                field_type=ftype,
                locator_strategy=strategy,
            )
            outcomes.append(
                FieldFillOutcome(
                    field_key=obs.field_key,
                    status="filled" if diff.matched or actual else "filled",
                    locator_strategy=strategy,
                    fill_diff=diff,
                    evidence={"fill_diff": diff.to_dict()},
                )
            )
        except Exception as exc:  # noqa: BLE001
            outcomes.append(
                FieldFillOutcome(
                    field_key=obs.field_key,
                    status="failed",
                    error=str(exc),
                )
            )
    return outcomes
