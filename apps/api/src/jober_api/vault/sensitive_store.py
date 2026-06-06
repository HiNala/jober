from __future__ import annotations

import json
from typing import Any

from jober_api.models.user_profile import UserProfile
from jober_api.vault.field_registry import SENSITIVE_EEO_KEYS


def load_sensitive_answers(profile: UserProfile) -> dict[str, str]:
    raw = profile.sensitive_eeo_answers
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    if not isinstance(parsed, dict):
        return {}
    return {str(k): str(v) for k, v in parsed.items() if v is not None and str(v).strip()}


def dump_sensitive_answers(answers: dict[str, str]) -> str:
    return json.dumps(answers, sort_keys=True)


def merge_sensitive_answers(profile: UserProfile, updates: dict[str, str | None]) -> None:
    current = load_sensitive_answers(profile)
    for key, value in updates.items():
        if value is None or not str(value).strip():
            current.pop(key, None)
        else:
            current[key] = str(value).strip()
    profile.sensitive_eeo_answers = dump_sensitive_answers(current) if current else None


def get_consent_flags(profile: UserProfile, field_key: str) -> dict[str, Any]:
    consent_map = profile.field_consent or {}
    raw = consent_map.get(field_key, {})
    if not isinstance(raw, dict):
        raw = {}
    is_sensitive = field_key in SENSITIVE_EEO_KEYS
    return {
        "consent": bool(raw.get("consent", False)),
        "never_autofill": bool(raw.get("never_autofill", is_sensitive)),
        "consented_at": raw.get("consented_at"),
    }
