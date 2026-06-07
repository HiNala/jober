# Mission 07 — Form Discovery & Field Mapping

## Task list
- [x] Form scanner: inputs, textareas, selects, combobox/listbox roles, uploads; label evidence
- [x] Field-mapping agent: `mapped_profile_field`, confidence, evidence → `FormFieldObservation`
- [x] Confidence policy: high + non-sensitive → auto-fill eligible; low/ambiguous/sensitive → `needs_review`
- [x] Multi-step detection via `data-step` sections and Next/Continue heuristics
- [x] Resume/cover-letter upload classification
- [x] `proposed_value_redacted` per field (never log raw values)
- [x] Frontend: Discovered fields panel in job detail drawer
- [x] Mapping memory: `(platform, label)` → field key on human confirm (no sensitive values)

## API
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/job-targets/{id}/discover-form` | Scan fixture HTML → observations |
| GET | `/api/job-targets/{id}/field-observations` | Latest discovery for job |
| PATCH | `/api/job-targets/field-observations/{id}` | Edit mapping/status; optional `remember` |

## Acceptance criteria
- Fixture forms produce complete field inventory (single-step, multi-step, dropzone, required, EEO)
- Sensitive fields → `needs_review` even when profile has values
- Low-confidence mappings → `needs_review`, not silent auto-fill
- Upload controls located on dropzone fixture
- Gates green; Design Council ≥18/20 on fields panel

## Iteration (Mission 99)
- [x] Mapping memory on PATCH `remember: true` (platform + label only)
- [x] 422 test when `fixture_html` missing
- [x] README + TS type export for discovered fields panel
- [ ] Browser worker `discover_form` task (deferred to Mission 08)
- [ ] Re-scan after conditional field reveal
