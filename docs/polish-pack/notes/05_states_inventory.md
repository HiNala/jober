# Mission 05 — Page states inventory

**Date:** 2026-06-11 · **Status:** Compliant after Mission 05

| Route | Empty | Loading | Error | Success |
|-------|-------|---------|-------|---------|
| `/dashboard` | **Compliant** — `DashboardFirstRun` when no job targets | `PageLoading` via `dashboard/loading.tsx` + `DashboardContent` | `AppRouteError` + retry | N/A (metrics panel) |
| `/queue` | **Compliant** — `PageEmpty` in table/kanban; import CTA | `PageLoading` | `AppRouteError` + retry | Import wizard done → “View queue” + next-step copy |
| `/discover` | **Compliant** — `CandidateReview` guides search/refresh | `PageLoading` (new) | `AppRouteError` (new) | Toast on accept/batch |
| `/library` (resumes) | **Compliant** — `PageEmpty` + upload CTA | Skeleton rows | `AppRouteError` (new) | Upload toast |
| `/library` (letters) | **Compliant** — `PageEmpty` → Document Studio | Skeleton | shared | — |
| `/library` (jobs/lists) | **Compliant** — `PageEmpty` → Discover | Skeleton | shared | — |
| `/library` (runs) | **Compliant** — `PageEmpty` → queue | Skeleton | shared | — |
| `/search` | **Compliant** — `PageEmpty` before query | `PageLoading` (new) | `AppRouteError` (new) | Result groups |
| `/analytics` | **Compliant** — `PageEmpty` when no activity | `PageLoading` | `AppRouteError` | Charts when data exists |
| `/vault` | **Compliant** — checklist + resume dropzone (`kind=resume`) | `PageLoading` | `AppRouteError` | Upload toast |
| `/documents` | **Compliant** — `PageEmpty` when no jobs | `PageLoading` | `AppRouteError` | Generate toast |
| `/settings` | N/A (form surface) | `PageLoading` | `AppRouteError` | Save toasts |
| `/runs/[id]` | Canvas `PageEmpty` (existing) | `RunConsoleSkeleton` | run console `PageError` | — |

## P0 fixes (UI-REVIEW)

| Issue | Resolution |
|-------|------------|
| Queue `make seed` | `QUEUE_EMPTY` copy + `PageEmpty` + import CTA |
| Vault dropzone spreadsheet text | `FileUpload` `kind="resume"` |
| Blog CMS placeholder | `BLOG_LEAD` user-facing copy |
| Dashboard empty metrics | `DashboardFirstRun` replaces ops panels when queue empty |
| Document studio “seed demo data” | `DOCUMENTS_*` copy |

## Deferred

| Item | Owner |
|------|-------|
| Screenshot re-capture 14–23 | Post-deploy / Mission 31 |
| Sample data toggle | No trivial public API — CTAs point to import |
| Full-page search → ⌘K palette | Mission 09+ |
