# Testing architecture

Jober uses a **test pyramid** with deterministic offline fixtures. **No live ATS submissions in automated tests.**

## Fixture ATS site (`fixtures/ats/`)

A small FastAPI server (`jober-fixtures`) serves synthetic HTML pages that imitate Ashby-, Lever-, Greenhouse-, and Workday-like apply flows. Pages are **authored**, not scraped from real ATS markup.

```bash
pip install -e ./fixtures/ats
python -m jober_fixtures.server --port 8765
# or: make fixture-serve
```

Browse `http://127.0.0.1:8765/` for the route index, or `GET /catalog` for the machine-readable manifest.

### Behavioral fixtures

| Route | Expected behavior |
|-------|-------------------|
| `behaviors/single-step` | Basic email + name; fill succeeds |
| `behaviors/multi-step` | Next-button wizard; discovery only |
| `behaviors/combobox` | `role=listbox` custom combobox |
| `behaviors/dropzone` | Resume + cover letter uploads |
| `behaviors/required-validation` | Required vs optional markers |
| `behaviors/conditional-fields` | Hidden field revealed by checkbox |
| `behaviors/shifting-selector` | Brittle `id` changes; label locator must survive |
| `behaviors/already-applied` | Idempotent already-applied page |
| `behaviors/submit-success` | Clear success confirmation |
| `behaviors/uncertain-confirmation` | Ambiguous post-submit copy |
| `gates/login` | Raises `login` checkpoint — never bypass |
| `gates/captcha` | Raises `captcha` checkpoint — never bypass |
| `security/injection` | Prompt-injection text treated as untrusted data |
| `platforms/*` | Platform-specific apply shells |
| `jobs/*` | Job posting pages for extraction tests |

Expected outcomes live in `fixtures/ats/jober_fixtures/outcomes.py` and are asserted by `apps/api/tests/test_fixture_pipeline.py` and `apps/worker/tests/test_fixture_browser.py`.

### Fixture for every bug

When a real run fails in a new way:

1. Add a synthetic page (or extend an existing one) under `fixtures/ats/jober_fixtures/pages/`.
2. Register the route in `server.py` and add a `FixtureOutcome` in `outcomes.py`.
3. Add a test that reproduces the failure against the fixture server.
4. Land the fix only when the new test passes.

The fix is not done until the fixture + test exist.

## Test layers

| Layer | Location | What it covers |
|-------|----------|----------------|
| **Unit** | `apps/api/tests/`, `packages/*/tests/` | Spreadsheet import, resume extraction, job normalization, prompt assembly, claims guard, ATS scoring, field mapping, state transitions, retry taxonomy, redaction, encryption |
| **Integration** | `apps/api/tests/` (DB + MinIO) | API endpoints, document generation, checkpoint resolution |
| **Browser** | `apps/worker/tests/test_fixture_browser.py` | Playwright against fixture server; discovery + label locators |
| **Policy (blocking)** | `pytest -m policy` | No consent-less sensitive autofill; no CAPTCHA/login bypass; no auto-submit without explicit opt-in; injection text as data |

Policy tests run in a dedicated CI job and **fail the build** on regression.

### Markers

- `@pytest.mark.policy` — blocking safety invariants
- `@pytest.mark.quarantine` — flaky tests excluded from default runs (`addopts = "-m 'not quarantine'"`); optional CI lane

### Environment flags

| Variable | Effect |
|----------|--------|
| `CI=true` | Enables DB-backed tests in CI |
| `RUN_DB_TESTS=1` | Enables DB tests locally |
| `SKIP_PLAYWRIGHT=1` | Skip Playwright tests |
| `SKIP_FIXTURE_SERVER=1` | Skip tests that start the in-process fixture server |
| `FIXTURE_ATS_PORT` | Port for fixture server (default `8765`) |
| `PLAYWRIGHT_HEADED` | Set `false` in CI; headed mode is for local debugging only |

## Manual live smoke (not CI)

Opt-in only. Never submit.

```bash
# Open a real job URL in a visible browser, extract, generate letter, dry-run discovery.
# Set JOBER_LIVE_SMOKE_URL in the environment; do not wire this into CI.
```

## Coverage

API coverage gate: `fail_under = 55` in `apps/api/pyproject.toml`. CI uploads `coverage.xml` on every run.

## Running locally

```bash
make test              # api + worker pytest (default, excludes quarantine)
make test-fixtures     # fixture catalog + pipeline tests
make test-policy       # blocking policy suite
make fixture-serve     # standalone fixture server
```

With Postgres for integration tests:

```bash
make infra
export RUN_DB_TESTS=1 DATABASE_URL=postgresql+asyncpg://jober:jober@localhost:5432/jober?ssl=disable
cd apps/api && pytest -q --cov=jober_api
```
