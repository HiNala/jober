# Mission 25 — Critical-path coverage map

**Date:** 2026-06-12  
**CI:** authoritative for full pytest + e2e  
**Web inventory:** 42 vitest files, **125** tests (was 113)

## Discovery

| Layer | Tool | Baseline |
|-------|------|----------|
| API | `pytest --cov=jober_api` (CI uploads `coverage.xml`) | `fail_under = 58` in `pyproject.toml` |
| Worker | `pytest -q` | 22 tests, policy + fixture browser |
| Web | `pnpm test` (vitest, node env) | Lib/unit tests only — no `@testing-library` (by design) |

Web vitest runs in **node** environment; pack-critical UI behavior is tested via extracted pure modules (`lib/*`) matching existing convention. React component mount tests deferred to Mission 26 e2e.

## Critical-path coverage matrix

| Path | Verdict | Tests / evidence |
|------|---------|------------------|
| Consent sheet + analytics gating | **Covered** | `consent.test.ts`, `consent-state.test.ts` (+ `setAnalyticsConsent`, `markConsentPrompted`) |
| Forms mapper + 422 envelope | **Covered** | `map-api-errors.test.ts` (+ 402 budget, lockout) |
| Page states (empty/loading/error) | **Covered** | `page-state-contracts.test.ts`, `onboarding-copy.test.ts` |
| SSE reconnect labels | **Covered** | `stream-status.test.ts` (+ error/disconnected); hook reconnect in e2e M26 |
| Command palette actions | **Covered** | `command-palette-actions.test.ts` + `workspace-store.test.ts` |
| Document studio lock on regen | **Covered** | `merge-paragraphs.test.ts` (+ all-locked / none-locked) |
| Auth lifecycle | **Covered** | `test_auth.py` register→verify→login→reset→logout |
| Email sender + enqueue failure | **Covered** | `test_email.py`, `test_coverage_critical.py::test_email_enqueue_failure_alerts_in_production` |
| Error envelope + correlation | **Covered** | `test_error_contract.py`, `errors.test.ts` |
| Batch → enqueue → orchestrator | **Covered** | `test_batch_ops.py::test_create_and_enqueue_batch` (mocked Celery) |
| Correlation API → Celery | **Covered** | `test_observability.py`, `test_coverage_critical.py` |
| Fill policy (sensitive autofill) | **Covered** | `test_fill_policy.py`, `test_policy_baseline.py`, mutation in `test_coverage_critical.py` |
| Redaction (logs/events/LLM audit) | **Covered** | `test_privacy_redaction.py` (+ JWT/bearer), `test_security_controls.py` |
| Golden path integration | **Covered** | `test_golden_path_integration.py` (`@pytest.mark.policy`) |
| Workspace layout modes | **Covered** | `layout.test.ts` |
| Client form validation (auth) | **Covered** | `client-validation.test.ts` |

## Waivers

| Item | Rationale | Owner |
|------|-----------|-------|
| `useRunStream` reconnect timer (React hook) | **Covered (M26)** — `core-journey.fullstack.spec.ts` reload + `run-event-stream` | — |
| Full React component mount (ConsentSheet, DocumentStudio) | **Partial (M26)** — document studio cycle e2e; ConsentSheet still lib-only | Incremental |
| Discover/documents inline field-error migration | Form inventory **P** rows — UI pattern, not safety | Mission 12 follow-up / incremental |
| Parametrized per-router API envelope sweep | High count, low marginal value vs `test_error_contract` | Incremental |

## Mutation spot-checks (Mission 25)

| Module | Break attempted | Test that must fail |
|--------|-----------------|---------------------|
| `vault/fill_policy.py` | Agent guess on sensitive without consent | `test_mutation_fill_policy_blocks_sensitive_agent_guess` |
| `privacy/redaction.py` | Leave JWT/bearer/sk in logs | `test_mutation_redaction_masks_bearer_jwt_and_sk_keys`, `test_scrub_text_masks_bearer_and_jwt_tokens` |

Verified locally: tests pass on real code; breaking `agent_propose_fill` sensitive branch or removing `_JWT_RE` would fail the above.

## Flake hunt

| Suite | Runs | Result |
|-------|------|--------|
| `pnpm test` | 3× | **125 passed** each (2026-06-12 local) |
| `pytest tests/test_coverage_critical.py` | 1× | **4 passed** (py 3.12) |
| Full API 3× | — | CI authoritative (local host lacks Postgres on default ports) |

No new flakes introduced; no quarantine changes.

## CI duration

New tests are pure unit (`no_db` / vitest lib). Expected CI delta **< +25%** (≈15 web + 5 api tests, sub-second each).

## Commands

```bash
cd apps/api && pytest -q --cov=jober_api --cov-report=term-missing
cd apps/api && pytest -q tests/test_coverage_critical.py tests/test_fill_policy.py tests/test_privacy_redaction.py
cd apps/worker && pytest -q
cd apps/web && pnpm test
make test-policy && make test-fixtures
```
