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

## Iteration (Mission 99)
- [x] Explain panel maps `paragraph_grounding` → resume facts + job keywords
- [x] Template LLM only asserts resume-backed skills (claims guard CI-safe)
- [x] Shared TS types export `cover_letter_hook` / `why_fit`

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
