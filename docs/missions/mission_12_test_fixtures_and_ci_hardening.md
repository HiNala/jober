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
- [x] Finish leftovers — behavior-gate + injection fixtures now asserted via fixture server URL
- [x] Gates green — ruff, mypy, pytest (133 api / 19 worker / 31 fixture+packages), web lint/typecheck/build/test
- [x] No regressions — full suite green
- [x] Policy holds — 30 blocking `pytest -m policy` tests pass
- [x] Secrets clean — `detect-secrets` baseline passes
- [x] Design Council — 19/20 recorded in `design-review.md`
- [x] Self-improvement — `test_behavior_gate_fixture_verify_via_server` + `test_injection_fixture_server_treats_page_text_as_data`
- [x] Docs current — `testing.md`, README Makefile targets
- [x] Pushed to `origin/main`
