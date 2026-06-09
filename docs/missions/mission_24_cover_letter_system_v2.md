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
- [x] Finish leftovers — per-run toggle UI, library duplicate button
- [x] Gates green — ruff, mypy, pytest, web lint/typecheck/build, CI
- [x] Full suite — patch text ATS test, run-options API, letter-options endpoint
- [x] Policy invariants unchanged (claims guard + prompt pack untrusted job page)
- [x] Secrets — detect-secrets baseline clean in CI
- [x] File hygiene — all modules under 2000 lines; per-task commits
- [x] Design Council 20/20 on Document Studio, canvas, settings, run console
- [x] Self-improvement — `PATCH /application-runs/{id}/run-options` + run console control
- [x] Docs — README Mission 24 routes; mission + design-review updated
- [x] Fixture-for-bug — `run_id` FK test; patch text manual_edit regression
- [x] CI green — [27178549543](https://github.com/HiNala/jober/actions/runs/27178549543) on `cc1f6bd`

## Deferred (non-blocking)
- Library “apply to job” UI — duplicate API accepts `job_target_id`; Library only duplicates in place today
