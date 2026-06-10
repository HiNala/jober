# Application Audit — Jober

**Audit date:** 2026-06-10
**Auditor scope:** full repository inspection (code, docs, tests, CI, deployment config, production screenshots)
**Companion doc:** [`01_product_design_positioning_audit.md`](01_product_design_positioning_audit.md)

---

## 1. Executive summary

Jober is a **functionally complete, already-deployed product** — not a prototype. Thirty-five build missions (`docs/missions/mission_00_*` through `mission_34_*`) have been executed, CI is real, the test suite is large (60+ API test files, worker tests, web vitest + Playwright e2e), and the app is live on Railway (web: `web-production-29902.up.railway.app`, API: `api-production-4b5b.up.railway.app`).

The improvement opportunity is therefore **not feature building**. It is:

1. **Land in-flight work.** 18 modified files and 5 untracked paths sit uncommitted on `main` (formatting cleanups, a local-dev web Docker service, a screenshot pipeline, the start of UI polish work).
2. **Close incomplete flows.** Email verification tokens are created but outbound email is not configured — signup verification and password reset are dead ends in production. The Pro plan card is displayed but not purchasable.
3. **Execute the existing UI review.** `docs/screenshots/UI-REVIEW.md` (23 production screenshots, captured 2026-06-10) documents seven "generic template" patterns and six priority upgrade themes that have not yet been implemented.
4. **Validate, then harden.** Recent commit history (`SameSite=None` cookies, Railway SSL fixes) shows production fire-fighting; the deployment surface needs systematic re-validation rather than more change.
5. **Deepen the thin spots:** in-app e2e coverage (only 2 Playwright specs, axe only on marketing routes), responsive behavior of the workspace shell, and copy polish (dev copy like `make seed` appears in production empty states).

A coding agent following this pack should make the existing product excellent — coherent, reliable, beautiful — and resist adding surface area.

## 2. What the app appears to be

**Jober** is an *assisted application autopilot* for high-volume, high-quality job applications, built by/for Brian Permut and productized as a multi-tenant SaaS (Free/Pro plans). For each job in a tracked queue it opens the apply URL in a real Playwright browser, detects the ATS (Ashby/Lever/Greenhouse/Workday/etc.), extracts the job, generates a grounded cover letter, fills the form from an encrypted profile vault, verifies readiness, and hands the human a **review-and-submit** checkpoint. Explicit non-goals (documented in `docs/MASTER_PLAN.md` §0): no CAPTCHA bypass, no bot-detection evasion, no unattended mass submission. Default policy is `review_before_submit`.

## 3. Current architecture overview

Monorepo, pnpm + pip, Docker Compose for local dev, Railway for production.

| Piece | Stack | Location |
|---|---|---|
| Web | Next.js 16.2.7 (App Router), React 19, Tailwind 4, shadcn/Base UI, TanStack Query, Zustand, Recharts | `apps/web` |
| API | FastAPI, Pydantic v2, SQLAlchemy 2 async, Alembic, 28 routers | `apps/api` |
| Worker | Celery + Playwright Chromium (headed locally, Browserless option) | `apps/worker` |
| TUI | Rich interactive console | `apps/tui` |
| Shared packages | `schemas` (Pydantic → generated TS types), `extraction`, `forms`, `fill`, `recovery`, `verification` | `packages/` |
| Infra | `infra/compose.yaml` (+ new root `compose.yaml` include), Dockerfiles in `infra/docker/`, Railway `*.railway.toml`, nginx, backup scripts | `infra/` |
| Data | Postgres (source of truth), Redis (queue/locks/sessions), MinIO (artifacts, tenant-prefixed keys) | compose services |
| Fixtures | Synthetic ATS pages for offline CI | `fixtures/ats` |

Key web internals: design tokens in `apps/web/src/lib/design/tokens.ts`, motion vocabulary in `lib/design/motion.ts` (enforced by `pnpm check:motion`), shared page states in `components/states/page-states.tsx`, workspace shell in `components/workspace/`, live canvas in `components/canvas/`, analytics SDK in `lib/analytics/sdk.ts`.

