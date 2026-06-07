from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from jober_api.services.claims_index import validate_claims


@dataclass(frozen=True)
class DraftLetter:
    body: str
    asserted_facts: list[str]
    paragraph_grounding: list[dict[str, Any]]


@dataclass(frozen=True)
class ClaimsGuardResult:
    ok: bool
    unsupported: list[str]
    draft: DraftLetter


def parse_draft_payload(raw: str) -> DraftLetter:
    data = json.loads(raw)
    body = str(data.get("body", "")).strip()
    facts = [str(f) for f in data.get("asserted_facts", []) if str(f).strip()]
    grounding = data.get("paragraph_grounding", [])
    if not isinstance(grounding, list):
        grounding = []
    return DraftLetter(body=body, asserted_facts=facts, paragraph_grounding=grounding)


def verify_draft_claims(
    draft: DraftLetter,
    claims_index: dict[str, Any],
) -> ClaimsGuardResult:
    unsupported = validate_claims(claims_index, draft.asserted_facts)
    return ClaimsGuardResult(ok=not unsupported, unsupported=unsupported, draft=draft)
