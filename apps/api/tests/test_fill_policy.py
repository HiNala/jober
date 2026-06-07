from __future__ import annotations

import json

import pytest

from jober_api.repositories.user_profile import UserProfileRepository
from jober_api.vault.fill_policy import FillOutcome, agent_propose_fill, resolve_field_fill

pytestmark = [
    pytest.mark.policy,
    pytest.mark.skipif(
        __import__("os").getenv("CI") != "true" and __import__("os").getenv("RUN_DB_TESTS") != "1",
        reason="requires Postgres",
    ),
]


@pytest.mark.asyncio
async def test_sensitive_field_without_consent_never_autofilled(
    db_session,
    truncate_tables,
) -> None:
    repo = UserProfileRepository(db_session)
    profile = await repo.create(
        sensitive_eeo_answers=json.dumps({"veteran_status": "no"}),
        field_consent={"veteran_status": {"consent": False, "never_autofill": True}},
    )

    resolution = resolve_field_fill(profile, "veteran_status")
    assert resolution.outcome == FillOutcome.NEEDS_HUMAN

    agent = agent_propose_fill(profile, "veteran_status", agent_guess="no")
    assert agent.outcome == FillOutcome.NEEDS_HUMAN
    assert agent.value is None


@pytest.mark.asyncio
async def test_sensitive_field_with_consent_returns_stored_value(
    db_session,
    truncate_tables,
) -> None:
    repo = UserProfileRepository(db_session)
    profile = await repo.create(
        sensitive_eeo_answers=json.dumps({"disability": "prefer_not_to_answer"}),
        field_consent={"disability": {"consent": True, "never_autofill": False}},
    )

    resolution = resolve_field_fill(profile, "disability")
    assert resolution.outcome == FillOutcome.VALUE
    assert resolution.value == "prefer_not_to_answer"


@pytest.mark.asyncio
async def test_never_autofill_forces_needs_human_even_with_value(
    db_session,
    truncate_tables,
) -> None:
    repo = UserProfileRepository(db_session)
    profile = await repo.create(
        sensitive_eeo_answers=json.dumps({"gender": "man"}),
        field_consent={"gender": {"consent": True, "never_autofill": True}},
    )

    resolution = resolve_field_fill(profile, "gender")
    assert resolution.outcome == FillOutcome.NEEDS_HUMAN
    assert resolution.reason == "never_autofill"


def test_agent_cannot_invent_sensitive_value_without_storage() -> None:
    from jober_api.models.user_profile import UserProfile

    profile = UserProfile()
    profile.field_consent = {"race_ethnicity": {"consent": True, "never_autofill": False}}

    agent = agent_propose_fill(profile, "race_ethnicity", agent_guess="Asian")
    assert agent.outcome == FillOutcome.NEEDS_HUMAN
