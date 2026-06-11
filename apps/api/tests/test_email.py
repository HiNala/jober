from __future__ import annotations

import logging

import pytest

from jober_api.config import settings
from jober_api.services.email.console import ConsoleEmailSender
from jober_api.services.email.dispatch import (
    dispatch_password_reset_email,
    dispatch_verification_email,
)
from jober_api.services.email.sender import (
    deliver_email_payload,
    email_to_payload,
    inbox_delivery_enabled,
    mask_email,
)
from jober_api.services.email.templates import password_reset_email, verification_email

pytestmark = pytest.mark.no_db


def test_mask_email_redacts_local_part() -> None:
    assert mask_email("person@example.com") == "p***@example.com"


def test_verification_template_includes_link() -> None:
    message = verification_email("user@example.com", "tok123", "Ada")
    assert "tok123" in message.text_body
    assert "/verify-email" in message.text_body
    assert message.subject


def test_password_reset_template_includes_link() -> None:
    message = password_reset_email("user@example.com", "reset456")
    assert "reset456" in message.text_body
    assert "/reset-password" in message.text_body


def test_console_sender_logs(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO)
    message = verification_email("user@example.com", "tok", None)
    ConsoleEmailSender().send(message)
    assert "user@example.com" in caplog.text
    assert "tok" in caplog.text


def test_inbox_delivery_requires_smtp(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "email_backend", "console")
    assert inbox_delivery_enabled() is False
    monkeypatch.setattr(settings, "email_backend", "smtp")
    monkeypatch.setattr(settings, "smtp_host", "smtp.example.com")
    monkeypatch.setattr(settings, "email_from", "Jober <noreply@example.com>")
    assert inbox_delivery_enabled() is True


def test_dispatch_verification_uses_console_in_dev(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO)
    monkeypatch.setattr(settings, "jober_env", "development")
    monkeypatch.setattr(settings, "email_backend", "console")

    import jober_api.services.email.dispatch as dispatch_module

    def _sync(payload: dict[str, str]) -> str:
        deliver_email_payload(payload)
        return "sync-dev"

    monkeypatch.setattr(dispatch_module, "_enqueue_or_deliver", _sync)
    dispatch_verification_email("user@example.com", "abc", "User")
    assert "abc" in caplog.text


def test_dispatch_password_reset(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO)
    monkeypatch.setattr(settings, "email_backend", "console")
    import jober_api.services.email.dispatch as dispatch_module

    def _sync(payload: dict[str, str]) -> str:
        deliver_email_payload(payload)
        return "ok"

    monkeypatch.setattr(dispatch_module, "_enqueue_or_deliver", _sync)
    dispatch_password_reset_email("user@example.com", "reset-tok")
    assert "reset-tok" in caplog.text


def test_email_to_payload_roundtrip() -> None:
    message = password_reset_email("a@b.co", "t")
    payload = email_to_payload(message)
    assert payload["to_email"] == "a@b.co"
    assert payload["subject"]
    assert payload["text_body"]
