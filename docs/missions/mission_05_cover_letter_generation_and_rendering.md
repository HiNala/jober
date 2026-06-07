# Mission 05 — Cover Letter Generation & Rendering

## Task list
- [x] Deterministic prompt pack (resume = truth; job page untrusted)
- [x] Claims guard with retry + rejection
- [x] ATS keyword extraction, coverage, stuffing penalty
- [x] PDF (ReportLab) + DOCX rendering → MinIO
- [x] `POST /api/documents/generate-cover-letter` + downloads
- [x] Fit lane → resume variant mapping
- [x] Document Studio UI + explain panel
- [x] LLM gateway with `LlmCall` logging + monthly budget cap

## Mission 99 (post–Mission 05)
- [x] Documents API integration test (generate + PDF download route)
- [x] Prompt pack policy tests (job-page untrusted section)
- [x] Document Studio: resume gate + word count display
- [x] Budget exceeded API test (HTTP 402 fixture)
- [x] `formatApiError` — clear toasts for budget cap / claims guard / missing resume
- [x] `.env.example` LLM vars aligned with `Settings` field names
- [x] Full gates green: ruff, mypy, pytest (45+), web lint/typecheck/build, detect-secrets

## API
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/documents/generate-cover-letter` | Generate/cache cover letter |
| GET | `/api/documents?job_target_id=` | List documents for job |
| GET | `/api/documents/{id}/download/pdf` | Download PDF |
| GET | `/api/documents/{id}/download/docx` | Download DOCX |

## Acceptance criteria
- Grounded letter + coverage + PDF for real job (template LLM when no API key)
- Claims guard rejects injected false credential in tests
- Stuffing penalty test passes
- `LlmCall` rows + budget block test
- Gates green; Design Council ≥18/20 on Document Studio
