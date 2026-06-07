# Mission 12 — Test Fixtures & CI Hardening

## Task list

### Fixture ATS site (`fixtures/ats/`)
- [x] FastAPI server with synthetic Ashby/Lever/Greenhouse/Workday-like pages
- [x] Behavioral fixtures: single-step, multi-step, combobox, dropzone, validation, conditional fields, already-applied, success/uncertain confirmation, login wall, CAPTCHA, prompt-injection, shifting selector
- [x] Known expected outcomes in `outcomes.py`; catalog parity tests

### Test pyramid
- [x] Unit tests (existing suites across api + packages)
- [x] Integration tests (API + DB + MinIO in CI)
- [x] Browser tests (`apps/worker/tests/test_fixture_browser.py`)
- [x] Policy tests (`pytest -m policy`) — consent, gates, opt-in submit, injection
- [x] Manual live smoke documented (not CI)

### CI
- [x] Service containers (Postgres, Redis, MinIO)
- [x] Unit + integration + browser + policy jobs
- [x] Coverage threshold gate (`fail_under = 55`)
- [x] Quarantine lane (`pytest -m quarantine`, non-blocking)
- [x] `mypy` / `ruff` / web `typecheck` / `lint:strict` blocking
- [x] Playwright trace artifact upload on failure

## Acceptance criteria
- [x] Full pipeline runs against fixtures in CI with no network egress and no live submissions
- [x] Every behavioral fixture has a passing assertion
- [x] Policy tests wired as blocking in CI
- [x] Coverage meets threshold; CI green

## Docs
- [x] `docs/architecture/testing.md` — pyramid, fixtures, "fixture for every bug" rule

## Mission 99 (post–Mission 12)
- [x] Re-read acceptance criteria; close gaps (legacy ATS loader paths, API `items` key)
- [x] Run all quality gates — 130 API + 19 worker + 23 fixture tests; 74% coverage
- [x] Update checkboxes; ready for push to `origin/main`
