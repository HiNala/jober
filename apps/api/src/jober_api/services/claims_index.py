from __future__ import annotations

import re
from typing import Any


def build_claims_index(extracted_text: str, skills_index: dict[str, Any] | None) -> dict[str, Any]:
    normalized = re.sub(r"\s+", " ", extracted_text or "").casefold()
    skills = []
    if skills_index and isinstance(skills_index.get("skills"), list):
        skills = [str(s) for s in skills_index["skills"]]
    tokens = set(re.findall(r"[a-z0-9+#.]{2,}", normalized))
    return {
        "normalized_text": normalized,
        "skills": skills,
        "tokens": sorted(tokens),
    }


def claim_supported(claims_index: dict[str, Any], claim: str) -> bool:
    needle = re.sub(r"\s+", " ", claim.strip()).casefold()
    if not needle:
        return False
    if needle in claims_index.get("normalized_text", ""):
        return True
    for skill in claims_index.get("skills", []):
        if needle == str(skill).casefold():
            return True
    tokens = claims_index.get("tokens", [])
    claim_tokens = re.findall(r"[a-z0-9+#.]{2,}", needle)
    return bool(claim_tokens and all(t in tokens for t in claim_tokens))


def validate_claims(claims_index: dict[str, Any], claimed_items: list[str]) -> list[str]:
    """Return unsupported claims (invented credentials/skills)."""
    unsupported: list[str] = []
    for item in claimed_items:
        if not claim_supported(claims_index, item):
            unsupported.append(item)
    return unsupported
