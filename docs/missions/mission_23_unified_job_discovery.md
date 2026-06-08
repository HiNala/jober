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
- [x] Run full CI gates and iteration sweep
- [x] `board_listing` fixture registered in `jober_fixtures` (discovery test path)
- [x] Design review + README verified; web lint/typecheck green locally

## Deferred (non-blocking)
- Redis-backed per-board cooldown enforcement (httpx fetch only today)
- Worker fallback when inline enrich fails on live ATS pages
