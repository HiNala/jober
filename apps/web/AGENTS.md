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

## Layout modes (Mission 09)

- Two in-app layout modes in `lib/workspace/layout.ts`:
  - **ops-desk:** nav + work + resizable canvas — only on `/runs/[id]`
  - **editorial:** nav + full-width content — everywhere else (dashboard, queue, discover, library, search, analytics, settings, admin)
- Never add split-pane to editorial routes.

## Component families (Mission 10)

- Three families in `lib/design/surface-variants.ts`:
  - **marketing:** bento grids, funnel cards, hero surfaces (`surface-marketing-*`)
  - **workspace:** data panels, tables, forms (`surface-workspace-*`)
  - **terminal:** run stream, live view, console (`surface-terminal-*`)
- Use `<Surface family="...">` or `surface.*` tokens; never mix families on the same screen.

## Design tokens (Mission 16, 28)

- Spacing, shadow, radius in `lib/design/tokens.ts`
- Motion vocabulary in `lib/design/motion.ts` — all animations must use motion tokens; `pnpm check:motion` enforces this
- `prefers-reduced-motion` honored globally via `usePrefersReducedMotion()`
- Page states use `components/states/page-states.tsx` (loading, empty, error) — never inline ad-hoc state UI

## E2E selectors (Mission 26)

- Prefer `data-testid` for full-stack Playwright specs (`*.fullstack.spec.ts`); marketing/a11y specs may use roles.
- Convention: `{area}-{action}` — e.g. `batch-enqueue`, `checkpoint-skip`, `studio-generate`, `paragraph-lock-0`.
- Do not rely on marketing copy for full-stack assertions (Mission 27 may change copy).
