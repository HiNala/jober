# Forms inventory — Mission 12

**Updated:** 2026-06-11 · Shared utilities: `lib/forms/map-api-errors.ts`, `use-form-submit.ts`, `client-validation.ts`, `file-limits.ts`, `components/forms/form-field.tsx`, `form-error.tsx`.

Legend: **Y** compliant · **P** partial (toast-only or auto-save) · **N** not migrated this mission.

| Form / surface | Client validation | 422 mapping | Pending state | Success feedback | Input preserved on error |
|----------------|-------------------|-------------|---------------|------------------|--------------------------|
| Auth — login | Y (`validateEmail`) | Y (`useFormSubmit`) | Y | redirect | Y |
| Auth — signup | Y (`validateSignup`) | Y + field aliases | Y | redirect / verify-pending | Y |
| Auth — forgot password | Y | Y | Y | success panel | Y |
| Auth — reset password | Y | Y | Y | redirect login | Y |
| Auth — link-google | Y | Y (`useFormSubmit`) | Y | redirect | Y |
| Auth — verify-email / verify-pending | P | Y | Y | message states | Y |
| Marketing — Pro waitlist | Y | Y (`formatApiError`) | Y | inline success | Y |
| Import — XLSX wizard | Y (`validateUploadFile`) | Y (`formatApiError`) | Y (preview/import) | toast + done card | Y (file kept) |
| Vault — resume upload | Y | Y | Y (`busy`) | toast | Y |
| Vault — profile fields | P (server on blur) | Y (`formatApiError`) | blur-save | toast on error | Y + unsaved guard |
| Vault — common answers | P | Y | blur-save | — | Y + unsaved guard |
| Settings — AI key | P (min length) | Y | Y | toast | Y + unsaved guard |
| Settings — app defaults | P | P | mutation | auto-save | Y (instant persist) |
| Settings — privacy delete | P (confirm phrase) | P | Y | redirect | Y |
| Discover — search/upload | P | Y (`formatApiError` elsewhere) | mutations | toast | Y |
| Documents — studio | P | Y | mutations | toast + save tick; 402 panel | P |
| Run console — letter options | P | Y | mutations | toast | P |
| Run console — checkpoint | P | Y | Y | toast | N/A (actions) |
| Library — CRUD forms | P | P | mutations | toast | P |
| Admin — config/users | P | P | mutations | toast | P |
| Jobs — review submit | P | Y | mutations | toast | P |

## Deferred to future missions

- **Owner Mission 25:** full inline migration for discover/documents/library/admin/job forms marked **P** above.
- Full migration of discover/documents/library/admin forms (toast-only errors already use `formatApiError` where wired).
- react-hook-form / zod — **not adopted** (not in deps).
- Upload cancel — API does not expose abort tokens; progress bar deferred.

## Pattern reference

See `apps/web/AGENTS.md` § Forms.
