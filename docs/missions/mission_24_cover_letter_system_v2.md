# Mission 24 — Cover Letter System v2

## Task list
- [x] Generate-letter toggle: global default (Settings) + batch `filters.generate_cover_letter`; skip when off or form has no `cover_letter_upload`
- [x] Templates: Classic, Modern, Compact — ATS-safe PDF/DOCX (Helvetica, selectable text)
- [x] Voice presets: direct, founder_operator, product_minded, technically_credible + legacy mapping
- [x] Inline edit + regenerate: PATCH text, lock paragraphs, regen section; canvas DocumentView
- [x] Per-job tailoring: extraction profile + tracker hook in prompt (Mission 06 / tracker fields)
- [x] Library: duplicate/reuse endpoint, version via `parent_document_id`, lock template for fit lane
- [x] Cost-aware: `LlmCall` with `run_id`, budget governor before batch generation
- [x] A/B tracking metadata in `keyword_coverage.ab_tracking` (template + voice + fit lane)

## Acceptance criteria
- [x] Toggle off skips generation; run continues resume-only when form allows
- [x] Template/voice stored and claims guard tests still pass
- [x] Locked paragraphs preserved; manual PATCH updates ATS score
- [x] Saved letters in Library; duplicate seeds new letter

## API routes

| Route | Purpose |
|-------|---------|
| `GET /api/documents/letter-options` | Templates + voice presets |
| `POST /api/documents/generate-cover-letter` | + `template_style`, `voice_preset`, `run_id`, regen options |
| `PATCH /api/documents/{id}` | Text edit, locks, template/voice metadata |
| `POST /api/documents/{id}/duplicate` | Reuse letter on same or new job |
| `GET /api/documents/{id}` | Full document read |

## Mission 99 (post–Mission 24)
- [x] CI green (193 API tests, web lint/typecheck/build)
- [x] FK fixture for `run_id` → `LlmCall` linkage test
- [x] Design Council 20/20 logged
