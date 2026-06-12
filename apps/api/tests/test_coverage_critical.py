"""Mission 25 — targeted coverage for pack-critical paths (no_db where possible)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from jober_api.config import settings
from jober_api.models.user_profile import UserProfile
from jober_api.privacy.redaction import scrub_text
from jober_api.services.email.dispatch import dispatch_verification_email
from jober_api.vault.fill_policy import FillOutcome, agent_propose_fill, resolve_field_fill
from jober_api.vault.sensitive_store import merge_sensitive_answers

pytestmark = pytest.mark.no_db


def test_email_enqueue_failure_alerts_in_production(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Production path must not silently drop enqueue failures (Mission 11/24)."""
    alerts: list[tuple[str, list[dict[str, object]]]] = []
    monkeypatch.setattr(settings, "jober_env", "production")
    monkeypatch.setattr(settings, "email_backend", "smtp")
    monkeypatch.setattr(settings, "smtp_host", "smtp.example.com")
    monkeypatch.setattr(settings, "email_from", "Jober <noreply@example.com>")

    import jober_api.services.email.dispatch as dispatch_module

    def _boom(_task, _payload):  # noqa: ANN001
        raise ConnectionError("redis unavailable")

    monkeypatch.setattr(dispatch_module, "enqueue_task", _boom)
    monkeypatch.setattr(
        dispatch_module,
        "dispatch_ops_alerts_sync",
        lambda source, items, **_: alerts.append((source, items)),
    )

    task_id = dispatch_verification_email("user@example.com", "tok", "User")
    assert task_id is None
    assert alerts
    assert alerts[0][0] == "email_enqueue_failed"
    assert "docs/runbooks/email-delivery.md" in str(alerts[0][1])


def test_mutation_fill_policy_blocks_sensitive_agent_guess() -> None:
    """Mutation spot-check: agent guesses must not bypass sensitive storage."""
    profile = UserProfile()
    merge_sensitive_answers(profile, {"work_authorization": "authorized"})
    profile.field_consent = {}
    resolution = resolve_field_fill(profile, "work_authorization")
    assert resolution.outcome == FillOutcome.NEEDS_HUMAN
    agent = agent_propose_fill(profile, "work_authorization", agent_guess="authorized")
    assert agent.outcome == FillOutcome.NEEDS_HUMAN
    assert agent.value is None


_SAMPLE_JWT = (
    "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0."
    "dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
)


def test_mutation_redaction_masks_bearer_jwt_and_sk_keys() -> None:
    """Mutation spot-check: common secret shapes must not survive scrub_text."""
    raw = (
        f"Authorization: Bearer abc.def.ghi token={_SAMPLE_JWT} "
        "key=sk-live-abcdefghijklmnop"
    )
    scrubbed = scrub_text(raw)
    assert "sk-live-abcdefghijklmnop" not in scrubbed
    assert _SAMPLE_JWT not in scrubbed
    assert "Bearer [REDACTED" in scrubbed or "[REDACTED" in scrubbed


def test_enqueue_task_without_correlation_uses_delay(monkeypatch: pytest.MonkeyPatch) -> None:
    from jober_api.celery_enqueue import enqueue_task
    from jober_api.request_context import clear_correlation_id

    clear_correlation_id()
    captured: dict[str, object] = {}

    class _FakeTask:
        def delay(self, *args):  # noqa: ANN001
            captured["args"] = args
            return MagicMock(id="task-delay")

        def apply_async(self, **_kwargs):  # noqa: ANN001
            raise AssertionError("apply_async should not run without correlation id")

    result = enqueue_task(_FakeTask(), "only-arg")
    assert result.id == "task-delay"
    assert captured["args"] == ("only-arg",)
