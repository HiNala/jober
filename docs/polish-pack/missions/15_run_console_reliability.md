# Mission 15: Run Console and Live Canvas Reliability

## Purpose
`/runs/[id]` is the product's signature surface — live screenshots over SSE, scrub timeline, artifact views, checkpoint resolution, review-and-submit. It must be bulletproof under real-world conditions: reconnects, long runs, slow networks, concurrent updates. This mission hardens it and polishes its interaction details.

## Context From Audits
Application audit §9 ("unverified: SSE reconnect behavior on flaky networks; checkpoint resolution under concurrent runs") and §13 (SSE `Last-Event-ID` reconnect correctness). Implementation: API `routers/run_console.py` (`GET /api/application-runs/{id}/events` SSE with `after_seq`/`Last-Event-ID`, console snapshot endpoint, checkpoint resolve endpoint); web `components/canvas/` and `components/run-console/`; `run_events` table from build-mission 11.

## Scope
- **Reconnect correctness:** kill/restore the network mid-run; verify no missed or duplicated events (resume from `Last-Event-ID`), a visible "reconnecting…" state, and snapshot re-sync fallback after long disconnects.
- **Long-run behavior:** event list virtualization or pruning so a multi-hundred-event run doesn't degrade the tab; screenshot stream memory (old blobs released).
- **Checkpoint UX:** resolving (approve/deny/edit/skip) is optimistic-but-safe — double-resolve impossible, conflict (already resolved elsewhere, e.g., TUI) handled with a clear state, edit checkpoint preserves input on failure (Mission 12 pattern).
- **Terminal/stream polish:** auto-scroll with scroll-lock-on-user-scroll, LIVE badge pulse via motion tokens, timestamp formatting, copy-to-clipboard on event payloads.
- **Run end states:** SUCCEEDED / FAILED_FINAL / SKIPPED each render a designed summary (artifacts, failure report link, next action) — not just a stopped stream.
- API side: verify SSE keepalive/heartbeat exists for proxy timeouts (Railway); add if missing.

## Out of Scope
- New canvas features (annotations, video export — creep).
- State machine or worker changes beyond what reconnect/heartbeat correctness requires.
- TUI changes (verify parity only where checkpoint conflicts involve it).

## Starting Checklist
1. Read `apps/api/src/jober_api/routers/run_console.py` fully: event sequencing, SSE framing, heartbeat, resolve endpoint semantics.
2. Read `components/canvas/` and `components/run-console/`: EventSource handling, reconnect logic, state stores (Zustand).
3. Read `apps/api/tests/test_run_console*.py` (locate via `ls apps/api/tests | grep -i console`) for the covered contract.
4. Start a fixture run locally (`make up`, fixture flow from Mission 03 notes) to have a live run to test against.
5. Check `docs/runbooks/worker-stuck.md` for known failure modes to reproduce.

## Tasks
1. Build a chaos checklist and execute it: kill API container mid-stream, throttle to Slow 3G, suspend laptop/resume, open the same run in two tabs, resolve a checkpoint from the TUI while web watches.
2. Fix reconnect gaps (client resume params, server `after_seq` correctness, snapshot re-sync); add the reconnecting UI state.
3. Add SSE heartbeat if absent (comment interval or ping event); confirm Railway proxy doesn't sever idle streams.
4. Implement event-list virtualization/pruning and blob lifecycle management; measure with a 500+ event fixture run.
5. Checkpoint resolve hardening: server-side idempotency on resolve (verify; add test), client conflict state, input preservation.
6. End-state summary panels and terminal polish items.
7. Tests: API tests for resume-from-seq and double-resolve; web vitest for the reconnect state machine; extend golden-path e2e to assert checkpoint resolve via UI.

## Self-Improvement Loop
1. Inspect the console under the next chaos-checklist condition.
2. Identify the highest-impact failure.
3. Make the smallest coherent improvement.
4. Validate by re-running that chaos condition plus the standard gates.
5. Document the condition → result in the notes file.
6. Repeat until every chaos condition passes.

## Validation
- `cd apps/api && ruff check src tests && mypy src && pytest -q`
- `cd apps/web && pnpm typecheck && pnpm lint:strict && pnpm test && pnpm build && pnpm check:motion`
- `pnpm test:e2e`
- Manual: full chaos checklist green, recorded in `docs/polish-pack/notes/15_console_chaos.md`.

## Acceptance Criteria
1. Every chaos condition has a recorded pass: no lost/duplicated events, visible reconnect state, no double-resolves, conflicts surfaced.
2. A 500+ event run stays responsive (no unbounded DOM/memory growth).
3. All run end states render designed summaries.
4. SSE survives ≥5 minutes idle behind the production proxy (heartbeat verified).
5. New tests cover resume-from-seq and resolve idempotency; all gates green.

## Documentation Requirements
- `docs/polish-pack/notes/15_console_chaos.md` (chaos checklist + results).
- Update README Mission 18 paragraph if behavior/shortcuts changed.
- Close the screenshot-set gap: capture `/runs/[id]` (active run + checkpoint + end states) into `docs/screenshots/` — the original 23-shot set has no run-detail capture ("no runs in the fresh test account"); use a seeded fixture run. Capture `/admin` views too if an admin account is available, or note the gap for Mission 24.

## Git Workflow
`git status` first; commits per concern (reconnect → heartbeat → virtualization → checkpoint → end states); reviewed diffs; bodies with what/why/validation/follow-ups; push after gates.

## Production Guidance
Deployable after gates + chaos checklist pass; this hardens the core surface. Deploy API and web together (SSE contract may have changed). Verify a real production run's stream within 24h of deploy; `bash scripts/railway-smoke.sh`.
