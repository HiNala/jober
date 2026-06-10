# Mission 30: Release Candidate, Production Re-Certification, and Post-Launch Checklist

## Purpose
The final integration pass: prove the whole product — after 29 missions of change — is coherent, regression-free, and production-certified. This mission runs everything, deploys the release candidate, re-certifies the live system against the launch checklist, and leaves the owner with a clean post-launch operating loop.

## Context From Audits
Application audit §21 defines the stability bar verbatim — this mission's job is to make every one of its nine criteria true simultaneously. Gates and tools: `docs/polish-pack/notes/gates.md` (M02), the e2e suite (M26), `scripts/staging-golden-path.sh`, `scripts/railway-smoke.sh`, `docs/runbooks/launch-checklist.md`, backup drill (M20), alert drills (M24).

## Scope
- **Full regression run:** every gate, every suite, 2× consecutive; fresh-clone sanity (clone to a temp dir, follow the README, reach a running stack — proves M29).
- **Golden-path triple:** fixture-local (e2e core journey spec), staging gate (`staging-golden-path.sh`) if staging exists, and a real manual production walkthrough post-deploy (signup with a real inbox → verify → import → dry-run batch → watch run → letter → export).
- **Release assembly:** confirm no half-landed work (`git status` clean, no orphaned pack branches), CHANGELOG finalized, version/tag the release (`git tag`), deploy API + worker + web per `docs/runbooks/deploy.md`.
- **Launch checklist execution:** every item in `docs/runbooks/launch-checklist.md` checked or explicitly waived with reason and owner sign-off; this includes the externally-blocked items (legal counsel review of `/acceptable-use`, `LLM_API_KEY` decision) — they get an honest waiver status, not silence.
- **Production re-certification:** smoke script, screenshot re-capture of all 23+ views (the final set — desktop + mobile), Lighthouse spot-check, alert test-fire, backup verification, uptime monitor confirmation.
- **Post-launch loop:** a one-page `docs/runbooks/post-launch.md`: daily/weekly checks (admin overview, cost, backups), where alerts arrive, the rollback command, and when to re-run this pack's Mission 31.

## Out of Scope
- Any new change beyond fixing regressions this mission itself finds (each fix follows Mission 31 rules: smallest change, full re-validation).
- Marketing announcements, pricing activation, or feature flags flips not already decided.

## Starting Checklist
1. Re-read application audit §21 and `docs/runbooks/launch-checklist.md` side by side; merge into one RC checklist.
2. `git log --oneline --grep="pack-"` — confirm every pack mission landed and pushed; `git status` clean.
3. Verify Railway env state matches `infra/railway/variables.example.env` expectations (incl. M11 email vars, M24 alert/Sentry vars).
4. Confirm a fresh production backup exists before deploying (M20 flow).
5. Check open blockers recorded by any mission's notes files — none may be silently open.

## Tasks
1. Fresh-clone sanity drill (temp directory, README only).
2. Full gate run ×2 (api, worker, web, fixtures, policy, e2e, motion, bundles, migrate-check); fix regressions; re-run.
3. Backup production; deploy RC; run `bash scripts/railway-smoke.sh`.
4. Manual production golden path with a real inbox; record every step's result.
5. Execute the merged launch checklist; collect waivers with owner sign-off where external (counsel, LLM key).
6. Final screenshot capture (prod, desktop + mobile) committed; final Lighthouse spot-check; alert test-fire; verify uptime monitor saw the deploy.
7. Tag the release; write `docs/runbooks/post-launch.md`; CHANGELOG release entry.
8. Close out: update `docs/polish-pack/mission_index.md` status table to complete; summarize residual risks in a final section of the application audit.

## Self-Improvement Loop
1. Inspect the next RC checklist item.
2. Identify the highest-impact failing or unverified item.
3. Make the smallest coherent fix (or document the waiver).
4. Re-validate the item **and** re-run the affected suite (a fix here can regress elsewhere — the full gate set is the unit of validation in this mission).
5. Record the evidence.
6. Repeat until the checklist is 100% checked-or-waived and two consecutive full gate runs are green.

## Validation
- Two consecutive full gate runs (every command in `docs/polish-pack/notes/gates.md`).
- `bash scripts/railway-smoke.sh` against production post-deploy.
- Manual production golden path transcript.
- Launch checklist artifact with check/waiver per item.
- Fresh-clone drill log.

## Acceptance Criteria
1. All nine criteria in application audit §21 simultaneously true, with evidence.
2. Production RC deployed, tagged, smoked, and manually golden-pathed.
3. Launch checklist 100% checked or owner-waived; no silent items.
4. Final screenshot + Lighthouse + alert + backup evidence committed.
5. `post-launch.md` exists; mission index closed out; zero unresolved pack blockers.

## Documentation Requirements
- `docs/runbooks/post-launch.md` (new), launch-checklist execution record, final screenshot sets, CHANGELOG release entry, residual-risk summary appended to `docs/polish-pack/audits/00_application_audit.md`.

## Git Workflow
`git status` first and last. RC fixes as individual reviewed commits; release tag (`vX.Y.Z`) created after production verification, not before; final push includes tag (`git push --follow-tags`). Commit bodies for fixes name the regression, root cause, and re-validation.

## Production Guidance
This mission deploys by design — but only after: two consecutive green full-gate runs, a fresh production backup, and the staging gate (if staging exists). Deploy in a window where the owner can respond to alerts. If the production walkthrough fails post-deploy, decide rollback (`docs/runbooks/rollback.md`) vs forward-fix within one hour — do not leave production in an unverified state overnight.
