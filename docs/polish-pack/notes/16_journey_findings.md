# Mission 16 — Discover → Queue → Batch journey findings

**Validated:** 2026-06-10 · Journey matrix for acquisition half of golden path.

## `/search` vs `/discover` decision

**Deliberate distinction (no merge)** — owner sign-off not required for clarity-only change:

| Route | Purpose | Nav hint |
|-------|---------|----------|
| `/discover` | Add **new** jobs — board search, XLSX into named lists, batch launch | "Find new jobs — boards or spreadsheet" |
| `/search` | **Find existing** workspace items — jobs, letters, runs, lists | "Search jobs, letters, and runs you already have" |

Cross-links on both page headers; workspace quick actions include Discover + "Search library".

## Journey matrix

| Entry path | Outcome | Result | Notes |
|------------|---------|--------|-------|
| XLSX @ `/queue` | Jobs in tracker | **Green** | Import wizard; re-import copy; warnings in preview |
| XLSX @ `/discover` upload | Jobs + list attach | **Green** | `attachImportToList` when list selected |
| Board search → accept → list | Jobs in named list | **Green** | Dedupe via accept API |
| List refresh | New candidates | **Green** | `refreshDiscoveryList` |
| List → batch | Preview → enqueue | **Green** | `BatchPreviewDialog` with exclusions |
| Dashboard batch | Preview dry-run / apply | **Green** | Policy picker; pacing note on panel |
| Manual single job add | — | **Gap (documented)** | No `POST /api/job-targets`; use import or discover accept |
| Export → re-import round-trip | App-owned columns preserved | **Green (API)** | `test_xlsx_round_trip.py` in CI |
| Queue → batch | Dashboard / Discover handoff | **Green** | Bulk-select bar links; no dead-end count |

## Seams closed this mission

- Shared `lib/jobs/status-vocabulary.ts` for queue filters and batch exclusion copy
- `BatchPreviewDialog` — included/excluded with reasons; `dry_run` vs `review_before_submit`; auto-submit opt-in note
- Import preview shows full warning list + idempotent re-import messaging
- `QueuePolicyBanner` — pause state + pacing note on `/queue`
- Nav tooltips + page subtitles for Search vs Discover

## Deferrals

| Item | Owner |
|------|-------|
| Full fixture e2e discover → list → batch preview | Mission 26 |
| Manual XLSX round-trip UI walk | Operator post-deploy |
| Manual single job API + form | Future — documented gap |
| Server-side queue filters wired from table | Mission 23 perf (optional) |

## Gates

- Web: typecheck, lint, test, build, e2e
- API: ruff, mypy, pytest; `make test-policy` in CI