Key API internals: RBAC permission registry in `auth/permissions.py` (startup-validated — every route must declare a permission), write-time redaction for events/LLM audit rows, LLM gateway with monthly budget hard-stop (HTTP 402), first-party analytics with Celery rollups.

## 4. Current user journeys

1. **Marketing → signup:** `/` → `/features` / `/how-it-works` / `/pricing` / `/faq` → `/signup` (native Argon2id auth, optional Google OAuth) → email verification token created (**but never emailed — broken in production**) → `/dashboard`.
2. **Golden path (core product):** import tracker XLSX at `/queue` (or board search at `/discover`) → profile/vault at `/settings` (with `/vault` redirect) → batch preview/create → run: extract → generate letter → discover form → fill → verify-ready → `/runs/[id]` live canvas → human review-and-submit → confirmation + artifacts.
3. **Document studio:** `/library` (letters tab) and `/documents` redirect — generate/edit/duplicate/download cover letters.
4. **Analytics:** `/analytics` (user), `/admin` (ops: overview, acquisition, runs, cost, system, flags).
5. **Recovery:** failure reports in job drawer, resume-from-checkpoint, circuit-breaker alerts.

## 5. Current feature inventory

(Each maps to a completed mission; see `docs/MISSION_INDEX.md`.)

- XLSX import/export round-trip (`routers/imports.py`, `exports.py`, `services/xlsx/`)
- Profile vault with field-level encryption + consent flags (`routers/profile.py`, `VAULT_ENCRYPTION_KEY`)
- Resume ingestion + parsing (`routers/resumes.py`, `services/resume_parser.py`)
- Job extraction + ATS platform detection (`routers/job_extraction.py`, `packages/extraction`)
- Form discovery / mapping memory / fill / readiness verification / review-submit (`routers/form_discovery.py`, `form_fill.py`, `verification.py`)
- Retry & recovery with attempt budgets and failure analytics (`routers/recovery.py`, `packages/recovery`)
- Live run console: SSE events, scrub timeline, checkpoint resolution (`routers/run_console.py`, web `components/canvas/`)
- Batch ops: pacing, per-domain locks, quiet hours, pause/resume (`routers/batches.py`)
- Cover letter system v2: templates, voices, locking, PDF (`routers/documents.py`)
- Unified discovery: board search, saved searches, named lists (`routers/discovery.py`, `job_lists.py`)
- Native auth + Google OAuth + sessions/CSRF (`routers/auth.py`, `services/auth/`)
- Multi-tenant + billing plans + Stripe webhook (`routers/billing.py`, `webhooks.py`)
- Privacy: purge, export-all, delete-all (`routers/privacy.py`)
- First-party analytics + rollup dashboards (`routers/analytics.py`, `analytics_dashboard.py`)
- RBAC + admin dashboard (`routers/admin.py`, `admin_dashboard.py`)
- Marketing site: landing, features, how-it-works, pricing, blog, FAQ, legal
- Ops: webhook alerts, Sentry hook, uptime script, runbooks (`docs/runbooks/`)

## 6. What works now

- **CI is green** on recent main (per `docs/MASTER_PLAN.md` M99 closeout notes and commit `a62aed1`).
- **Quality gates exist and are enforced:** `make lint` (ruff + mypy api/worker + web lint/typecheck/vitest), `make test`, `make test-fixtures`, `make test-policy`, `pnpm build`, `pnpm check:motion`, `pnpm check:bundles`.
- **Production is live** and smoke-checkable: `scripts/railway-smoke.sh`, `scripts/staging-golden-path.sh`, `scripts/uptime-check.sh`.
- **Safety spine is real:** policy test suite (`pytest -m policy`), sensitive fields default never-auto-fill, CAPTCHA/login → human checkpoint, write-time redaction.
- **Migrations are drift-checked** (`make migrate-check`, `apps/api/scripts/check_migration_drift.py`, `tests/test_migration_drift.py`).

## 7. What appears broken, incomplete, fragile, or unclear

Ranked; each item references evidence.

