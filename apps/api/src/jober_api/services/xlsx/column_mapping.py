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
    if cell.startswith(f"{candidate} ") or cell.endswith(f" {candidate}"):
        return 0.95
    cell_words = cell.split()
    cand_words = candidate.split()
    if cand_words == cell_words[: len(cand_words)]:
        return 0.93
    if candidate in cell_words:
        return 0.88
    if cell in candidate:
        return 0.85
    if candidate in cell:
        # Penalize long headers where the alias is only a prefix word (e.g. "company" in
        # "company careers ats url").
        extra_words = max(0, len(cell_words) - len(cand_words))
        return max(0.72, 0.9 - 0.08 * extra_words)
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

        candidates: list[tuple[float, str, str]] = []
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
            if best_score >= 0.72 and best_header:
                candidates.append((best_score, col_spec.field, best_header))

        candidates.sort(reverse=True)
        field_to_header: dict[str, str | None] = {col.field: None for col in spec.columns}
        scores: dict[str, float] = {col.field: 0.0 for col in spec.columns}
        used_fields: set[str] = set()
        used_headers: set[str] = set()
        for score, field, header in candidates:
            if field in used_fields or header in used_headers:
                continue
            field_to_header[field] = header
            scores[field] = score
            used_fields.add(field)
            used_headers.add(header)

        matched = len(used_fields)

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
