"""Blocking policy invariants for schema-layer defaults (Mission 01+)."""

import inspect

from jober_api.crypto.encrypted import EncryptedText
from jober_api.models.application_run import ApplicationRun
from jober_api.models.enums import RunPolicy
from jober_api.models.user_profile import UserProfile


def test_auto_submit_is_never_the_default_policy() -> None:
    column = ApplicationRun.__table__.c.policy
    default = column.default.arg if column.default is not None else None
    assert default == RunPolicy.REVIEW_BEFORE_SUBMIT
    assert default != RunPolicy.AUTO_SUBMIT


def test_sensitive_eeo_answers_use_encrypted_column() -> None:
    column = UserProfile.__table__.c.sensitive_eeo_answers
    assert isinstance(column.type, EncryptedText)


def test_needs_human_is_a_valid_checkpoint_handoff_state() -> None:
    """CAPTCHA/login/2FA flows will pause at NEEDS_HUMAN — state must exist in the machine."""
    from jober_api.models.enums import RunStatus

    assert RunStatus.NEEDS_HUMAN.value == "needs_human"


def test_redacted_columns_exist_on_audit_models() -> None:
    from jober_api.models.browser_event import BrowserEvent
    from jober_api.models.form_field_observation import FormFieldObservation
    from jober_api.models.llm_call import LlmCall

    assert "proposed_value_redacted" in FormFieldObservation.__table__.c
    assert "redacted_prompt" in LlmCall.__table__.c
    assert "redacted_response" in LlmCall.__table__.c
    # BrowserEvent stores screenshot keys, not raw page HTML in message by schema contract.
    assert "screenshot_key" in BrowserEvent.__table__.c
    assert "metadata" in BrowserEvent.__table__.c


def test_field_consent_json_supported_on_profile() -> None:
    assert "field_consent" in UserProfile.__table__.c
    hints = inspect.getdoc(UserProfile) or ""
    # Model docstring optional; column presence is the contract for Mission 04 vault work.
    assert hints or UserProfile.__tablename__ == "user_profiles"
