from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FixtureOutcome:
    slug: str
    platform: str
    expected_gate: str | None
    expected_fill_status: str | None
    expected_discovery_min_fields: int
    notes: str


FIXTURE_OUTCOMES: dict[str, FixtureOutcome] = {
    "behaviors/single-step": FixtureOutcome(
        slug="behaviors/single-step",
        platform="greenhouse",
        expected_gate=None,
        expected_fill_status="succeeded",
        expected_discovery_min_fields=2,
        notes="Basic email + name form",
    ),
    "behaviors/multi-step": FixtureOutcome(
        slug="behaviors/multi-step",
        platform="greenhouse",
        expected_gate=None,
        expected_fill_status=None,
        expected_discovery_min_fields=2,
        notes="Personal then details with Next",
    ),
    "behaviors/combobox": FixtureOutcome(
        slug="behaviors/combobox",
        platform="ashby",
        expected_gate=None,
        expected_fill_status=None,
        expected_discovery_min_fields=1,
        notes="role=listbox custom combobox",
    ),
    "behaviors/dropzone": FixtureOutcome(
        slug="behaviors/dropzone",
        platform="lever",
        expected_gate=None,
        expected_fill_status=None,
        expected_discovery_min_fields=2,
        notes="Resume + cover letter uploads",
    ),
    "behaviors/required-validation": FixtureOutcome(
        slug="behaviors/required-validation",
        platform="greenhouse",
        expected_gate=None,
        expected_fill_status="succeeded",
        expected_discovery_min_fields=2,
        notes="Required vs optional markers",
    ),
    "behaviors/conditional-fields": FixtureOutcome(
        slug="behaviors/conditional-fields",
        platform="workday",
        expected_gate=None,
        expected_fill_status=None,
        expected_discovery_min_fields=1,
        notes="Hidden field revealed by checkbox",
    ),
    "behaviors/shifting-selector": FixtureOutcome(
        slug="behaviors/shifting-selector",
        platform="greenhouse",
        expected_gate=None,
        expected_fill_status="succeeded",
        expected_discovery_min_fields=1,
        notes="Brittle id changes; label locator must survive",
    ),
    "behaviors/already-applied": FixtureOutcome(
        slug="behaviors/already-applied",
        platform="greenhouse",
        expected_gate="already_applied",
        expected_fill_status=None,
        expected_discovery_min_fields=0,
        notes="Idempotent already applied page",
    ),
    "behaviors/submit-success": FixtureOutcome(
        slug="behaviors/submit-success",
        platform="greenhouse",
        expected_gate=None,
        expected_fill_status=None,
        expected_discovery_min_fields=0,
        notes="Clear success confirmation text",
    ),
    "behaviors/uncertain-confirmation": FixtureOutcome(
        slug="behaviors/uncertain-confirmation",
        platform="greenhouse",
        expected_gate="uncertain_submission",
        expected_fill_status=None,
        expected_discovery_min_fields=0,
        notes="Ambiguous post-submit copy",
    ),
    "gates/login": FixtureOutcome(
        slug="gates/login",
        platform="greenhouse",
        expected_gate="login",
        expected_fill_status=None,
        expected_discovery_min_fields=0,
        notes="Must raise human checkpoint — never bypass",
    ),
    "gates/captcha": FixtureOutcome(
        slug="gates/captcha",
        platform="greenhouse",
        expected_gate="captcha",
        expected_fill_status=None,
        expected_discovery_min_fields=0,
        notes="Must raise human checkpoint — never bypass",
    ),
    "security/injection": FixtureOutcome(
        slug="security/injection",
        platform="greenhouse",
        expected_gate=None,
        expected_fill_status=None,
        expected_discovery_min_fields=0,
        notes="Injection text treated as untrusted data",
    ),
    "jobs/greenhouse": FixtureOutcome(
        slug="jobs/greenhouse",
        platform="greenhouse",
        expected_gate=None,
        expected_fill_status=None,
        expected_discovery_min_fields=0,
        notes="Greenhouse-like job posting for extraction tests",
    ),
    "jobs/lever": FixtureOutcome(
        slug="jobs/lever",
        platform="lever",
        expected_gate=None,
        expected_fill_status=None,
        expected_discovery_min_fields=0,
        notes="Lever-like job posting for extraction tests",
    ),
    "jobs/ashby": FixtureOutcome(
        slug="jobs/ashby",
        platform="ashby",
        expected_gate=None,
        expected_fill_status=None,
        expected_discovery_min_fields=0,
        notes="Ashby-like job posting for extraction tests",
    ),
    "jobs/workday": FixtureOutcome(
        slug="jobs/workday",
        platform="workday",
        expected_gate=None,
        expected_fill_status=None,
        expected_discovery_min_fields=0,
        notes="Workday-like job posting for extraction tests",
    ),
    "platforms/greenhouse": FixtureOutcome(
        slug="platforms/greenhouse",
        platform="greenhouse",
        expected_gate=None,
        expected_fill_status="succeeded",
        expected_discovery_min_fields=2,
        notes="Greenhouse-like apply shell",
    ),
    "platforms/lever": FixtureOutcome(
        slug="platforms/lever",
        platform="lever",
        expected_gate=None,
        expected_fill_status="succeeded",
        expected_discovery_min_fields=2,
        notes="Lever-like posting layout",
    ),
    "platforms/ashby": FixtureOutcome(
        slug="platforms/ashby",
        platform="ashby",
        expected_gate=None,
        expected_fill_status="succeeded",
        expected_discovery_min_fields=2,
        notes="Ashby-like apply shell",
    ),
    "platforms/workday": FixtureOutcome(
        slug="platforms/workday",
        platform="workday",
        expected_gate=None,
        expected_fill_status="succeeded",
        expected_discovery_min_fields=2,
        notes="Workday-like apply shell",
    ),
}
