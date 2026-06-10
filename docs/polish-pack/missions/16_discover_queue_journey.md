# Mission 16: Discover → Queue → Batch Journey Coherence

## Purpose
The acquisition half of the golden path — getting jobs *into* the system and *launching* work on them — spans `/discover` (board search, lists, saved searches), `/queue` (tracker table, import/export), and batch creation. These were built in separate missions (03, 13, 23) and must now behave as one coherent journey with no seams, duplicate concepts, or dead ends.

## Context From Audits
Application audit §4 journey 2 and §9 (`/search` vs `/discover` overlap, positioning audit §9/§16). Mission 03 findings file records observed seams. Implementation: `routers/discovery.py`, `job_lists.py`, `job_targets.py`, `imports.py`, `exports.py`, `batches.py`; web `components/discover/`, `components/import/`, `components/jobs/`, queue route.

## Scope
- Walk and fix the four entry paths: XLSX import, board search → list, manual single job add (verify it exists — if absent, that's a *documented gap*, not a build order), and list refresh.
- Resolve the `/search` vs `/discover` confusion: clarify naming/descriptions in nav, or document the deliberate distinction in both UIs (one-line subtitle each); consolidation requires owner sign-off — propose, don't unilaterally merge.
- Import flow polish: dry-run mapping preview legibility, warning presentation, re-import behavior (idempotent updates messaging), export round-trip verified against a real workbook structure (`Direct Job Leads`, `Company Boards`, `Cover Letter Angles`).
- Queue table: status editing inline, filters match batch-preview filters (same vocabulary), fit signals visible, already-applied/dedupe states explained in UI.
- Batch creation: preview → create → enqueue flow shows pacing/quiet-hours consequences plainly; `dry_run` vs `review_before_submit` choice is unmistakable; `auto_submit` remains opt-in-gated and clearly marked.
- Cross-links: a discovered list flows into batch creation in ≤2 clicks (`filters.job_list_id` path).

## Out of Scope
- New discovery sources or board adapters (creep).
- Changes to pacing/lock policy logic (verify and present, don't alter).
- Auto-submit policy changes (policy suite is law: `make test-policy`).

## Starting Checklist
1. Re-read Mission 03 findings for this journey's recorded defects.
2. Read `routers/discovery.py`, `job_lists.py`, `batches.py` response shapes; the README Mission 23 and 13 sections.
3. Walk all four entry paths locally with `make up` + a sample workbook.
4. `grep -rn "search" apps/web/src/app/\(app\)/search` — what `/search` actually does vs `/discover`.
5. Read `apps/api/tests/test_discovery_api.py`, `test_batch_ops.py`, `test_import_api.py` for contracted behavior.

## Tasks
1. Execute the journey matrix (entry path × outcome) and record seams in `docs/polish-pack/notes/16_journey_findings.md`.
2. Fix import UX issues (mapping preview, warnings, re-import messaging); verify export round-trip with the fixture workbook and confirm app-owned columns (status/dates/notes) survive.
3. Implement the `/search` vs `/discover` clarity decision; update nav labels/subtitles.
4. Queue/batch vocabulary alignment (same filter names, same status chips — reuse one component).
5. Tighten the list → batch handoff; verify excluded-jobs explanations (already applied, prior success) appear in preview.
6. Verify policy visibility: quiet hours and pause state surfaced on the dashboard/queue when active.
7. Add/extend tests: API tests for any fixed contract, e2e extension of golden-path smoke to include board-search → list → batch preview.

## Self-Improvement Loop
1. Inspect the next cell of the journey matrix.
2. Identify the highest-impact seam.
3. Make the smallest coherent improvement.
4. Validate (gates + re-walk that path).
5. Document.
6. Repeat until the matrix is seamless.

## Validation
- `cd apps/api && ruff check src tests && mypy src && pytest -q && cd ../.. && make test-policy`
- `cd apps/web && pnpm typecheck && pnpm lint:strict && pnpm test && pnpm build`
- `pnpm test:e2e`
- Manual: full journey matrix re-walk; XLSX round-trip diff (export, re-import, no spurious changes).

## Acceptance Criteria
1. All entry paths reach a batch-ready queue without dead ends; journey matrix recorded green.
2. `/search` vs `/discover` distinction is explicit in the UI (or a consolidation proposal documented for owner sign-off).
3. Export → re-import round-trip is loss-free for app-owned columns.
4. Batch policy choices are unmistakable; policy test suite green.
5. All gates green.

## Documentation Requirements
- `docs/polish-pack/notes/16_journey_findings.md`.
- README corrections for any changed UX described in Missions 03/13/23 sections.

## Git Workflow
`git status` first; commits per journey segment; reviewed diffs; bodies with what/why/validation/follow-ups; push after gates.

## Production Guidance
Deployable after gates pass. The import/export path touches user data — manually verify a production dry-run import (with a disposable account) post-deploy; `bash scripts/railway-smoke.sh`.
