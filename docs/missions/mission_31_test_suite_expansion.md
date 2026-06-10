# Mission 31 — Test Suite Expansion & Quality Hardening

## Task list
- [x] **Unit:** schema contract tests; web consent + marketing fixtures; analytics UTM/metadata (M29–30 extended)
- [x] **Integration:** `test_golden_path_integration.py` — fixture fill → verify → analytics rollup → admin
- [x] **Integration:** `test_admin_routes_extended.py` — acquisition, cost, system, data-requests
- [x] **E2E (Playwright):** marketing axe checks on all public routes; funnel smoke; keyboard skip link; reduced-motion
- [x] **Browser pipeline:** `test_golden_path_browser.py` — single-step fixture loads in Chromium
- [x] **Policy:** golden path asserts `auto_submit_opt_in` false + existing blocking `pytest -m policy` job
- [x] **Coverage:** API `fail_under` raised 55 → 58
- [x] **Contract tests:** `packages/schemas/tests/test_contract.py` + web `schemas-contract.test.ts`

## Acceptance criteria
- [x] Golden-path integration passes against fixture ATS + form fixtures (no live network)
- [x] Policy job unchanged and blocking; golden path tagged `@pytest.mark.policy`
- [x] Playwright a11y + smoke in CI `web` job (after `pnpm build`)
- [x] Schema Python ↔ TypeScript contract tests in CI packages step

## CI jobs
| Job | M31 additions |
|-----|----------------|
| `backend` | `packages/schemas/tests`, golden path + admin integration tests |
| `policy` | includes new `test_golden_path_integration` policy assertion |
| `web` | Playwright a11y + funnel smoke |

## Iteration clause
Contract tests between `jober-schemas` and web `@jober/schemas` path. **Mission 99** runs next.
