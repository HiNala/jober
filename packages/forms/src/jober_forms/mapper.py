from __future__ import annotations

import re
from dataclasses import dataclass

from jober_forms.scanner import DiscoveredField, _DATE_HINTS, _SALARY_HINTS

LABEL_RULES: list[tuple[re.Pattern[str], str, float]] = [
    (re.compile(r"\b(e-?mail|email address)\b", re.I), "email", 0.92),
    (re.compile(r"\b(phone|mobile|telephone)\b", re.I), "phone", 0.9),
    (re.compile(r"\b(full name|your name|legal name)\b", re.I), "name", 0.9),
    (re.compile(r"\b(linkedin|portfolio|website|github)\b", re.I), "links", 0.85),
    (re.compile(r"\b(current title|job title|position)\b", re.I), "current_title", 0.82),
    (re.compile(r"\b(location|city|where do you live)\b", re.I), "location", 0.8),
    (re.compile(r"\b(notice period)\b", re.I), "notice_period", 0.88),
    (re.compile(r"\b(relocation|willing to relocate)\b", re.I), "relocation_pref", 0.85),
    (re.compile(r"\b(veteran|military)\b", re.I), "veteran_status", 0.9),
    (re.compile(r"\b(race|ethnicity)\b", re.I), "race_ethnicity", 0.9),
    (re.compile(r"\b(gender)\b", re.I), "gender", 0.9),
    (re.compile(r"\b(disability)\b", re.I), "disability", 0.9),
    (re.compile(r"\b(work authorization|authorized to work|legally authorized)\b", re.I), "work_authorization", 0.88),
    (re.compile(r"\b(sponsorship|visa)\b", re.I), "sponsorship_needed", 0.88),
    (re.compile(r"\b(salary|compensation|pay expectation)\b", re.I), "salary_prefs", 0.75),
    (re.compile(r"\b(why (do you want|this company)|motivation)\b", re.I), "why_this_company", 0.7),
    (re.compile(r"\b(tell us about yourself|about you)\b", re.I), "about_yourself", 0.7),
    (re.compile(r"\b(resume|cv)\b", re.I), "resume_upload", 0.85),
    (re.compile(r"\b(cover letter)\b", re.I), "cover_letter_upload", 0.85),
]

UPLOAD_FIELD_KEYS = {"resume_upload", "cover_letter_upload"}


@dataclass(frozen=True)
class FieldMapping:
    mapped_profile_field: str | None
    confidence: float
    mapping_evidence: list[str]
    ambiguous: bool


def _label_blob(field: DiscoveredField) -> str:
    parts = [field.label or "", field.field_key]
    parts.extend(ev.text for ev in field.evidence)
    return " ".join(parts)


def map_discovered_field(
    field: DiscoveredField,
    *,
    platform: str | None = None,
    memory_lookup: object | None = None,
) -> FieldMapping:
    blob = _label_blob(field)
    evidence: list[str] = []

    if field.is_upload or field.field_type == "file":
        if re.search(r"resume|cv", blob, re.I):
            return FieldMapping("resume_upload", 0.9, ["upload:resume"], False)
        if re.search(r"cover\s*letter", blob, re.I):
            return FieldMapping("cover_letter_upload", 0.9, ["upload:cover_letter"], False)
        return FieldMapping("unknown", 0.5, ["upload:unclassified"], True)

    if memory_lookup is not None and field.label:
        remembered = memory_lookup.lookup(platform or "generic", field.label)
        if remembered:
            evidence.append(f"memory:{remembered}")
            return FieldMapping(remembered, 0.95, evidence, False)

    best_key: str | None = None
    best_score = 0.0
    for pattern, key, score in LABEL_RULES:
        if pattern.search(blob):
            if score > best_score:
                best_key = key
                best_score = score
                evidence.append(f"label_rule:{key}")

    ambiguous = bool(_DATE_HINTS.search(blob) or _SALARY_HINTS.search(blob))
    if ambiguous:
        best_score = min(best_score, 0.55)
        evidence.append("ambiguous:date_or_salary")

    if best_key is None:
        return FieldMapping(None, 0.25, ["unknown"], True)

    if best_key in UPLOAD_FIELD_KEYS:
        return FieldMapping(best_key, best_score, evidence, False)

    return FieldMapping(best_key, best_score, evidence, ambiguous)