1. **Uncommitted working tree on `main`** — 18 modified files (mostly ruff re-formatting in API services/tests, a new worker DB-URL test, compose `web` service) and 5 untracked paths (`compose.yaml` root include, `infra/docker/Dockerfile.web`, `apps/web/scripts/capture-screenshots.mjs`, `apps/web/src/components/product/announcement-banner.tsx`, `docs/screenshots/`). In-flight, unvalidated, unlanded.
2. **Outbound email is not configured** (README: "email verification tokens are created but outbound email is not configured yet"). Signup verification and `/forgot-password` → `/reset-password` are dead ends in production. This is the single largest broken flow.
3. **LLM in production may be the stub template provider** unless `LLM_API_KEY` was set (README documents the command but not confirmation). Discovery task: verify prod behavior.
4. **UI genericness** — fully documented in `docs/screenshots/UI-REVIEW.md`: consent toast overlapping content on nearly every screen, identical 40/60 split-pane on all in-app routes, default shadcn card grids on marketing, dev copy (`make seed`) in the production queue empty state, unbranded auth pages.
5. **Pro plan is a dead card** on `/pricing` (not purchasable; Stripe webhook exists but no checkout). Either ghost it with a waitlist or wire checkout — decided in the positioning audit.
6. **Legal pages are drafts** (`/acceptable-use` explicitly "requires counsel before launch").
7. **Deployment fragility signals:** four of the last six commits are production hotfixes (Railway Postgres SSL ×2, cookie SameSite, URL rewriting). The worker `?ssl=disable` handling was being patched in the uncommitted diff.
8. **Thin in-app e2e coverage:** `apps/web/e2e/` holds only `a11y-marketing.spec.ts` and `golden-path-smoke.spec.ts`; axe runs against marketing routes only, not `/dashboard`, `/queue`, `/runs/[id]`, `/settings`.
9. **Windows dev friction:** backup/restore require Git Bash/WSL; the new `Dockerfile.web` + compose `web` service (uncommitted) exists precisely because host `node_modules` leaked into Linux containers.
10. **Possible repo hygiene issues:** `apps/web/test-results/` and `tsconfig.tsbuildinfo` exist in the working tree — verify they are gitignored.

## 8. UI audit

`docs/screenshots/UI-REVIEW.md` is the authoritative, current UI audit (23 prod screenshots at 1440×900, per-screen findings). Summary of its findings, which this pack adopts wholesale:

- **Works:** coherent dark system, clear human-in-the-loop story, "ops desk" app chrome, logical IA.
- **Generic patterns to fix:** default shadcn card grids (features/pricing/FAQ), indistinguishable Geist + teal eyebrow + blue CTA marketing, floating analytics consent toast on nearly every screen, identical split layout on all in-app routes, pasted-on bottom "Describe what you want…" bar (should be ⌘K palette), dev copy in empty states, auth pages on an empty void.
- **Priority themes:** (1) one distinctive brand layer used sparingly, (2) layout discipline — split-pane only on run/watch surfaces, (3) component tiering (marketing bento ≠ data table ≠ terminal), (4) purposeful motion via existing `motion.ts` tokens, (5) empty states as onboarding, (6) consent as a one-time bottom sheet.
- **P0 quick wins from the review:** fix user-facing copy bugs (queue empty state `make seed`, settings/vault dropzone wrong text, blog CMS-note leak); tame the consent banner; hide the **non-functional** bottom AI bar and add a ⌘K command palette; first-run onboarding on the empty dashboard.
- **Owner design direction (binding):** Linear-style focus — centered hero with the product preview in the center, larger navigation text and overall type scale, elegant micro-interactions everywhere they communicate state, with component patterns sourced from 21st.dev / v0 / comparable libraries and rebuilt on Jober's tokens.

Missions 04–10 and 27–28 in this pack implement that review screen by screen.

## 9. UX audit

- **Strong:** review-before-submit checkpoint model; masked fill diffs; failure reports with recommended manual action; import dry-run preview with column mapping; keyboard shortcuts in workspace shell (⌘B/⌘\\/⌘/).
- **Weak:** first-run experience — a new production user lands on `/dashboard` with empty data and dev-flavored guidance; no sample-data or guided "import your tracker" moment. Consent banner interrupts every page until dismissed. The signup → verify → (no email arrives) → confusion path is a trust-destroying UX hole. `/documents` and `/vault` are redirects — verify no stale nav links point at them.
- **Unverified:** SSE reconnect behavior on flaky networks on `/runs/[id]`; checkpoint resolution UX under concurrent runs; mobile usability of the three-pane workspace (almost certainly poor at <768px — needs audit, see Mission 15).

