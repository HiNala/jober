# Mission 08 — Form Filling & File Uploads

## Task list
- [x] Typed action tools over Playwright (`click_by_role`, `fill_by_label`, `upload_file`, etc.) with `BrowserEvent` persistence
- [x] Fill loop: `skipped` (eligible) observations → label/role locators → `filled`/`failed` + fill diff in evidence
- [x] Upload pipeline: MinIO download → `set_input_files` with dropzone fallback
- [x] Sandboxed snippet executor (AST allowlist, typed actions only)
- [x] Sensitive `needs_review` fields → human checkpoint (no auto-fill)
- [x] Per-step screenshots + DOM snapshot keys on fill runs
- [x] Login/CAPTCHA gates → checkpoint (no bypass)

## API
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/job-targets/{id}/fill-form` | Fill via `fixture_html` or enqueue browser worker |

## Acceptance criteria
- Eligible fields on single-step fixture fill via label locators
- Resume + cover letter attach on dropzone fixture
- Sandbox blocks malicious snippet in test
- Login fixture → 409 checkpoint
- Gates green

## Iteration clause
- [x] Fill diff object (`proposed_redacted` / `actual_redacted`) stored per field in `evidence.fill_diff`
