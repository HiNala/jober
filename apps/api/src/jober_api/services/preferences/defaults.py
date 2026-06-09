from __future__ import annotations

from copy import deepcopy
from typing import Any

DEFAULT_USER_PREFERENCES: dict[str, Any] = {
    "appearance": {
        "theme": "dark",
        "density": "comfortable",
        "reduced_motion": None,
        "canvas_view_mode": "single",
        "filmstrip_visible": True,
    },
    "notifications": {
        "in_app_run_attention": True,
        "in_app_batch_complete": True,
        "email_batch_complete": False,
    },
    "application_defaults": {
        "generate_cover_letter_per_run": True,
        "letter_template": "classic",
        "voice_preset": "direct",
        "site_cooldown_seconds": None,
    },
    "ai": {
        "preferred_draft_model": None,
        "preferred_scoring_model": None,
    },
}


def deep_merge(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(base)
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def merged_preferences(stored: dict[str, Any] | None) -> dict[str, Any]:
    return deep_merge(DEFAULT_USER_PREFERENCES, stored or {})
