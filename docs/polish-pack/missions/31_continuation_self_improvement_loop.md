# Mission 31: Continuation / Self-Improvement Loop

**Run this mission between every other mission in this pack.** It is reusable: after Mission 01, after Mission 02, … and once more after Mission 30. It exists because no mission lands perfectly — each one creates small seams (a test that barely passes, a doc line now stale, a component the new pattern didn't reach, a finding parked in a notes file) that compound into mediocrity if not swept immediately.

## Purpose
Consolidate, verify, and refine the previous mission's outcome; absorb necessary adjacent work; and re-raise the whole-product quality bar before the next mission begins. This is where the product becomes *finished* rather than merely *worked on*.

## Operating Rules (read every time)

- You are allowed to handle work that was not explicitly listed in the previous mission if it is necessary to satisfy the previous mission's acceptance criteria or preserve the application's coherence, reliability, usability, accessibility, performance, or product clarity.
- You are not allowed to add unrelated features or expand the product surface area without strong evidence that the addition is necessary. The feature-creep guardrails in `docs/polish-pack/audits/01_product_design_positioning_audit.md` §20 are binding.
- Prefer refinement, repair, simplification, consolidation, and validation over expansion.
- Continue looping until the mission acceptance criteria are met, validation passes, and no obvious high-impact scoped improvements remain.
- Never hide a failure. A red gate is either fixed in this loop or recorded as a blocker in the previous mission's notes file with repro steps.

## Context From Audits
The audits define the destination: application audit §21 (stability criteria) and positioning audit §21 (polish criteria). Every continuation loop moves the product measurably toward those two lists. The design north star is on record: Linear-style focus and typography, Hyper Agents / Figma / 21st.dev craft (UI-REVIEW header + owner direction in Mission 28) — apply it to anything user-facing you touch.

## Scope
1. The previous mission's acceptance criteria — verify each one again, fresh, with its own validation commands.
2. Anything the previous mission changed — its blast radius (callers, consumers, docs, tests, screenshots of touched surfaces).
3. Findings parked in `docs/polish-pack/notes/*` that the previous mission created or that name the just-finished area.
4. Whole-product spot checks (rotate: one route's states, one a11y pass, one chaos condition, one doc command) so quality doesn't silo.

## Out of Scope
- New features, new pages, new dependencies, new surface area (see Operating Rules).
- Starting the next mission's work early.
- Refactors unrelated to the previous mission's blast radius unless they fix an active defect.

## Starting Checklist
1. `git status --short` and `git diff` — anything unstaged/uncommitted from the previous mission? Triage it first; the tree must be clean before this loop ends.
2. `git log --oneline -10` — read the previous mission's commits; re-read its mission doc's Acceptance Criteria and Validation sections.
3. Read the previous mission's notes file in `docs/polish-pack/notes/` (findings, waivers, blockers, follow-ups it recorded).
4. Read `docs/polish-pack/mission_index.md` status and `docs/polish-pack/notes/03_golden_path_findings.md` — any finding assigned to the just-finished mission must now be resolved or re-assigned.
5. Skim the two audit docs' acceptance-criteria sections (§21 each) as the standing bar.

## Tasks
1. **Re-verify:** run the previous mission's full Validation section verbatim. Anything red gets fixed now.
2. **Seam sweep:** inspect the blast radius — callers of changed code, surfaces using changed components (re-capture their screenshots if user-facing: `cd apps/web && PLAYWRIGHT_SKIP_WEB_SERVER=1 PLAYWRIGHT_BASE_URL=<env> node scripts/capture-screenshots.mjs`), docs describing changed behavior, tests asserting old behavior that now pass vacuously.
3. **Debt intake:** collect the previous mission's "known follow-ups" from commit bodies and notes; do each that fits the Operating Rules; re-assign the rest to the owning future mission explicitly (edit that mission doc's Context or the findings file).
4. **Rotate one whole-product spot check** (states / a11y / chaos / docs — pick the least-recently-run; note which in the loop log).
5. **Gate run:** the full gate set from `docs/polish-pack/notes/gates.md` (or, before Mission 02 exists, the union of the previous mission's validation commands).
6. **Document:** append a loop entry (see Documentation Requirements).
7. **Commit & decide deployment** (see below).

## Self-Improvement Loop
1. Inspect the current state of the previous mission's goal and its blast radius.
2. Identify the single highest-impact gap: a failed acceptance criterion > a regression > a seam > a parked follow-up > a spot-check finding.
3. Make the smallest coherent improvement that closes it.
4. Validate: the targeted check first, then the affected suite, then (before ending the loop) the full gate set.
5. Document the result in the loop log.
6. Repeat. **Exit only when all of the following hold:** the previous mission's acceptance criteria all verify green; the full gate set passes; the working tree is clean; and one further inspection pass finds no remaining improvement that is both high-impact and in scope. If you cannot reach that state, record the blocker precisely (what, where, repro, why blocked) and stop.

## Validation
- The previous mission's Validation section, rerun in full.
- The full gate set: `make migrate-check`; api/worker `ruff check src tests && mypy src && pytest -q`; `make test-fixtures && make test-policy`; web `pnpm typecheck && pnpm lint:strict && pnpm test && pnpm build && pnpm check:motion && pnpm check:bundles && pnpm test:e2e`.
- Screenshot re-capture for any user-facing surface touched in this loop.
- `git status --short` empty at exit.

## Acceptance Criteria
1. Every acceptance criterion of the previous mission independently re-verified green (not assumed from its closing state).
2. Full gate set green; zero flakes observed in this loop (a flake found = a flake fixed or quarantined-with-issue).
3. No unstaged/uncommitted changes; no follow-up exists only in a commit message (each is done or re-assigned in writing).
4. The loop log entry exists and names: what was re-verified, what was improved, what was deferred where, and the deployment decision.
5. One rotated whole-product spot check completed and recorded.

## Documentation Requirements
Append to `docs/polish-pack/notes/continuation_log.md` (create on first run) one dated entry per loop:
`## Loop after Mission NN — YYYY-MM-DD` followed by: re-verification results, improvements made (with commits), deferrals (with new owner), spot check run + result, gate summary, deployment decision + outcome.

## Git Workflow
1. `git status` and `git diff` before anything.
2. Stage only files belonging to each fix; one commit per coherent improvement: `fix|chore|docs(scope): summary [pack-31 after NN]`.
3. Commit body: what changed, why, validation performed, known follow-ups.
4. Push only when the full gate set is green and the local workflow authorizes it (repo convention: push at mission boundaries — a completed continuation loop is a boundary).
5. Never hide failures: a red gate at push time means no push — fix or record the blocker.

## Production Guidance
At the end of each loop, decide deployment explicitly and record it. Deploy only when **all** hold: build/lint/typecheck/tests green (full gate set); the primary journey works (e2e core spec, or manual fixture walkthrough before Mission 26 exists); no known security or data-loss risk is open; env/deploy config is ready for the change; the change leaves production coherent (no half of a two-part contract change); and the previous mission's own Production Guidance permits it. When deploying: follow `docs/runbooks/deploy.md`, then `bash scripts/railway-smoke.sh`, and record the outcome in the loop log. When not deploying, write the reason — "not deploying: waiting to batch with Mission NN" is a valid, recorded decision.
