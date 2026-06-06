from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from jober_api.models.user_profile import UserProfile
from jober_api.vault.field_registry import FIELD_BY_KEY, FieldTier, VaultFieldSpec
from jober_api.vault.sensitive_store import get_consent_flags, load_sensitive_answers


class FillOutcome(str, Enum):
    VALUE = "value"
    NEEDS_HUMAN = "needs_human"


@dataclass(frozen=True)
class FillResolution:
    outcome: FillOutcome
    value: Any = None
    reason: str | None = None


def _read_public_value(profile: UserProfile, spec: VaultFieldSpec) -> Any:
    if spec.profile_attr:
        return getattr(profile, spec.profile_attr, None)
    return None


def resolve_field_fill(profile: UserProfile, field_key: str) -> FillResolution:
    spec = FIELD_BY_KEY.get(field_key)
    if spec is None:
        return FillResolution(FillOutcome.NEEDS_HUMAN, reason="unknown_field")

    consent = get_consent_flags(profile, field_key)

    if spec.tier == FieldTier.SENSITIVE:
        if consent["never_autofill"]:
            return FillResolution(
                FillOutcome.NEEDS_HUMAN,
                reason="never_autofill",
            )
        answers = load_sensitive_answers(profile)
        sensitive_key = spec.sensitive_key or spec.key
        stored = answers.get(sensitive_key)
        if not consent["consent"] or not stored:
            return FillResolution(
                FillOutcome.NEEDS_HUMAN,
                reason="missing_consent_or_value",
            )
        return FillResolution(FillOutcome.VALUE, value=stored)

    value = _read_public_value(profile, spec)
    if spec.tier == FieldTier.PUBLIC and value not in (None, "", {}):
        return FillResolution(FillOutcome.VALUE, value=value)

    if spec.tier == FieldTier.PREFERENCE and value is not None:
        return FillResolution(FillOutcome.VALUE, value=value)

    return FillResolution(FillOutcome.NEEDS_HUMAN, reason="empty_standard_field")


def agent_propose_fill(profile: UserProfile, field_key: str, agent_guess: Any) -> FillResolution:
    """Single entry point for agents — guesses are ignored for sensitive fields."""
    spec = FIELD_BY_KEY.get(field_key)
    if spec is not None and spec.tier == FieldTier.SENSITIVE:
        return resolve_field_fill(profile, field_key)
    resolved = resolve_field_fill(profile, field_key)
    if resolved.outcome == FillOutcome.VALUE:
        return resolved
    if agent_guess not in (None, ""):
        return FillResolution(FillOutcome.VALUE, value=agent_guess)
    return FillResolution(FillOutcome.NEEDS_HUMAN, reason="no_stored_or_agent_value")