## 10. Accessibility audit

- **In place:** `@axe-core/playwright` wired in `e2e/a11y-marketing.spec.ts`; `prefers-reduced-motion` honored globally (Mission 19); Base UI primitives are accessibility-positive.
- **Gaps:** no axe coverage of authenticated app routes; no documented keyboard path through the golden path (queue → run → checkpoint resolve → submit); focus management in drawers/command bar unverified; Recharts charts need text alternatives; color-contrast of low-contrast outline icons flagged in UI-REVIEW. Mission 14 covers this.

## 11. Responsive design audit

Marketing pages presumably responsive (standard Next/Tailwind patterns) but unverified below 1440×900 — all 23 screenshots are desktop. The three-pane workspace shell (`components/workspace/`) with resizable panels is a desktop-first design; behavior at tablet/phone widths is undocumented and untested (no viewport-parameterized e2e). Mission 15 covers this.

## 12. Performance audit

- **In place:** bundle budget checker (`pnpm check:bundles`, `scripts/check-bundle-budget.mjs`); Mission 32 (perf/load/resilience) was executed; analytics dashboards read rollups, never raw event scans; `test_load_smoke.py` exists.
- **To verify:** Recharts and canvas components are heavy — confirm they are code-split out of marketing/auth bundles; LCP on `/` with the hero mockup; SSE event volume on long runs; Celery rollup duration as `AnalyticsEvent` grows. Missions 23–24 cover this.

## 13. Reliability and error-handling audit

- **In place:** retry taxonomy with attempt budgets (3 normal + 1 alternate), resumable checkpoints, circuit breakers with admin attention items, failure reports, idempotency ("already applied" detection), per-domain locks.
- **To verify:** API error response shape consistency across 28 routers (likely drifted across 35 missions); web error boundaries per route group; SSE `Last-Event-ID` reconnect correctness; behavior when MinIO/Redis are down (`/readyz` vs runtime). Missions 16, 19 cover this.

## 14. Security and data-handling audit

- **In place:** Argon2id, Redis cookie sessions + CSRF, RBAC with startup validation, field-level vault encryption, write-time redaction (`LOG_MODE=redacted`), presigned URL TTL (15 min), tenant-prefixed MinIO keys, prompt-injection defense posture (page text is data, not instructions), production boot refusal on placeholder secrets / `DEV_AUTH_BYPASS`, threat model doc (`docs/architecture/threat-model.md`), `.secrets.baseline` (detect-secrets), pre-commit hooks.
- **To re-verify:** `SameSite=None` cookie change (commit `67e04b7`) implications — `None` requires `Secure` and broadens CSRF exposure; confirm CSRF token enforcement still covers all mutating routes. Tenant isolation test (`test_tenant_isolation.py`) was just modified in the uncommitted diff — confirm it still passes. Dependency audit (pip + pnpm) has no scheduled cadence. Mission 22 covers this.

## 15. Testing and validation audit

- **API:** 60+ test files including golden-path integration, tenant isolation, policy markers, migration drift, load smoke. Strong.
- **Worker:** targeted tests (db URL, fixture browser). Adequate.
- **Web:** vitest configured; component test depth unknown (discovery task); e2e thin (2 specs).
- **Fixtures:** synthetic ATS catalog with its own tests (`make test-fixtures`). Strong and CI-safe.
- **Gap:** no e2e of authenticated app flows (login → import → batch → run console); axe app-route coverage; visual regression is manual (screenshot script is new and uncommitted). Missions 25–26 cover this.

## 16. Code quality and maintainability audit

