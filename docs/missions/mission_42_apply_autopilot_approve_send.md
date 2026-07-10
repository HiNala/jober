# Mission 42 — Apply Autopilot: Review, Approve & Send

> **Phase:** Perfection pack  
> **Depends on:** M07–M11, M39, M41  
> **Run Mission 99 after**

## Purpose

Close the product promise: for each selected job, Jober extracts, fills, uploads, verifies — and the user **only has to approve/send** (or resolve a clear checkpoint). Fix pipeline logic gaps, form-fill reliability, review UX, and confirmation archive so the golden path is world-class.

## Context

Core agent pipeline exists through verification and review-and-submit. Residual pain:
- Review package UX may not feel one-tap
- Sensitive fields / CAPTCHA handoff not always CheckpointCard-grade
- Fill diff readability
- Confirmation capture after human submit
- Batch orchestration edge cases
- Broken integrations / flaky recovery paths

## Scope

### In scope
- Review-and-submit UX: ApproveSendBar, fill diff, attachments checklist, sensitive field summary
- Checkpoint flows: login, CAPTCHA, ambiguous field, sensitive missing
- Verification readiness clarity (what’s blocking submit)
- Post-submit confirmation capture + status round-trip to JobTarget / XLSX
- Policy enforcement: default review_before_submit; auto_submit opt-in only
- Reliability fixes in form discovery/fill/upload as bugs found
- Golden path e2e + fixture ATS pages

### Out of scope
- Auto-submit as default
- CAPTCHA solving
- New ATS platforms beyond fixing existing adapters

## Starting checklist
- [ ] Walk fixture golden path locally headed
- [ ] Read verification + fill packages + run console
- [ ] List open defects from `AUDIT_FINDINGS` / polish notes related to runs

## Tasks

### 1. Review package completeness
- [ ] API `ReviewPackage` includes: fields filled/skipped, files, letter, resume, warnings, platform, screenshots
- [ ] UI five-second scan: company/role, completeness %, blockers, diff, Approve / Edit field / Pause
- [ ] Mask sensitive values in diff (show last-4 or ••••)

### 2. Human checkpoints
- [ ] All NEEDS_HUMAN reasons map to CheckpointCard options or free-text where needed
- [ ] Resume after checkpoint without losing fill state
- [ ] Clear copy: “We don’t bypass CAPTCHAs — complete it in the browser, then continue”

### 3. Pipeline hardening
- [ ] Fix known flaky selectors on fixture ATSs
- [ ] Upload both resume + letter; verify attachments
- [ ] Idempotent: already-applied detection
- [ ] Recovery agent produces actionable failure report UI

### 4. After submit
- [ ] Capture confirmation screenshot/DOM
- [ ] Set JobTarget status + applied_date
- [ ] Optional export round-trip status to workbook

### 5. Batch
- [ ] Queue shows per-job state machine cleanly
- [ ] Cooldowns respected; pause/resume
- [ ] Entitlement limits with upgrade CTA (M38)

### 6. Tests
- [ ] Golden path integration + e2e core journey
- [ ] Policy baseline still blocks unsafe modes in CI
- [ ] Form fill sensitive field tests

## Validation
```bash
cd apps/api && pytest tests/test_golden_path_integration.py tests/test_form_fill.py tests/test_verification.py tests/test_recovery.py tests/test_run_console.py -q
cd apps/worker && pytest -q
cd apps/web && pnpm typecheck && pnpm lint:strict
pnpm exec playwright test e2e/core-journey.fullstack.spec.ts e2e/golden-path-smoke.spec.ts e2e/recovery.fullstack.spec.ts
```

## Acceptance criteria
- [ ] Fixture job: import → docs ready → run → review → approve path works without manual DB hacks
- [ ] User never forced to re-type vault data already present
- [ ] Blockers are explicit; Approve disabled until ready (or confirms residual risk)
- [ ] Design Council ≥19/20 review + run console
- [ ] Policy tests green

## Production guidance
- Headed local for debugging; Browserless for server workers
- Watch Playwright version drift
