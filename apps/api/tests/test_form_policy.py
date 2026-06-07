from __future__ import annotations

import pytest
from jober_forms.policy import apply_confidence_policy

pytestmark = pytest.mark.policy


def test_low_confidence_needs_review() -> None:
    draft = apply_confidence_policy(
        mapped_field="unknown",
        confidence=0.4,
        fill_outcome="needs_human",
        fill_value=None,
        field_type="text",
        is_sensitive=False,
        is_ambiguous=False,
        is_upload=False,
    )
    assert draft.status == "needs_review"


def test_ambiguous_salary_needs_review() -> None:
    draft = apply_confidence_policy(
        mapped_field="salary_prefs",
        confidence=0.75,
        fill_outcome="value",
        fill_value="120000",
        field_type="text",
        is_sensitive=False,
        is_ambiguous=True,
        is_upload=False,
    )
    assert draft.status == "needs_review"


def test_high_confidence_public_eligible_for_autofill() -> None:
    draft = apply_confidence_policy(
        mapped_field="email",
        confidence=0.92,
        fill_outcome="value",
        fill_value="user@example.com",
        field_type="email",
        is_sensitive=False,
        is_ambiguous=False,
        is_upload=False,
    )
    assert draft.status == "skipped"
    assert draft.proposed_value_redacted is not None
    assert "user@example.com" not in draft.proposed_value_redacted


def test_sensitive_always_needs_review() -> None:
    draft = apply_confidence_policy(
        mapped_field="veteran_status",
        confidence=0.95,
        fill_outcome="value",
        fill_value="No",
        field_type="select",
        is_sensitive=True,
        is_ambiguous=False,
        is_upload=False,
    )
    assert draft.status == "needs_review"
