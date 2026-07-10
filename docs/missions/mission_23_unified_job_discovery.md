# Mission 23 — Unified Job Discovery & List Building

## Task list
- [x] Single `/discover` surface: Search for jobs + Upload a list (XLSX)
- [x] Board search from tracker company boards + user-provided careers URLs
- [x] Candidate review with fit signal, source, and selection
- [x] List building: accept into named list with dedupe (Mission 03 upsert key)
- [x] Auto-enrich accepted jobs via inline extraction + ATS guess
- [x] Batch launch from saved list (`job_list_id` filter)
- [x] Saved searches + refresh list for new openings (iteration clause)

## Acceptance criteria
- [x] Build a list by searching boards **and** uploading XLSX into the same named list
- [x] Candidates show fit signal and source; accepting creates `JobTarget`s
- [x] Saved lists in Library; launch batch from list
- [x] Design Council ≥18/20 on discovery surface

## API routes

| Route | Purpose |
|-------|---------|
| `POST /api/discovery/search` | Query boards + tracker; return candidates |
| `POST /api/discovery/accept` | Accept candidates into list (dedupe) |
| `POST /api/discovery/lists/{id}/refresh` | New candidates only |
| `POST /api/discovery/lists/{id}/attach-import` | Attach XLSX import run to list |
| `GET/POST /api/discovery/saved-searches` | Saved search CRUD |
| `PATCH /api/discovery/lists/{id}/saved-search` | Link list to saved search |
| `POST /api/batches` with `filters.job_list_id` | Batch from list |

## Notes
- Discovery uses user-chosen boards/URLs; respects site cooldowns via httpx fetch (no mass crawl)
- Fit scoring is advisory keyword overlap vs active resume skills
- Company boards are tenant-scoped after migration `l4h1i2d23e47`

## Mission 99 (post–Mission 23)
- [x] Finish leftovers — all task + acceptance criteria verified
- [x] Gates green — CI backend, policy, web (lint, typecheck, build, test)
- [x] Full suite green — discovery + board parser + batch list filter tests added
- [x] Policy invariants — discovery does not touch fill/submit/CAPTCHA paths; policy job blocking in CI
- [x] Secrets — `detect-secrets` baseline clean in CI
- [x] File hygiene — discover modules under 500 lines; per-task commits on `main`
- [x] Design Council — 20/20 on `/discover` (see `design-review.md`)
- [x] Self-improvement — accept dedupes duplicate rows in one request; returns `skipped_duplicates`
- [x] Docs — README `/discover` blurb; mission + design-review updated
- [x] Fixture-for-every-bug — `board_listing` in `jober_fixtures`; parser unit tests

## Deferred (non-blocking)
- Redis-backed per-board cooldown enforcement (httpx fetch only today)
- Worker fallback when inline enrich fails on live ATS pages

---

## Residual perfection (2026-07) → Mission 40

| Residual gap | Owner mission |
|--------------|---------------|
| Explainable fit score v2 (reasons chips, ranking) | **M40** |
| Candidate UX + bulk accept on 2030 shell | **M40** |
| Saved search refresh reliability | **M40** |
| Seamless handoff to document prep + batch | **M40** → M41/M42 |
| Redis board cooldowns (if still open) | **M40** if in scope, else note |
