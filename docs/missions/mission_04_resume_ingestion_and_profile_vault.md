# Mission 04 — Resume Ingestion & Profile Vault

## Task list
- [x] Resume upload → MinIO → `ResumeAsset` with `is_active`
- [x] PDF/DOCX text extraction + skills index (jsonb)
- [x] Optional embedding id stub (LLM gateway)
- [x] Profile vault tiers: public, preference, sensitive EEO (encrypted JSON)
- [x] Common answers library
- [x] Completeness score + checklist UI
- [x] Vault frontend with consent toggles + encrypted markers
- [x] `fill_policy` guard + unit tests (no consent-less autofill)
- [x] Resume claims index + invented-credential test

## API
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/profile` | Full vault view + checklist |
| PATCH | `/api/profile` | Public + preference fields |
| PATCH | `/api/profile/vault` | Sensitive values + consent |
| GET | `/api/profile/common-answers` | Reusable answer templates |
| PUT | `/api/profile/common-answers/{key}` | Upsert answer body |
| POST | `/api/resumes` | Upload PDF/DOCX |
| GET | `/api/resumes` | List resume assets |

## Acceptance criteria
- Resume uploads extract text and skills
- Sensitive fields ciphertext at rest (`test_encryption` + vault API)
- `never_autofill` → `NEEDS_HUMAN` in fill policy
- Agent cannot populate consent-less sensitive fields (`test_fill_policy`)
- Gates green; Design Council ≥18/20 on vault
