from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher

from jober_api.services.xlsx.sheet_specs import SheetSpec


def _normalize_header(value: object) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"[/\\]+", " ", text)
    text = re.sub(r"[^\w\s]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def _score_header(cell: str, candidate: str) -> float:
    if not cell or not candidate:
        return 0.0
    if cell == candidate:
        return 1.0
    if candidate in cell or cell in candidate:
        return 0.92
    return SequenceMatcher(None, cell, candidate).ratio()


@dataclass(frozen=True)
class ResolvedColumnMapping:
    sheet: str
    header_row: int
    fields: dict[str, str | None]
    scores: dict[str, float]


def resolve_sheet_mapping(
    sheet_name: str,
    rows: list[tuple[object, ...]],
    spec: SheetSpec,
    *,
    max_scan_rows: int = 15,
) -> ResolvedColumnMapping | None:
    best: ResolvedColumnMapping | None = None
    scan_limit = min(max_scan_rows, len(rows))

    for row_idx in range(scan_limit):
        row = rows[row_idx]
        normalized = [_normalize_header(cell) for cell in row]
        if not any(normalized):
            continue

        field_to_header: dict[str, str | None] = {}
        scores: dict[str, float] = {}
        matched = 0

        for col_spec in spec.columns:
            best_score = 0.0
            best_header: str | None = None
            for header_cell, raw in zip(normalized, row, strict=False):
                if not header_cell:
                    continue
                for alias in col_spec.aliases:
                    alias_norm = _normalize_header(alias)
                    score = _score_header(header_cell, alias_norm)
                    if score > best_score:
                        best_score = score
                        best_header = str(raw).strip() if raw is not None else None
            field_to_header[col_spec.field] = best_header if best_score >= 0.72 else None
            scores[col_spec.field] = best_score
            if best_score >= 0.72:
                matched += 1

        if matched < spec.min_matches:
            continue

        candidate = ResolvedColumnMapping(
            sheet=sheet_name,
            header_row=row_idx,
            fields=field_to_header,
            scores=scores,
        )
        if best is None or matched > sum(1 for s in best.scores.values() if s >= 0.72):
            best = candidate

    return best


def mapping_preview(spec: SheetSpec, resolved: ResolvedColumnMapping) -> list[dict[str, object]]:
    preview: list[dict[str, object]] = []
    for col in spec.columns:
        preview.append(
            {
                "field": col.field,
                "matched_header": resolved.fields.get(col.field),
                "confidence": round(resolved.scores.get(col.field, 0.0), 3),
                "required": col.required,
            }
        )
    return preview
