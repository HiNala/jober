# Mission 29 — Pre-flight review findings

**Date:** 2026-06-12
**Reviewer:** Fable 5 agent
**Scope:** Full codebase and mission pack validation after Missions 01–28

## Executive summary

Missions 01–28 are complete, committed, and green in CI. The product is substantially polished and production-ready. Nine small gaps remain to be closed in Mission 29 (documentation) and Mission 30 (release certification). None are blocking for a soft launch; the only external blocker is legal counsel review of `/acceptable-use`.

## Verified complete

- All 28 missions landed on `main` with `[pack-NN]` commits.
- Continuation loops logged after every mission; no silent skips.
- Quality gates green: api 83 passed, worker 22, web 128 tests, marketing e2e 71, fullstack e2e 5, policy 19.
- UI-REVIEW themes 1–6 implemented: brand signature, layout discipline, component tiering, motion tokens, empty states as onboarding, consent bottom sheet.
- Email delivery (SMTP/console), observability alerts, e2e coverage, copy/SEO, performance budgets all shipped.

## Gaps requiring action

### Mission 29 (documentation)

| # | Item | File | Action |
|---|---|---|---|
| 1 | Uncommitted `pyproject.toml` adds `celery[redis]` | `apps/api/pyproject.toml` | Triage: commit if intentional dependency fix, else restore |
| 2 | Uncommitted `compose.yaml` adds LLM env vars to API service | `infra/compose.yaml` | Triage: commit if intentional local-dev fix, else restore |
| 3 | Debug scripts and screenshots untracked | `scripts/debug_signup.js`, `scripts/screenshot_admin.js`, `scripts/screenshot_app.js`, `scripts/screenshot_auth.js`, `tmp_screenshots/` | Remove or `.gitignore` |
| 4 | README references non-existent missions | `README.md` | `Mission 33` → `Mission 29`; `Mission 34` → `Mission 24` |
| 5 | CHANGELOG unreleased section incomplete | `CHANGELOG.md` | Expand to cover missions 01–28 (already updated in this review) |
| 6 | `variables.example.env` references non-existent mission | `infra/railway/variables.example.env` | `Mission 34` → `Mission 24` (already updated in this review) |
| 7 | Runbooks need verification walk and date stamps | `docs/runbooks/*.md` | Execute steps locally; fix drift; add "last verified" |
| 8 | Env vars may have drifted from code | `.env.example`, `infra/railway/variables.example.env` | Cross-check against `config.py` settings |
| 9 | Architecture docs need cross-link verification | `docs/architecture/*.md` | Confirm M18/M21/M26/M28 deltas landed |
| 10 | Agent convention files may be stale | `CLAUDE.md`, `AGENTS.md` | Update with pack decisions (testids, forms, layout modes) |

### Mission 30 (release candidate)

| # | Item | Action |
|---|---|---|
| 1 | Full gate run ×2 consecutive | Required before deploy |
| 2 | Fresh production backup | M20 flow |
| 3 | Deploy RC; `bash scripts/railway-smoke.sh` | Per `deploy.md` |
| 4 | Manual production golden path with real inbox | Signup → verify email → dashboard |
| 5 | Launch checklist execution with waivers | External: legal counsel, OG images, Lighthouse PSI |
| 6 | Screenshot re-capture (desktop + mobile) | `scripts/capture-screenshots.mjs` |
| 7 | Alert test-fire (`POST /api/admin/ops/test-alert`) | After `OPS_ALERT_WEBHOOK_URL` set |
| 8 | Tag release (`v0.1.0` or `v0.2.0`) | After verification, not before |
| 9 | Write `docs/runbooks/post-launch.md` | Daily/weekly checks, rollback command |
| 10 | 7-day post-launch review scheduled | Reliability, cost, funnel |

## Open blockers (waivable for launch)

- **Legal counsel review of `/acceptable-use`** — external; waive in Mission 30 with honest copy.
- **Lighthouse CWV manual verification** — automated blocked by bot interstitial; manual PSI post-deploy.
- **Per-route OG image assets** — deferred from Mission 27; post-launch.
- **`auth-journey` fullstack in CI** — requires `E2E_AUTH_NATIVE=1`; Mission 26 waiver.

## No feature creep

All gaps are validation, documentation, or cleanup. No new product surface is required.
