<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

## Forms (Mission 12)

- **422 errors:** `mapApiErrors()` in `src/lib/forms/map-api-errors.ts` — never parse `detail` ad hoc.
- **Submit flows:** `useFormSubmit()` for pending + form/field errors; disable submit while `pending`.
- **Fields:** `FormField` + `fieldDescribedBy()` for labels and inline errors; `FormError` for form-level alerts.
- **Client rules:** `client-validation.ts` mirrors server bounds (password ≥10, email format).
- **Uploads:** `validateUploadFile()` before calling the API; show errors in `FileUpload`.
- **Heavy editors:** `useUnsavedChanges(dirty)` on vault drafts and settings API-key entry.
- **Toasts:** `formatApiError()` from `src/lib/api/errors.ts` for mutation failures.
