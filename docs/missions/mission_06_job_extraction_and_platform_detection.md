# Mission 06 — Job Extraction & Platform Detection

## Task list
- [x] Playwright worker: browser context per run, trace + video, screenshots, encrypted storage-state helpers
- [x] Deterministic action API (`goto`, `get_visible_text`, `extract_accessibility_tree`, etc.)
- [x] Platform detection adapters (Ashby → Lever → Greenhouse → Workday → Jobvite → Personio/Teamtailor → generic) with confidence + evidence
- [x] Job Intelligence Agent: normalized `JobProfile` + fit score vs resume skills
- [x] Prompt-injection defense (untrusted page text; injection fixture test)
- [x] Cache `JobProfile` per (job, day)
- [x] Login/CAPTCHA/2FA → `request_human_checkpoint` (no bypass)

## API
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/job-targets/{id}/extract` | Extract via fixture HTML or enqueue browser worker |
| GET | `/api/job-targets/{id}/job-profile` | Read cached profile for today |

## Acceptance criteria
- Fixture ATS pages detect correct platform with evidence
- Populated schema-valid `JobProfile` per fixture
- Injection fixture does not add false credentials to structured fields
- Login fixture → HTTP 409 + `HumanCheckpoint`
- Trace/screenshot keys written on browser path; gates green

## Iteration (Mission 99)
- [x] Per-adapter confidence + evidence on `PlatformDetectionRead`
- [x] Company/product summary extractor feeds cover letter `company_summary`
- [x] CAPTCHA gate API test + `force` cache bypass test
- [x] Celery dispatch warning when worker not reachable
- [x] README local install order for schemas + extraction packages
- [x] Full gates green (61 API + 3 worker tests; web build)
