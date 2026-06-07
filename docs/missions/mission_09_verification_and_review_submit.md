# Mission 09 — Readiness Verification & Review-and-Submit

## Task list
- [x] Verification Agent (`jober-verify`): required fields, uploads, validation errors, submit enabled
- [x] Readiness gate: `verify_ready` → `REVIEW_AND_SUBMIT` on pass; failures → `NEEDS_HUMAN`
- [x] Review-and-submit API + Job Detail panel: summary, fill diff, readiness, Submit / Edit / Skip
- [x] Submission + verification classification (success / already applied / uncertain)
- [x] Idempotency: prior successful runs + on-page already-applied detection
- [x] Success: `JobTarget.status = applied`, `applied_date` stamped
- [x] `auto_submit` gated behind explicit per-batch opt-in (never default)

## API
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/job-targets/{id}/verify-ready` | Run readiness checks (`fixture_html`) |
| GET | `/api/job-targets/{id}/review` | Review package for awaiting run |
| GET | `/api/application-runs/{id}/review` | Review package by run |
| POST | `/api/application-runs/{id}/submit` | Human submit + confirmation capture |
| POST | `/api/application-runs/{id}/skip-submit` | Skip without submitting |

## Acceptance criteria
- Missing required field → readiness fail, no submit step
- Complete fixture → review-and-submit → Submit captures confirmation
- Already-applied fixture detected without re-submit
- Uncertain confirmation → `verify_submission`, not auto-success
- Gates green; Design Council ≥18/20 on review screen

## Iteration clause
- [x] Pre-submit human-readable summary (`build_human_summary`) shown above Submit
