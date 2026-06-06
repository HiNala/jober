# Mission 03 — Job Spreadsheet Import

## Objective
Import the tracker workbook into the database, map every sheet to its entity, and round-trip status changes back out.

## Task list
- [x] `POST /api/imports/jobs-xlsx` (multipart) with `dry_run` preview
- [x] Fuzzy column mapping + preview/confirm in UI
- [x] Upsert by `(Company, Role, Direct apply URL)` with `(Company, Role)` fallback; `import_id` per run
- [x] Normalize trim/dates/URLs/priority/status defaults
- [x] Import warnings in report (never silent drops)
- [x] Frontend drag-drop → mapping preview → import summary
- [x] `GET /api/exports/jobs-xlsx` round-trip (app-owned status/dates/notes)
- [x] Job Queue: table + kanban, filters, bulk select, detail drawer
- [x] ATS guess column + inline status editing with optimistic updates

## API
| Method | Path | Notes |
|--------|------|-------|
| POST | `/api/imports/jobs-xlsx?dry_run=true` | Preview mapping + row counts |
| POST | `/api/imports/jobs-xlsx` | Commit import |
| GET | `/api/exports/jobs-xlsx` | Download workbook |
| GET | `/api/job-targets` | List with filters (`status`, `priority`, `company`, `role`, `location`, `ats_guess`) |
| PATCH | `/api/job-targets/{id}` | Update status, dates, notes |

## Acceptance criteria
- Importing the real workbook: 155 JobTargets, 130 CompanyBoards, 10 CoverLetterAngles (verify with production file)
- Re-import updates in place (no duplicate JobTargets)
- UI status edits appear in exported workbook
- `ruff` / `mypy` / `pytest` + web `typecheck` / `lint:strict` green

## Notes
- Blank apply + careers URLs → `needs_url` warning; excluded from auto-runs until resolved
- Spreadsheet status ignored when application runs exist for a job target
