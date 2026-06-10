# Mission 29: Documentation, Runbooks, and Onboarding Accuracy

## Purpose
This pack changed auth UX, layouts, email, errors, consent, performance characteristics, and deploy-relevant config. Documentation that lies is worse than none: this mission reconciles every doc with the shipped reality, reorganizes the README for a new operator (not just the mission historian), and verifies every runbook by following it literally.

## Context From Audits
Application audit §17: docs are excellent but mission-history-organized and at drift risk; the deploy runbook predates the recent SSL/cookie hotfixes and this pack's changes (email env vars, alert classes, e2e job). The pack itself generated `docs/polish-pack/notes/*` files that need indexing.

## Scope
- **README restructure:** lead with what Jober is + live URLs, then task-organized operator sections (run locally, develop, test, deploy, operate); push mission-by-mission history into a linked appendix or per-feature docs. Every command in the README is re-executed verbatim during this mission — any that fails gets fixed (command or doc).
- **Runbook verification:** walk each of the 9 runbooks (`deploy`, `rollback`, `restore-backup`, `rotate-secrets`, `worker-stuck`, `queue-backed-up`, `infra-down`, `cost-spike`, `launch-checklist`) step-by-step against staging/local where executable; correct drift; add the email-provider runbook from Mission 11 if not already present.
- **Env var truth:** `.env.example` and `infra/railway/variables.example.env` list every variable the code reads (cross-check with a grep of the settings modules), each with a one-line comment; no orphaned or missing vars.
- **CHANGELOG:** summarize this pack's user-visible changes.
- **Architecture docs:** confirm `errors.md` (M18), `threat-model.md` (M21), `motion.md`/`design-tokens.md` (M28), `testing.md` (M26) deltas all landed; fix cross-links.
- **CLAUDE.md / AGENTS.md:** update agent-facing conventions (testids, forms pattern, layout modes, component families) so future agents inherit this pack's decisions.
- Index the pack's notes files from `docs/polish-pack/mission_index.md`.

## Out of Scope
- New tutorial content, video, or docs sites.
- Rewriting the historical mission docs (they are records, not living docs — add a banner note only if actively misleading).

## Starting Checklist
1. `git log --oneline --grep="pack-"` — the full change inventory to reconcile.
2. Read the README top to bottom flagging stale claims (consent banner→sheet, bottom bar→palette, email setup, layout modes…).
3. List code-read env vars: `grep -rn "env\|getenv\|Settings" apps/api/src/jober_api/config*.py apps/worker/src --include="*.py" | grep -i "field\|env"` plus `grep -rn "process.env\|NEXT_PUBLIC" apps/web/src apps/web/next.config.ts`.
4. Skim each runbook noting which steps are executable locally vs staging-only.
5. Check `docs/MISSION_INDEX.md` references the new pack (add a pointer if absent).

## Tasks
1. README restructure + command re-execution sweep (record each command's result in the notes file).
2. Runbook walks with corrections; date-stamp a "last verified" line in each runbook.
3. Env var reconciliation in both example files.
4. CHANGELOG entry; architecture-doc cross-link fixes.
5. CLAUDE.md/AGENTS.md convention updates.
6. Cross-index: `docs/polish-pack/mission_index.md` ↔ notes files ↔ `docs/MISSION_INDEX.md` pointer.

## Self-Improvement Loop
1. Inspect the next doc by *executing* it (commands run, steps followed), not by reading it.
2. Identify the highest-impact inaccuracy.
3. Make the smallest coherent correction (fix the doc, or fix the code/script if the documented behavior is the right one).
4. Validate by re-executing.
5. Mark the doc verified with date.
6. Repeat until every doc in scope carries a current verification.

## Validation
- Every README command executed successfully on this machine (or marked with its real platform requirement, e.g. "Git Bash/WSL").
- Each runbook carries a "last verified: 2026-MM-DD" line backed by the walk.
- `git grep -n "make seed" docs README.md` and similar stale-claim greps return only intentional references.
- Full gates (`docs/polish-pack/notes/gates.md`) still green if any code/scripts changed.

## Acceptance Criteria
1. A new operator can go from clone to running stack to first dry-run using only the README, with zero failing commands.
2. All 9+ runbooks verified and date-stamped.
3. Env example files complete and accurate against code.
4. CHANGELOG current; agent convention files updated; indexes cross-linked.
5. No doc claims contradicted by the shipped product.

## Documentation Requirements
This mission *is* documentation; additionally record the command-sweep results in `docs/polish-pack/notes/29_doc_verification.md`.

## Git Workflow
`git status` first; commits per doc area (`docs(readme): task-organized operator guide [pack-29]`); reviewed diffs; push after gates.

## Production Guidance
Docs-only changes deploy trivially (no app deploy needed unless scripts changed). If a runbook walk uncovered a real config defect in production, fix it under Mission 31 rules with its own deployment decision.
