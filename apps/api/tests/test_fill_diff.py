from __future__ import annotations

from jober_fill.fill_diff import build_fill_diff


def test_fill_diff_masks_email_values() -> None:
    diff = build_fill_diff(
        proposed="ada@example.com",
        actual="ada@example.com",
        field_type="email",
        locator_strategy="label",
    )
    assert diff.matched is True
    assert "ada@example.com" not in (diff.proposed_redacted or "")
    assert "@" in (diff.proposed_redacted or "")


def test_fill_diff_detects_mismatch() -> None:
    diff = build_fill_diff(
        proposed="555-0100",
        actual="555-0199",
        field_type="tel",
        locator_strategy="label",
    )
    assert diff.matched is False
    assert diff.actual_redacted is not None