- Ruff + mypy enforced on api/worker; ESLint strict + tsc on web; custom eslint rules dir (`apps/web/eslint-rules/`) and motion-token checker show above-average discipline. Files-under-2000-lines convention documented.
- The uncommitted diff is itself mostly formatting normalization — suggests a recent ruff config change not yet landed; land it (Mission 01) before anything else, or every future diff is polluted.
- 28 routers / 25+ service modules is a lot of surface; no dead-code sweep has happened post-launch (e.g., Clerk auth mode retained alongside native auth — verify it's still wanted).

## 17. Documentation audit

- **Excellent:** README (23 KB, accurate command tables), `MASTER_PLAN.md`, per-mission docs, architecture docs (rbac, threat-model, testing, motion, product, design-tokens), 9 runbooks, launch checklist, CHANGELOG.
- **Risks:** README is mission-history-organized ("Mission 04", "Mission 23"…) rather than user-task-organized — fine for the owner, harder for a new operator. Some docs may have drifted from the deployed reality (e.g., deploy runbook vs the recent SSL hotfixes). Mission 29 covers this.

## 18. Deployment readiness audit

- **Live:** Railway production with private Postgres/Redis/storage, per-service `*.railway.toml`, production Dockerfiles, boot-time secret enforcement, backup/restore scripts, uptime cron, ops alert webhook, launch checklist.
- **Open:** outbound email (blocker for real users), `LLM_API_KEY` confirmation, legal counsel on draft pages, MinIO Railway config just modified (uncommitted `infra/railway/minio.railway.toml` diff — validate before deploy), staging golden-path gate should be re-run after the in-flight work lands.

## 19. Prioritized risk list

| # | Risk | Severity | Mission |
|---|---|---|---|
| 1 | Uncommitted work on `main` lost or half-landed | High | 01 |
| 2 | Signup verification / password reset dead-end (no email) | High | 11 |
| 3 | Quality gates not re-validated after in-flight diff | High | 02 |
| 4 | Golden path regression undetected in prod (recent hotfix churn) | High | 03 |
| 5 | Consent toast degrading every page's UX | Medium | 04 |
| 6 | Generic UI undermining positioning (full UI-REVIEW backlog) | Medium | 06–10, 27–28 |
| 7 | `SameSite=None` cookie / CSRF surface unreviewed | Medium | 20, 22 |
| 8 | No e2e or axe coverage of authenticated app | Medium | 14, 26 |
| 9 | Workspace shell unusable on mobile (unverified) | Medium | 15 |
| 10 | Legal pages unreviewed by counsel | Medium (external) | 30 (gate) |
| 11 | Stub LLM provider silently active in prod | Medium | 03 |
| 12 | Doc drift vs deployed reality | Low | 29 |

## 20. Recommended mission sequence

See [`docs/polish-pack/mission_index.md`](../mission_index.md). Order: land in-flight work → re-green gates → validate golden path → execute UI-REVIEW fixes (consent, states, auth, marketing, layout, components) → close the email flow → forms/a11y/responsive → core-surface reliability (run console, discovery/queue, documents) → backend hardening (errors, auth, DB, security) → performance → observability → test depth → copy/brand polish → docs → RC → launch re-certification. Run Mission 31 (continuation loop) between every mission.

## 21. Acceptance criteria for considering the current app stable

All must hold simultaneously:

1. `git status` clean on `main`; no orphaned in-flight work.
2. `make lint`, `make test`, `make test-fixtures`, `make test-policy` pass locally; CI green on `main`.
3. `cd apps/web && pnpm typecheck && pnpm lint:strict && pnpm test && pnpm build && pnpm check:motion && pnpm check:bundles` all pass.
4. `pnpm test:e2e` passes, including axe checks on marketing **and** core app routes.
5. Golden path completes against fixtures (`bash scripts/staging-golden-path.sh` on staging, fixture pipeline locally) with zero manual intervention except the designed human checkpoints.
6. Signup → verification email received → verified login works in production (or email is explicitly feature-flagged off with honest UI copy).
7. `bash scripts/railway-smoke.sh` passes against production.
8. No production screen shows dev-only copy; consent UX no longer overlaps content (re-capture screenshots via `apps/web/scripts/capture-screenshots.mjs` to verify).
9. Every item in `docs/runbooks/launch-checklist.md` is checked or explicitly waived with a reason.
