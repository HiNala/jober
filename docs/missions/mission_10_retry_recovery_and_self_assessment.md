# Mission 10 — Retry, Recovery & Self-Assessment

## Task list
- [x] Attempt manager with budgets (3 normal + 1 alternate); `ApplicationAttempt` per try
- [x] Recovery Agent (`jober-recover`): taxonomy, classify, strategy proposal, self-assessment
- [x] Final failure report generator + API/UI surfacing
- [x] Circuit breaker on repeated platform/failure-class events
- [x] Resume-from-checkpoint API
- [x] Failure analytics dashboard (iteration clause)

## API
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/job-targets/{id}/recovery-fill` | Fixture recovery loop with budgets |
| GET | `/api/application-runs/{id}/failure-report` | Actionable failure report |
| POST | `/api/application-runs/{id}/resume` | Resume from last checkpoint |
| GET | `/api/recovery/failure-analytics` | Failure classes by ATS + circuit alerts |

## Acceptance criteria
- Selector failure recovers via label locator on later attempt
- Unrecoverable (forced brittle) exhausts budget + failure report
- Resume continues from checkpoint (not attempt 1)
- Circuit breaker trips at 5 same-class failures
- Gates green
