# Mission 12: Forms, Input States, and Validation Consistency

## Purpose
The app is form-heavy: auth, profile/vault, settings, import mapping confirmation, batch creation, discovery filters, document options, checkpoint edit. Validation behavior, error presentation, and pending states likely drifted across 35 build missions. This mission makes every form behave identically: validate predictably, fail readably, never lose user input.

## Context From Audits
Application audit §9 (UX) and §13 (error-handling consistency unverified); UI-REVIEW notes on default-looking inputs. The API uses Pydantic v2 — 422 responses have a known shape; the web must render them consistently rather than ad hoc per form.

## Scope
- Inventory every user-facing form in `apps/web/src` (auth pages, `(app)/settings`, vault editor in `components/vault/`, import flow in `components/import/`, batch creation, discovery filters in `components/discover/`, document generation options in `components/documents/`, checkpoint resolution edit in `components/canvas/` or `run-console/`).
- Standardize: inline field errors (from both client checks and API 422 field paths), form-level error slot, pending/disabled submit with spinner, success feedback (sonner toasts are installed — use consistently), unsaved-changes guard on heavy editors (vault, settings).
- Client validation mirrors server rules where cheap (required, formats, lengths); server remains authoritative.
- Map Pydantic 422 `loc` paths to fields in one shared helper, not per form.
- File inputs (resume upload, XLSX import): size/type validation with clear errors before upload; progress state during upload.

## Out of Scope
- New form libraries (no react-hook-form/zod adoption unless already present — verify first; build on what exists).
- API validation rule changes (only fix server messages that are user-hostile, and only with tests).
- Form *layout* redesign (families handled in Mission 10).

## Starting Checklist
1. `grep -rln "onSubmit\|useMutation" apps/web/src/components apps/web/src/app` — build the form inventory.
2. Read 2–3 representative forms (login, vault PATCH, import upload) to catalog current patterns.
3. Read one API 422 response body (hit a validation error locally) to design the shared error mapper.
4. Check `components/ui/` for existing field/error primitives.
5. Check how TanStack Query mutations surface errors today.

## Tasks
1. Write the inventory table (`docs/polish-pack/notes/12_forms_inventory.md`): form × {client validation, 422 mapping, pending state, success feedback, input-preservation on error}.
2. Build shared utilities: `mapApiErrors()` (422 → field map), a `FormField` error slot convention, a `useFormSubmit`-style mutation wrapper if a pattern is repeated ≥3 times.
3. Migrate forms worst-first; preserve input values on every failure path (test by killing the API mid-submit).
4. File inputs: pre-upload checks (XLSX mime/size per `routers/imports.py` limits; resume PDF/DOCX per `routers/resumes.py`), progress + cancel where the API supports it.
5. Unsaved-changes guard on vault and settings editors.
6. Vitest coverage for the shared utilities and one migrated form per pattern; e2e: one negative-path test (submit invalid signup, assert inline errors).

## Self-Improvement Loop
1. Inspect the next form in the inventory with forced failures (empty submit, server 422, network kill).
2. Identify the highest-impact inconsistency.
3. Make the smallest coherent improvement.
4. Validate (gates + the forced-failure pass).
5. Update the inventory row.
6. Repeat until every row is compliant.

## Validation
- `cd apps/web && pnpm typecheck && pnpm lint:strict && pnpm test && pnpm build`
- `pnpm test:e2e`
- `cd apps/api && pytest -q` (if any server messages changed)
- Manual: forced-failure pass per inventory row; no form loses typed input on error.

## Acceptance Criteria
1. Inventory complete; every form compliant on all five columns.
2. 422 field errors render inline on every migrated form via the shared mapper.
3. Every submit has a pending state; double-submit is impossible.
4. No form loses user input on any failure path.
5. All gates green.

## Documentation Requirements
- `docs/polish-pack/notes/12_forms_inventory.md` with final compliance state.
- Brief pattern doc in `apps/web/AGENTS.md` or `CLAUDE.md` so future forms follow it.

## Git Workflow
`git status` first; commits: shared utilities → per-area migrations; diffs reviewed; bodies cover what/why/validation/follow-ups; push after gates.

## Production Guidance
Deployable after gates pass; behavior-improving but contract-neutral. Batch with neighboring UI missions if preferred; smoke after deploy.
