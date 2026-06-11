# Mission 15 — Run console chaos checklist

Recorded pass/fail for `/runs/[id]` reliability hardening. Automated coverage supplements manual checks where Docker/API fixtures are unavailable locally.

## Checklist

| Condition | Expected | Result | Evidence |
|-----------|----------|--------|----------|
| SSE resume via `after_seq` query param | Events after seq only, no duplicates | **Pass** | `test_sse_reconnect_replays_after_seq` |
| SSE resume via `Last-Event-ID` header | Same as `after_seq` | **Pass** | `test_sse_last_event_id_header_resumes_after_seq` |
| SSE burst cap (50 events/poll) | No proxy flood | **Pass** | `test_sse_stream_includes_retry_and_caps_burst` |
| SSE idle heartbeat (15s) | `: heartbeat` comment keeps connection alive | **Pass** | `test_sse_emits_heartbeat_when_idle` (interval patched to 0 in test) |
| Mid-stream reconnect (client) | Snapshot re-fetch + resume seq; "Reconnecting" label | **Pass** | `useRunStream` + `stream-status.test.ts`; UI in `run-console.tsx` / `event-terminal.tsx` |
| Event list pruning (500+ events) | DOM bounded to newest 500 | **Pass** | `prune-events.test.ts`, `MAX_STREAM_EVENTS` |
| Double checkpoint resolve | Server 422, client conflict panel | **Pass** | `test_checkpoint_double_resolve_returns_422`; `checkpoint-card.tsx` conflict UI |
| Checkpoint resolve sync | Console snapshot clears `open_checkpoint` | **Pass** | `test_checkpoint_resolve_from_api`, `test_checkpoint_skip_syncs_console_snapshot` |
| SSE clears checkpoint on peer tab | `human.required` skip/deny/approve clears card | **Pass** | `apply-stream-event.test.ts` |
| Run end states | Summary panel for succeeded/applied/failed/skipped | **Pass** | `run-end-state-summary.tsx` |
| Terminal auto-scroll + scroll lock | Follows tail until user scrolls up | **Pass** | `event-terminal.tsx` |
| Copy event payload | Per-line copy button | **Pass** | `event-terminal.tsx` |
| Kill API mid-stream | Visible reconnecting, no crash | **Pass (code)** | Client sets `connecting` on `EventSource` error when `lastSeq > 0`; manual re-verify in staging |
| Slow 3G throttle | Reconnect backoff (3s) + snapshot fallback | **Pass (code)** | `retry: 3000` server + client `setTimeout(3000)` reconnect |
| Same run in two tabs | Second resolve → conflict on first | **Pass (code)** | 422 conflict UI + `onResolved` → `reconnect()` |
| TUI resolve while web watches | SSE `human.required` or manual Sync | **Pass (code)** | `applyStreamEvent` + Sync button |
| 500+ event fixture run responsive | Pruning keeps list at 500 | **Pass (unit)** | Manual perf check deferred to CI/staging with long fixture run |

## Follow-ups

- Capture `/runs/[id]` screenshots (active, checkpoint, end state) when a seeded fixture run is available in the screenshot script — gap noted for Mission 24 if admin/seed account unavailable.
- Re-run full chaos on staging after deploy (API + web together); `bash scripts/railway-smoke.sh` within 24h.

## Gates (Mission 15 close)

- Web: `pnpm typecheck`, `pnpm lint:strict`, `pnpm test`, `pnpm build`, `pnpm check:motion`, `pnpm test:e2e`
- API: `ruff`, `mypy`, `pytest` (DB tests in CI with `CI=true`)
