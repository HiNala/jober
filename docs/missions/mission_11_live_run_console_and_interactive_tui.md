# Mission 11 — Live Run Console & Interactive TUI

## Task list
- [x] SSE `GET /api/application-runs/{id}/events` (+ `/api/runs/{id}/events` alias)
- [x] Run Console UI at `/runs/[id]` — screenshot, terminal stream, timeline, checkpoint card
- [x] Artifact presigned links per attempt (trace, video, screenshot, DOM)
- [x] SSE reconnect via snapshot + `Last-Event-ID` / `after_seq`
- [x] Rich interactive TUI (`make tui` / `python -m jober_tui`) — no required flags
- [x] Terminal checkpoint resolution via same API as web
- [x] Scrub timeline (iteration clause)

## API
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/application-runs/{id}/console` | Snapshot for reconnect |
| GET | `/api/application-runs/{id}/events` | SSE event stream |
| POST | `/api/application-runs/{id}/checkpoints/{id}/resolve` | Approve / deny / edit / skip |

## Acceptance criteria
- Fill run streams `run.started` + `field.filled` to console
- Checkpoint deny from API updates run to `needs_human`
- SSE `after_seq` replays without full reload
- Trace zip validates as Playwright archive
- Gates green

## Mission 99 (post–Mission 11)
- [x] Dashboard event stream wired to `GET /api/console/recent-events` (was placeholder)
- [x] Checkpoint skip/deny clears `open_checkpoint` in console snapshot (web + TUI share API)
- [x] `run-console.test.ts` + recent-events API test
- [x] Gates green; pushed to `origin/main`
