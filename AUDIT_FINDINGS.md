# Production Readiness Audit Findings

**Repository:** HiNala/jober  
**Audit date:** 2026-06-22  
**Auditor role:** Senior production-readiness auditor (5-pass + cross-validation)  
**Scope:** Full repo — `apps/api`, `apps/web`, `apps/worker`, infra, CI, packages  

**Commands run during audit:**

| Command | Result |
|---------|--------|
| `git fetch --all --prune` | Clean; only `origin/main` |
| `rg` (TODO/FIXME/stub/mock/placeholder patterns) | No app-code TODO/FIXME; actionable hits in billing, OAuth, notifications, legal |
| `apps/api` — `ruff check src tests` | **Pass** |
| `apps/api` — `mypy src` | **Pass** (227 files) |
| `apps/worker` — `ruff check src tests` | **Pass** |
| `apps/worker` — `mypy src` | **Pass** (25 files) |
| `apps/web` — `pnpm typecheck` | **Pass** |
| `apps/web` — `pnpm lint:strict` | **Fail** — `use-media-query.ts:14` (`react-hooks/set-state-in-effect`) |
| Full-stack pytest / e2e | **Not run** (requires Docker + DB; documented as manual verification) |

---

## Pass 1 — Product Completeness and Stub Audit

### Finding: Web middleware protects only a subset of authenticated app routes

- Severity: Critical
- Confidence: High
- Category: Auth / route protection
- Files/Locations:
  - `apps/web/src/middleware.ts:8`
  - `apps/web/src/middleware.ts:33-35`
- Evidence:
  - `PROTECTED_PREFIXES` lists `/dashboard`, `/queue`, `/documents`, `/vault`, `/settings`, `/runs` only.
  - `/discover`, `/library`, `/search`, `/analytics`, and `/admin/*` are not matched; unauthenticated users can load full workspace chrome (API calls still 401).
- Why it matters:
  - Defense-in-depth failure; admin UI renders before API RBAC; exposes client bundles and layout to unauthenticated visitors.
- Recommended fix:
  - Extend `PROTECTED_PREFIXES` and `config.matcher` to all `(app)` routes, or invert to “protect everything except marketing/auth”.
- Validation:
  - Log out → visit `/discover`, `/library`, `/analytics`, `/admin` → redirect to `/login?next=…`.
- Status:
  - Open

---

### Finding: API auth falls back to header-based dev identity when mode is misconfigured

- Severity: Critical
- Confidence: High
- Category: Fake auth / misconfiguration
- Files/Locations:
  - `apps/api/src/jober_api/auth/deps.py:39-45`
- Evidence:
  - After checking `native` and configured `clerk`, `get_auth_context` calls `_auth_from_dev_headers`, which trusts `X-Jober-Tenant-Id` / `X-Jober-User-Id` (`deps.py:70-94`).
  - Production boot blocks `AUTH_MODE=dev` and `DEV_AUTH_BYPASS` but not this fallback when `AUTH_MODE=clerk` without issuer.
- Why it matters:
  - Misconfigured production deploy could authenticate arbitrary users via headers.
- Recommended fix:
  - Fail closed in production unless `auth_mode` is explicitly `native` or fully configured `clerk`; never default to header auth outside dev/test.
- Validation:
  - `JOBER_ENV=production`, `AUTH_MODE=clerk`, empty `CLERK_JWT_ISSUER` → API refuses boot or rejects all requests.
- Status:
  - Open

---

### Finding: Stripe webhook accepts unsigned payloads when secret is unset

- Severity: Critical
- Confidence: High
- Category: Billing / stub security path
- Files/Locations:
  - `apps/api/src/jober_api/routers/webhooks.py:24-33`
- Evidence:
  - When `settings.stripe_webhook_secret` is falsy, handler parses raw JSON without signature verification, then calls `apply_stripe_event`.
- Why it matters:
  - Attackers can forge subscription events and upgrade tenants to Pro without payment.
- Recommended fix:
  - Require `STRIPE_WEBHOOK_SECRET` in production startup; reject unsigned payloads always outside explicit test mode.
- Validation:
  - POST unsigned payload to `/api/webhooks/stripe` in prod-like env → 400/503, tenant plan unchanged.
- Status:
  - Open

---

### Finding: Pro billing / Stripe Checkout not wired end-to-end

- Severity: High
- Confidence: High
- Category: Billing / product completeness
- Files/Locations:
  - `apps/web/src/lib/marketing/plans.ts:43` — `priceLabel: "Coming soon"`
  - `apps/web/src/app/pricing/page.tsx:48` — `"Stripe checkout opens soon"`
  - `apps/web/src/components/marketing/pricing-plans.tsx:48-60` — Pro card uses waitlist, not checkout
  - `apps/web/src/components/workspace/workspace-nav.tsx:108-117` — “Upgrade to Pro” links to `/settings`
- Evidence:
  - No checkout-session creation endpoint in API or web client (grep for checkout session creation: 0 hits).
  - Webhook handler and entitlements exist; only waitlist capture is user-facing.
- Why it matters:
  - Users cannot self-serve upgrade; monetization path is incomplete despite Pro messaging.
- Recommended fix:
  - Add authenticated Stripe Checkout Session API + CTAs on Pricing and Settings; gate Pro entitlements on successful checkout.
- Validation:
  - Free user completes Stripe test checkout → Settings shows `plan: pro` and raised limits.
- Status:
  - Open

---

### Finding: Google sign-in disabled in default web build despite backend support

- Severity: High
- Confidence: High
- Category: Auth / UX stub
- Files/Locations:
  - `apps/web/src/components/auth/google-sign-in-block.tsx:25-37`
  - `apps/web/src/lib/auth/google-oauth.ts:1-4`
  - `apps/web/.env.example:7-8` — `NEXT_PUBLIC_GOOGLE_OAUTH_ENABLED=false`
- Evidence:
  - When OAuth flag is false, button is `pointer-events-none opacity-50` with tooltip “Google sign-in coming soon”.
  - Backend Google OAuth routes exist under `/api/auth/google/*`.
- Why it matters:
  - Users see a sign-in option that cannot work; implies incomplete auth story at launch.
- Recommended fix:
  - Enable flag when API credentials are configured; hide block entirely when OAuth unavailable (no fake disabled button).
- Validation:
  - Set `NEXT_PUBLIC_GOOGLE_OAUTH_ENABLED=true` + API Google creds → OAuth flow completes.
- Status:
  - Open

---

### Finding: Notification preference toggles persist but have no delivery implementation

- Severity: High
- Confidence: High
- Category: Settings / stub behavior
- Files/Locations:
  - `apps/web/src/components/settings/notifications-settings-section.tsx:15-50`
  - `apps/api/src/jober_api/services/preferences/defaults.py` (defaults only)
- Evidence:
  - Preferences `in_app_run_attention`, `in_app_batch_complete`, `email_batch_complete` are saved via `updatePreferences`.
  - Repo-wide grep: no worker, email, or in-app dispatch reads these keys outside settings UI and defaults.
- Why it matters:
  - Users believe they configured notifications; toggles have no effect — misleading product completeness.
- Recommended fix:
  - Wire preferences into batch/run completion handlers, or hide toggles until implemented with honest copy.
- Validation:
  - Enable “Email when batch finishes” → complete batch → email sent (or UI shows “not yet available”).
- Status:
  - Open

---

### Finding: Legal pages ship with explicit draft banner

- Severity: High
- Confidence: High
- Category: Legal / compliance
- Files/Locations:
  - `apps/web/src/components/marketing/legal-draft-banner.tsx:15-20`
  - `apps/web/src/app/privacy/page.tsx:21-22`
  - `apps/web/src/app/terms/page.tsx`, `apps/web/src/app/acceptable-use/page.tsx`
- Evidence:
  - Banner: “Draft — requires legal review before public launch.”
  - Privacy page: “Last updated: June 2026 (draft).”
- Why it matters:
  - Public legal pages linked from marketing footer are not counsel-approved for launch.
- Recommended fix:
  - Legal review, finalize copy and dates, remove draft banner before public launch.
- Validation:
  - `/privacy`, `/terms`, `/acceptable-use` show no draft banner; counsel sign-off recorded.
- Status:
  - Open

---

### Finding: Web dev auth bypass bakes fake Pro user into client at build time

- Severity: High
- Confidence: High
- Category: Fake auth / build-time config
- Files/Locations:
  - `apps/web/src/contexts/auth-context.tsx:86-97`
  - `apps/web/src/lib/api/client.ts:16-27`
  - `apps/web/src/middleware.ts:4-12`
- Evidence:
  - When `NEXT_PUBLIC_DEV_AUTH_BYPASS=true` or `NEXT_PUBLIC_AUTH_MODE=dev`, middleware skips session check and auth context returns fake user with `plan: "pro"`.
  - Client sends `X-Jober-Tenant-Id` / `X-Jober-User-Id` headers.
- Why it matters:
  - Accidental production web build with bypass flags breaks auth UX and security posture independently of API `DEV_AUTH_BYPASS` guard.
- Recommended fix:
  - CI/deploy gate: fail build if bypass flags set with `JOBER_ENV=production`; document in launch checklist.
- Validation:
  - Production web artifact must not contain bypass env values; unauthenticated `/dashboard` redirects to login.
- Status:
  - Open

---

### Finding: Search job results link to queue root, not specific job

- Severity: Medium
- Confidence: High
- Category: Disconnected UI behavior
- Files/Locations:
  - `apps/web/src/app/(app)/search/page.tsx:64-68`
- Evidence:
  - Job hits use `<Link href="/queue">` without `job.id`; run hits correctly use `/runs/${run.id}`.
- Why it matters:
  - Search appears functional but cannot deep-link to job detail drawer.
- Recommended fix:
  - Link to `/queue?job=${job.id}` (queue page supports `openJobId` query param).
- Validation:
  - Search known job → click result → job drawer opens on queue page.
- Status:
  - Open

---

### Finding: `/kitchen-sink` dev component page is publicly reachable

- Severity: Medium
- Confidence: High
- Category: Dev surface / sample data
- Files/Locations:
  - `apps/web/src/app/kitchen-sink/page.tsx:16-35,43-46`
- Evidence:
  - Page uses hardcoded `SAMPLE_EVENTS` and live `MetricCards`; comment says “Dev-only” but route is not auth-gated.
  - Excluded from sitemap/robots only.
- Why it matters:
  - Exposes internal component reference and may hit real API when session/bypass present.
- Recommended fix:
  - Guard with dev env, 404 in production builds, or require auth.
- Validation:
  - Production URL `/kitchen-sink` → 404 or redirect.
- Status:
  - Open

---

### Finding: Resume embedding gateway returns synthetic ID without calling provider

- Severity: Medium
- Confidence: High
- Category: Backend stub
- Files/Locations:
  - `apps/api/src/jober_api/services/embedding_gateway.py:8-13`
- Evidence:
  - Docstring: “LLM gateway stub”; returns `f"resume-embed:{resume_asset_id}"` without embedding API call.
- Why it matters:
  - Semantic keyword matching may be incomplete if downstream assumes real vectors.
- Recommended fix:
  - Integrate embedding provider or disable feature until ready.
- Validation:
  - Upload resume → embedding stored via provider, not synthetic string only.
- Status:
  - Open

---

### Finding: Template LLM provider used when no API key configured

- Severity: Medium
- Confidence: High
- Category: Production fallback / sample output
- Files/Locations:
  - `apps/api/src/jober_api/services/llm/gateway.py:232-236`
  - `apps/web/src/components/documents/llm-provider-banner.tsx:29-31`
- Evidence:
  - `get_llm_provider` returns `TemplateLlmProvider()` when `llm_provider == "template"` or no key.
  - UI banner mitigates but generation still produces template letters.
- Why it matters:
  - Production without keys ships deterministic template content users may treat as AI-generated.
- Recommended fix:
  - Block generation in production without platform or BYOK key, or enforce key in startup checks.
- Validation:
  - Production without `LLM_API_KEY` → generation blocked or explicit error, not silent templates.
- Status:
  - Open

---

### Finding: Email delivery optional — verification/reset emails may never arrive

- Severity: Medium
- Confidence: High
- Category: Auth completeness
- Files/Locations:
  - `apps/api/src/jober_api/privacy/secrets_check.py:43-46`
  - `apps/web/src/lib/auth/copy.ts:46-48`
  - `apps/web/src/app/(auth)/verify-pending/page.tsx`
- Evidence:
  - Startup logs warning when `EMAIL_BACKEND` is not inbox-capable; does not block boot.
  - UI copy honestly states verification unavailable when email disabled.
- Why it matters:
  - Production without SMTP breaks signup verification and password reset trust path.
- Recommended fix:
  - Treat inbox delivery as launch gate in production `secrets_check`, or enforce alternate verification.
- Validation:
  - `GET /api/auth/email-delivery` → `inbox_delivery: true` in prod; signup receives verification email.
- Status:
  - Open

---

### Finding: Vault fully implemented but absent from primary navigation

- Severity: Low
- Confidence: High
- Category: UX / discoverability
- Files/Locations:
  - `apps/web/src/components/app-shell/nav-links.tsx:29-46`
  - `apps/web/src/app/(app)/vault/page.tsx`
- Evidence:
  - `APP_NAV` lists Dashboard, Queue, Discover, Library, Search, Analytics, Settings — no Vault entry.
  - Vault reachable via `/vault`, onboarding, and Settings duplicate.
- Why it matters:
  - Core feature may be missed by users after onboarding.
- Recommended fix:
  - Add Vault to main nav or consolidate entry point with clear label.
- Validation:
  - New user can reach vault from nav without hunting Settings.
- Status:
  - Open

---

### Finding: TUI menu entries are stubbed “Coming soon”

- Severity: Low
- Confidence: High
- Category: Stub (non-web surface)
- Files/Locations:
  - `apps/tui/src/jober_tui/app.py:19-42`
- Evidence:
  - Most menu options print “Coming soon in a future mission.”; only fixture run works.
- Why it matters:
  - Low risk if TUI is not shipped; confusing if published as CLI product.
- Recommended fix:
  - Document TUI as experimental or remove stub menu entries.
- Validation:
  - N/A for web launch unless TUI is distributed.
- Status:
  - Open

---

### Finding: Command palette shows disabled shortcut reference rows with no action

- Severity: Low
- Confidence: High
- Category: UI with no behavior
- Files/Locations:
  - `apps/web/src/components/workspace/workspace-command-palette.tsx:112-126`
- Evidence:
  - `CommandItem disabled` rows for “Open palette” and “Toggle navigation” are labels only.
- Why it matters:
  - Minor polish gap; shortcuts work globally but palette items look interactive yet do nothing.
- Recommended fix:
  - Replace with help text or wire to same handlers as keyboard shortcuts.
- Validation:
  - ⌘K/⌘B still work; palette items optional.
- Status:
  - Open

---

### Finding: `/documents` is redirect-only alias to Library studio (intentional)

- Severity: Info
- Confidence: High
- Category: Route alias
- Files/Locations:
  - `apps/web/src/app/(app)/documents/page.tsx:3-5`
- Evidence:
  - `redirect("/library?tab=letters&view=studio")`; covered by e2e `document-studio.spec.ts`.
- Why it matters:
  - Not broken; ops/docs should know studio lives under Library tab.
- Recommended fix:
  - None required; optionally add nav alias.
- Validation:
  - `GET /documents` → redirect to library studio URL.
- Status:
  - Open (informational)

---

**Pass 1 summary:** 17 findings — 3 Critical, 5 High, 5 Medium, 3 Low, 1 Info. Core workflows (queue, discover, vault, runs, document studio) are largely wired to real APIs; blockers concentrate in auth surface, billing, legal, and honest-but-incomplete settings.

---

## Pass 2 — API, Routing, Integration, and Data Flow Audit

**Inventory:** 28 router modules registered via `apps/api/src/jober_api/routers/__init__.py`; ~135 `/api/*` routes; 22 web client modules under `apps/web/src/lib/api/`. Startup `validate_rbac_coverage()` enforces permission tags on non-public routes.

### Finding: Batch enqueue does not verify tenant ownership (IDOR)

- Severity: Critical
- Confidence: High
- Category: Tenant isolation / API
- Files/Locations:
  - `apps/api/src/jober_api/routers/batches.py:112-125`
  - `apps/api/src/jober_api/services/batch/service.py:188-195`
- Evidence:
  - `post_enqueue_batch` calls `require_auth(request)` but does not pass `auth.tenant_id` to `enqueue_batch`.
  - `enqueue_batch` uses `ApplicationBatchRepository(session).get(batch_id)` with no tenant filter.
- Why it matters:
  - Any authenticated user who knows another tenant’s batch UUID can enqueue it.
- Recommended fix:
  - Pass `tenant_id` into `enqueue_batch`; use tenant-scoped repository; 404 if batch not owned.
- Validation:
  - Cross-tenant enqueue test (tenant A session + tenant B batch id) → 404. Mirror `test_security_controls.py` resume test pattern.
- Status:
  - Open

---

### Finding: Batch skip and reorder lack tenant scoping (IDOR)

- Severity: Critical
- Confidence: High
- Category: Tenant isolation / API
- Files/Locations:
  - `apps/api/src/jober_api/routers/batches.py:176-204`
  - `apps/api/src/jober_api/services/batch/service.py:248-271`
- Evidence:
  - `post_skip_batch_item` and reorder handlers do not pass tenant id; repositories fetch by id only.
- Why it matters:
  - Cross-tenant batch manipulation possible with guessed UUIDs.
- Recommended fix:
  - Resolve items/batches via tenant-scoped joins before mutation.
- Validation:
  - Cross-tenant skip/reorder integration tests → 404.
- Status:
  - Open

---

### Finding: Per-batch pause/resume and global queue concurrency are not tenant-scoped

- Severity: High
- Confidence: High
- Category: Tenant isolation / abuse
- Files/Locations:
  - `apps/api/src/jober_api/routers/batches.py:147-158,207-212`
  - `apps/api/src/jober_api/services/batch/redis_control.py:108-113`
- Evidence:
  - `pause_batch` / `resume_batch` call Redis with `batch_id` only, no ownership check.
  - `PATCH /api/queue/concurrency` sets global Redis key for any authenticated user.
- Why it matters:
  - Tenant A can pause tenant B’s batch or change concurrency for all tenants.
- Recommended fix:
  - Verify batch belongs to caller’s tenant before Redis mutations; scope or admin-gate concurrency.
- Validation:
  - Tenant A pauses tenant B batch → 404; non-admin concurrency patch → 403.
- Status:
  - Open

---

### Finding: Multipart uploads bypass centralized API client (missing credentials/CSRF)

- Severity: High
- Confidence: High
- Category: Integration / auth
- Files/Locations:
  - `apps/web/src/lib/api/vault.ts:105-108`
  - `apps/web/src/lib/api/library.ts:121-124`
  - `apps/web/src/lib/api/jobs.ts:45-60`
- Evidence:
  - Raw `fetch(url, { method: "POST", body: form })` without `credentials: "include"`, CSRF header, or dev bypass headers.
  - `apiFetch` in `client.ts` adds these for JSON mutations.
- Why it matters:
  - Resume and spreadsheet uploads fail under native session auth in browser; dev bypass headers also skipped.
- Recommended fix:
  - Add `uploadFetch()` mirroring `apiFetch` for FormData POSTs.
- Validation:
  - Upload resume with session cookies → 200; without credentials → 401.
- Status:
  - Open

---

### Finding: Review API response schema strips nested `cover_letter` object

- Severity: High
- Confidence: High
- Category: Schema mismatch
- Files/Locations:
  - `apps/api/src/jober_api/services/verification/service.py:374-388`
  - `packages/schemas/src/jober_schemas/verification.py:37-50`
  - `apps/api/src/jober_api/routers/verification.py:107-116`
  - `apps/web/src/lib/api/verification.ts:37-47`
- Evidence:
  - Service returns nested `cover_letter` with `id`, `text`, `locked_paragraphs`, etc.
  - `ReviewPackageRead` defines only `cover_letter_preview`; FastAPI `response_model=ReviewPackageRead` drops extra fields.
  - Frontend `ReviewPackage` interface expects full `cover_letter` for review canvas editor.
- Why it matters:
  - Run review canvas may not receive full letter data despite backend having it.
- Recommended fix:
  - Extend `ReviewPackageRead` with optional `cover_letter` sub-schema matching service payload.
- Validation:
  - `GET /api/application-runs/{id}/review` includes `cover_letter.id`; review canvas renders letter text.
- Status:
  - Open

---

### Finding: Run console SSE via EventSource may omit cross-origin session cookies

- Severity: High
- Confidence: Medium
- Category: Integration / real-time
- Files/Locations:
  - `apps/web/src/hooks/useRunStream.ts:76` (EventSource usage)
  - `apps/web/src/lib/api/run-console.ts:70-73`
- Evidence:
  - `runEventsStreamUrl` targets `NEXT_PUBLIC_API_URL`; `EventSource` does not support `credentials: "include"` like fetch.
  - Split-origin deploy (web app domain ≠ API domain) is common on Railway.
- Why it matters:
  - Live run stream may 401 or fail silently when web and API are on different origins.
- Recommended fix:
  - Same-origin Next.js proxy for SSE, or fetch-based streaming with credentials.
- Validation:
  - Split-origin E2E: open run console → events stream connects with authenticated session.
- Status:
  - Open

---

### Finding: Celery batch dispatch failures swallowed after batch marked RUNNING

- Severity: Medium
- Confidence: High
- Category: Silent failure / integration
- Files/Locations:
  - `apps/api/src/jober_api/services/batch/celery_dispatch.py:12-13`
  - `apps/api/src/jober_api/services/batch/service.py:209-221`
- Evidence:
  - `dispatch_batch_tick` catches all exceptions and returns `None`.
  - Batch status set to `RUNNING` before dispatch; client may receive `orchestrator_task_id: null` with no error.
- Why it matters:
  - Batches appear running with no worker progress; hard to debug in production.
- Recommended fix:
  - Surface dispatch failure (503/422) or rollback batch status; log/metric on null task id.
- Validation:
  - Stop broker → enqueue returns error; batch not stuck RUNNING without task.
- Status:
  - Open

---

### Finding: Weak request validation on several mutating routes

- Severity: Medium
- Confidence: High
- Category: Validation
- Files/Locations:
  - `apps/api/src/jober_api/routers/batches.py:49-87,116`
  - `apps/api/src/jober_api/routers/form_discovery.py:72-84`
  - `apps/api/src/jober_api/routers/verification.py:33-34,129-130`
- Evidence:
  - Bodies typed as `dict[str, Any]` without Pydantic models; contrast with `settings.py` using `PolicyUpdate`.
- Why it matters:
  - Invalid payloads may fail late or corrupt state; OpenAPI docs incomplete.
- Recommended fix:
  - Add shared schemas in `@jober/schemas` for batch, verification, form-discovery payloads.
- Validation:
  - Invalid enum/field → 422 with structured `detail`.
- Status:
  - Open

---

### Finding: Backend routes with no web client consumer (orphans)

- Severity: Medium
- Confidence: High
- Category: Disconnected API
- Files/Locations:
  - `apps/api/src/jober_api/routers/verification.py:29` — `verify-ready`
  - `apps/api/src/jober_api/routers/recovery.py:78,92` — run failure-report, resume
  - `apps/api/src/jober_api/routers/run_console.py:162` — browser-storage-state
  - `apps/api/src/jober_api/routers/documents.py:138` — list documents
  - `apps/api/src/jober_api/routers/auth.py:242` — change-password
  - `apps/api/src/jober_api/routers/batches.py:99-212` — batch detail, pause/resume, cancel, skip, reorder, concurrency
- Evidence:
  - Grep of `apps/web/src/lib/api` shows no wrappers for these routes; some used only in e2e helpers or worker paths.
- Why it matters:
  - Product gaps or dead API surface; maintenance burden; features exist but unreachable from UI.
- Recommended fix:
  - Wire UI for user-facing ops (change password, batch controls) or document as internal/worker-only and restrict if needed.
- Validation:
  - Product intent review; each orphan either has UI consumer or explicit internal-only doc.
- Status:
  - Open

---

### Finding: `fetchReadiness` ignores `/readyz` check details

- Severity: Low
- Confidence: High
- Category: Integration / observability
- Files/Locations:
  - `apps/web/src/lib/api/health.ts:10-18`
  - `apps/api/src/jober_api/main.py:55-78`
- Evidence:
  - Web health helper treats any `/readyz` HTTP success as `"ready"` without parsing `report.checks`.
- Why it matters:
  - Worker-health pill may show ready when Redis/MinIO degraded.
- Recommended fix:
  - Parse `status` and failed checks from readiness JSON.
- Validation:
  - Stop Redis → UI pill shows degraded with check name.
- Status:
  - Open

---

### Finding: Static / placeholder fields in verification responses

- Severity: Medium
- Confidence: High
- Category: Static data
- Files/Locations:
  - `apps/api/src/jober_api/services/verification/service.py:372`
  - `apps/api/src/jober_api/routers/auth.py:269-274` — TOTP setup disabled scaffolding
- Evidence:
  - `resume_filename` hardcoded `"resume.pdf"` regardless of active asset.
  - TOTP setup endpoint returns disabled scaffolding.
- Why it matters:
  - Review UI shows incorrect filename; 2FA appears partially implemented.
- Recommended fix:
  - Resolve real resume filename from active asset; hide TOTP until implemented.
- Validation:
  - Review package shows actual uploaded filename.
- Status:
  - Open

---

**Pass 2 summary:** 11 findings — 2 Critical, 4 High, 4 Medium, 1 Low. Router registration complete; highest risk is tenant isolation gaps on batch ops and upload/SSE integration under native auth.

---

## Pass 3 — Security, Auth, Permissions, Privacy, and Abuse Audit

**Reference:** `docs/architecture/threat-model.md`, `apps/api/src/jober_api/privacy/secrets_check.py`

### Finding: Server-side SSRF via discovery and job extraction URL fetches

- Severity: High
- Confidence: High
- Category: SSRF / abuse
- Files/Locations:
  - `apps/api/src/jober_api/services/discovery/board_parser.py:61-67`
  - `apps/api/src/jober_api/services/discovery/service.py:216-217`
  - `apps/api/src/jober_api/services/job_extraction/service.py:232-235`
- Evidence:
  - `fetch_board_html` uses `httpx.AsyncClient(..., follow_redirects=True).get(url)` with no scheme/host/private-IP blocklist.
  - User-supplied board URLs and job URLs fetched server-side.
- Why it matters:
  - Attackers can probe internal services (metadata endpoints, private Redis/MinIO networks).
- Recommended fix:
  - Shared `validate_outbound_url()`: HTTPS-only in prod, block private/link-local IPs after DNS, cap redirects and response size.
- Validation:
  - Reject `http://127.0.0.1`, `http://169.254.169.254` → 422; allow public ATS HTTPS URLs.
- Status:
  - Open

---

### Finding: API file uploads have no server-side size limits

- Severity: Medium
- Confidence: High
- Category: File upload / DoS
- Files/Locations:
  - `apps/api/src/jober_api/routers/resumes.py:49-51`
  - `apps/api/src/jober_api/routers/imports.py:24-29`
  - `apps/web/src/lib/forms/file-limits.ts:7-8`
- Evidence:
  - API reads entire upload with `await file.read()`; limits exist only in web client (10 MB / 20 MB).
- Why it matters:
  - Bypassable DoS via large uploads; memory pressure on API workers.
- Recommended fix:
  - Enforce size caps in API before read; return 413 on exceed.
- Validation:
  - Upload > limit → 413; valid size → 200.
- Status:
  - Open

---

### Finding: Content Security Policy is report-only with permissive script-src

- Severity: Medium
- Confidence: High
- Category: XSS
- Files/Locations:
  - `apps/web/next.config.ts:3-14,30-31`
- Evidence:
  - Header is `Content-Security-Policy-Report-Only` with `'unsafe-inline'` and `'unsafe-eval'` in `script-src`.
- Why it matters:
  - CSP does not block XSS; only reports violations.
- Recommended fix:
  - Switch to enforcing CSP after report burn-in; tighten `script-src` with nonces/hashes.
- Validation:
  - Enforcing CSP header present; XSS probe blocked.
- Status:
  - Open

---

### Finding: Auth rate limiting trusts client-supplied X-Forwarded-For

- Severity: Medium
- Confidence: High
- Category: Rate limiting / abuse
- Files/Locations:
  - `apps/api/src/jober_api/routers/auth.py:52-57`
  - `apps/api/src/jober_api/auth/rate_limit.py:11-18`
- Evidence:
  - `_client_ip()` prefers first `X-Forwarded-For` hop without trusted-proxy validation.
- Why it matters:
  - Attackers can rotate spoofed IPs to evade login/signup/reset rate limits.
- Recommended fix:
  - Honor forwarded headers only from known proxy peers; else use `request.client.host`.
- Validation:
  - Spoofed `X-Forwarded-For` from untrusted client ignored.
- Status:
  - Open

---

### Finding: No global authenticated API rate limiting on expensive routes

- Severity: Medium
- Confidence: High
- Category: Abuse / cost
- Files/Locations:
  - `apps/api/src/jober_api/routers/auth.py:61-67` (auth only)
  - `apps/api/src/jober_api/routers/waitlist.py:14-16` (waitlist only)
- Evidence:
  - No middleware-level limiter in `main.py`; LLM generation, discovery fetch, batch enqueue unthrottled per user.
- Why it matters:
  - Cost abuse and DoS on expensive endpoints.
- Recommended fix:
  - Redis-backed per-tenant limits on high-cost routes; global authenticated middleware default.
- Validation:
  - Burst over limit → 429 on target routes.
- Status:
  - Open

---

### Finding: Public analytics collector has no rate limit

- Severity: Medium
- Confidence: High
- Category: Abuse / privacy
- Files/Locations:
  - `apps/api/src/jober_api/auth/deps.py:17-18`
  - `apps/api/src/jober_api/routers/analytics.py:24-33`
- Evidence:
  - `POST /api/events` is public, CSRF-exempt; consent gating drops events without consent cookie but no IP rate limit.
- Why it matters:
  - DB-fill abuse even with consent cookie manipulation attempts.
- Recommended fix:
  - IP-based rate limit; cap batch size server-side.
- Validation:
  - Flood returns 429 or drops after threshold.
- Status:
  - Open

---

### Finding: Clerk JWT audience verification disabled

- Severity: Medium
- Confidence: High
- Category: Auth (Clerk mode only)
- Files/Locations:
  - `apps/api/src/jober_api/auth/deps.py:103-109`
- Evidence:
  - `jwt.decode(..., options={"verify_aud": False})`.
- Why it matters:
  - If `AUTH_MODE=clerk`, tokens intended for other audiences may be accepted.
- Recommended fix:
  - Configure expected `aud` from env; enable verification.
- Validation:
  - Token with wrong `aud` → 401.
- Status:
  - Open

---

### Finding: CSRF-exempt session refresh with cross-site cookies

- Severity: Low
- Confidence: Medium
- Category: CSRF
- Files/Locations:
  - `apps/api/src/jober_api/auth/deps.py:28`
  - `apps/api/src/jober_api/routers/auth.py:158-169`
- Evidence:
  - `/api/auth/refresh` in `PUBLIC_API_PREFIXES`; with `SameSite=None` cookies, cross-site refresh POST possible.
- Why it matters:
  - Limited impact (rotation only) but unnecessary exposure.
- Recommended fix:
  - Require CSRF or custom header for refresh.
- Validation:
  - Cross-site refresh without CSRF → 403.
- Status:
  - Open

---

### Finding: Session absolute TTL only — no idle timeout

- Severity: Low
- Confidence: High
- Category: Session handling
- Files/Locations:
  - `apps/api/src/jober_api/config.py:66`
  - `apps/api/src/jober_api/auth/sessions.py:54`
  - `docs/architecture/threat-model.md:90`
- Evidence:
  - Default `session_ttl_seconds: 86400`; Redis TTL only; threat model notes stolen-session residual risk.
- Why it matters:
  - Stolen session valid until expiry.
- Recommended fix:
  - Optional idle timeout or shorter production TTL.
- Validation:
  - Inactivity window invalidates session.
- Status:
  - Open

---

### Finding: Dev-only auth tokens exposed in response headers

- Severity: Low
- Confidence: High
- Category: Secrets / logging
- Files/Locations:
  - `apps/api/src/jober_api/routers/auth.py:97-98,199-200`
- Evidence:
  - Register/forgot-password set `X-Jober-Verify-Token` / `X-Jober-Reset-Token` in development.
- Why it matters:
  - Safe in dev; must never appear in production responses.
- Recommended fix:
  - Production smoke test asserting headers absent.
- Validation:
  - Prod forgot-password response has no reset token header.
- Status:
  - Open

---

### Finding: Root `.env.example` missing production security variables

- Severity: Low
- Confidence: High
- Category: Configuration / secrets
- Files/Locations:
  - `.env.example:22-25`
  - `infra/railway/variables.example.env:9-10`
- Evidence:
  - Root example omits `COOKIE_SECURE`, `DEV_AUTH_BYPASS`, `STRIPE_WEBHOOK_SECRET`, `CORS_ORIGINS`; Railway template documents some.
- Why it matters:
  - Operators may deploy with insecure defaults from incomplete docs.
- Recommended fix:
  - Add commented production security vars to all env templates.
- Validation:
  - Launch checklist cross-checks examples vs `config.py` fields.
- Status:
  - Open

---

**Pass 3 controls verified (no finding):** Production boot guards (`secrets_check.py`), RBAC default-deny + startup coverage, CSRF double-submit (`test_csrf_coverage.py`), cookie HttpOnly/Secure flags, tenant isolation tests (`test_tenant_isolation.py`), log redaction, presigned URL TTL, analytics consent opt-in, Stripe signature when secret configured.

**Pass 3 summary:** 11 findings — 1 High, 7 Medium, 3 Low. Strong baseline; SSRF and upload limits are top gaps beyond Pass 1–2 auth/billing issues.

---

## Pass 4 — Production Reliability, Observability, Performance, and Deployment Audit

### Finding: Batch orchestrator can double-dispatch the same PENDING item

- Severity: High
- Confidence: High
- Category: Concurrency / idempotency
- Files/Locations:
  - `apps/worker/src/jober_worker/batch_orchestrator.py:49-73`
  - `apps/worker/src/jober_worker/batch_runner.py:149-163`
  - `apps/worker/src/jober_worker/celery_app.py:26-29`
- Evidence:
  - Orchestrator selects PENDING item and enqueues `execute_batch_item.delay` without atomic claim.
  - Worker sets `RUNNING` only after task starts; beat tick every `batch_tick_seconds` (default 5s).
  - Race: two ticks can enqueue two tasks before either commits RUNNING.
- Why it matters:
  - Duplicate application runs for same batch item in production.
- Recommended fix:
  - Atomic claim: `UPDATE ... WHERE status=PENDING RETURNING` or Redis claim key before dispatch.
- Validation:
  - Simulate concurrent ticks → only one run created per item.
- Status:
  - Open

---

### Finding: N+1 queries in batch preview / create path

- Severity: High
- Confidence: High
- Category: Performance
- Files/Locations:
  - `apps/api/src/jober_api/services/batch/service.py:85-90,106-107,145`
- Evidence:
  - `_skip_reason` calls `ApplicationRunRepository.list_for_job(job.id)` per eligible job (up to 500).
  - `create_batch` always calls `preview_batch` first.
- Why it matters:
  - Batch creation latency scales linearly with queue size; can timeout under load.
- Recommended fix:
  - Bulk-load prior successful runs in one query grouped by `job_target_id`.
- Validation:
  - Preview 500 jobs → single-digit query count (profiler or SQL log assertion).
- Status:
  - Open

---

### Finding: Railway and Docker API health probes use `/healthz` not `/readyz`

- Severity: Medium
- Confidence: High
- Category: Deployment / health checks
- Files/Locations:
  - `infra/railway/api.railway.toml:15-16`
  - `infra/docker/Dockerfile.api:45-46`
  - `apps/api/src/jober_api/main.py:49-78`
- Evidence:
  - Probes hit `/healthz` which always returns OK; `/readyz` checks Postgres/Redis/MinIO and returns 503 on failure.
- Why it matters:
  - Traffic routed to API instances whose dependencies are down.
- Recommended fix:
  - Point deploy probes at `/readyz` or add pre-traffic readiness gate.
- Validation:
  - Stop Postgres → probe fails → instance removed from rotation.
- Status:
  - Open

---

### Finding: No Prometheus/OpenTelemetry metrics endpoint

- Severity: Medium
- Confidence: High
- Category: Observability
- Files/Locations:
  - `apps/api/src/jober_api/` (no `/metrics` exporter found)
- Evidence:
  - Observability is log- and admin-dashboard-centric; no standard metrics scrape target.
- Why it matters:
  - Hard to alert on error rates, queue depth, LLM spend without log parsing.
- Recommended fix:
  - Add `/metrics` or OpenTelemetry exporter for critical counters (runs, failures, LLM calls).
- Validation:
  - Prometheus scrape succeeds; dashboards show run failure rate.
- Status:
  - Open

---

### Finding: `/readyz` creates and disposes DB engine on every request

- Severity: Medium
- Confidence: High
- Category: Performance / reliability
- Files/Locations:
  - `apps/api/src/jober_api/health.py:41-60`
- Evidence:
  - `readiness_report` calls `create_async_engine` + `dispose()` per probe.
- Why it matters:
  - Connection churn under frequent Railway/uptime/admin polling.
- Recommended fix:
  - Reuse shared pool or rate-limit probe cost.
- Validation:
  - Probe load test → stable connection count.
- Status:
  - Open

---

### Finding: Environment variable documentation gaps vs `config.py`

- Severity: Medium
- Confidence: High
- Category: Configuration
- Files/Locations:
  - `apps/api/src/jober_api/config.py:16-101`
  - `.env.example`, `infra/railway/variables.example.env`
- Evidence:
  - Undocumented in templates: `DATABASE_POOL_SIZE`, `CLERK_*`, `STRIPE_*`, `ANALYTICS_*`, session tuning, `LLM_EMBEDDING_MODEL`, `BROWSERLESS_URL` (API side).
  - `.env.example` duplicates `POSTGRES_HOST_PORT` with conflicting defaults (lines ~44 and ~90).
- Why it matters:
  - Misconfiguration in production deploys; pool exhaustion or missing Stripe keys undetected until runtime.
- Recommended fix:
  - Sync all `config.py` fields to env templates with comments.
- Validation:
  - Script or checklist diff `config.py` fields vs `.env.example`.
- Status:
  - Open

---

### Finding: Batch detail serialization returns all items without pagination cap

- Severity: Medium
- Confidence: High
- Category: Unbounded query / payload
- Files/Locations:
  - `apps/api/src/jober_api/services/batch/service.py:332-359`
  - `apps/api/src/jober_api/repositories/application_batch.py:55-62`
- Evidence:
  - `list_for_batch` has no LIMIT; `serialize_batch` returns full items array.
- Why it matters:
  - Large batches produce huge JSON payloads and slow UI.
- Recommended fix:
  - Paginate batch items or cap with cursor for detail endpoint.
- Validation:
  - Batch with 1000 items → response paginated or under size budget.
- Status:
  - Open

---

### Finding: Celery worker tasks lack explicit idempotency and ack settings

- Severity: Medium
- Confidence: High
- Category: Worker reliability
- Files/Locations:
  - `apps/worker/src/jober_worker/tasks.py:16-32`
  - `apps/worker/src/jober_worker/celery_app.py:18-43`
- Evidence:
  - `extract_job` / `fill_form` have no dedup key or entry guard; no `task_acks_late`, `task_reject_on_worker_lost` in config.
  - `send_transactional_email` retries up to 3 without idempotency key.
- Why it matters:
  - At-least-once delivery can duplicate browser jobs or emails.
- Recommended fix:
  - Add ack/retry policy; idempotency keys on email and browser tasks.
- Validation:
  - Worker kill mid-task → no duplicate side effects on retry.
- Status:
  - Open

---

### Finding: Web strict lint fails — blocks CI web job

- Severity: Medium
- Confidence: High
- Category: CI / build
- Files/Locations:
  - `apps/web/src/hooks/use-media-query.ts:14`
- Evidence:
  - `pnpm lint:strict` error: `react-hooks/set-state-in-effect` on `setMatches(media.matches)` in effect.
- Why it matters:
  - CI web lint gate fails; blocks merge/deploy pipeline.
- Recommended fix:
  - Refactor hook to avoid synchronous setState in effect body (e.g. subscribe-only pattern).
- Validation:
  - `pnpm lint:strict` passes in CI.
- Status:
  - Open

---

### Finding: pnpm version mismatch between production Docker and CI

- Severity: Low
- Confidence: High
- Category: Deployment
- Files/Locations:
  - `infra/docker/Dockerfile.web.prod:8` — `pnpm@9`
  - `.github/workflows/ci.yml:267-269` — pnpm 10
- Evidence:
  - Different lockfile resolution behavior possible between CI and prod image build.
- Why it matters:
  - “Works in CI, fails in prod” dependency drift risk.
- Recommended fix:
  - Align Dockerfile to pnpm 10.
- Validation:
  - Same lockfile install in CI and prod Docker build.
- Status:
  - Open

---

### Finding: No automated CD workflow — deploy is manual

- Severity: Low
- Confidence: High
- Category: Deployment
- Files/Locations:
  - `.github/workflows/` — only `ci.yml`, `uptime.yml`
  - `docs/runbooks/deploy.md:30-32`
- Evidence:
  - Production deploy via Railway CLI; no gated promote/rollback in CI.
- Why it matters:
  - Human error in deploy steps; slower recovery.
- Recommended fix:
  - Optional CD workflow post-CI with environment gates.
- Validation:
  - Documented manual process followed until CD exists.
- Status:
  - Open

---

### Finding: Web has no Sentry — client errors only go to analytics

- Severity: Low
- Confidence: High
- Category: Observability
- Files/Locations:
  - `apps/web/src/components/analytics/analytics-provider.tsx:40-56`
  - `apps/api/src/jober_api/privacy/logging.py:68-86` (API Sentry optional)
- Evidence:
  - No `@sentry/nextjs` or `instrumentation.ts` in web app.
- Why it matters:
  - Production client failures hard to diagnose without user reports.
- Recommended fix:
  - Add web Sentry matching API observability story.
- Validation:
  - Thrown client error appears in Sentry dashboard.
- Status:
  - Open

---

**Pass 4 positive signals:** Alembic migrate-on-boot (`infra/docker/api-entrypoint.sh`), non-root Docker users, CI migration drift check, backup/restore scripts, correlation ID → Celery headers, analytics rollup idempotency, production secret enforcement at API boot.

**Pass 4 summary:** 12 findings — 2 High, 6 Medium, 4 Low.

---

## Pass 5 — UX Edge Cases, Accessibility, Consistency, and Maintainability Audit

### Finding: Admin routes guarded only on client — no edge middleware

- Severity: Medium
- Confidence: High
- Category: Accessibility / security UX
- Files/Locations:
  - `apps/web/src/components/auth/admin-route-guard.tsx:7-19`
  - `apps/web/src/middleware.ts:8,34` (admin not in matcher)
- Evidence:
  - `AdminRouteGuard` checks `isAdmin(user)` after client hydration; middleware does not protect `/admin/*`.
- Why it matters:
  - Non-admin users briefly see admin shell; relies entirely on API RBAC for data (which is correct) but poor UX and leaks admin UI structure.
- Recommended fix:
  - Add `/admin` to middleware protected prefixes; keep client guard for role check messaging.
- Validation:
  - Non-admin without session cannot load `/admin` HTML shell.
- Status:
  - Open

---

### Finding: E2E accessibility suite does not use real session auth

- Severity: Medium
- Confidence: High
- Category: Tests / a11y coverage gap
- Files/Locations:
  - `apps/web/e2e/helpers/app-auth.ts:3-8`
  - `apps/web/e2e/a11y-app.spec.ts:7-16`
- Evidence:
  - Comments reference dev bypass tenant/user IDs; axe tests hit app routes without exercising login flow or session cookie behavior.
- Why it matters:
  - Auth-gated UI states (verify pending, 401 errors, CSRF failures) not covered by a11y suite.
- Recommended fix:
  - Add fullstack a11y spec with native auth signup/login path.
- Validation:
  - Axe clean on `/dashboard` after real login E2E.
- Status:
  - Open

---

### Finding: Dates rendered with `toLocaleString()` without explicit locale/timezone

- Severity: Medium
- Confidence: Medium
- Category: Locale / timezone
- Files/Locations:
  - `apps/web/src/components/vault/profile-vault.tsx:166`
  - `apps/web/src/components/library/library-cover-letters.tsx:103`
  - `apps/web/src/components/library/library-runs.tsx:55`
- Evidence:
  - `new Date(...).toLocaleString()` uses browser default only; no shared formatter or user timezone preference.
- Why it matters:
  - Inconsistent timestamps across users; support confusion for batch/run timing vs API UTC storage.
- Recommended fix:
  - Central `formatDateTime()` using user timezone from preferences or `Intl` with explicit options.
- Validation:
  - User in US/EU timezones sees consistent localized times matching API UTC source.
- Status:
  - Open

---

### Finding: Notification settings use raw checkboxes without design-system form patterns

- Severity: Low
- Confidence: Medium
- Category: Accessibility / consistency
- Files/Locations:
  - `apps/web/src/components/settings/notifications-settings-section.tsx:15-50`
- Evidence:
  - Plain `<input type="checkbox">` inside `<label>`; project convention (AGENTS.md) prefers `FormField` + described-by for settings forms elsewhere.
- Why it matters:
  - Inconsistent error/description wiring; harder to extend with help text and a11y descriptions.
- Recommended fix:
  - Migrate to `FormField` + switch component matching other settings sections.
- Validation:
  - Axe scan on Settings notifications section clean; screen reader announces label + description.
- Status:
  - Open

---

### Finding: Canvas artifact thumbnails use empty alt text

- Severity: Low
- Confidence: Medium
- Category: Accessibility
- Files/Locations:
  - `apps/web/src/components/canvas/canvas-filmstrip.tsx:90`
  - `apps/web/src/components/canvas/artifact-grid-view.tsx:82`
- Evidence:
  - `alt=""` on screenshot thumbnails.
- Why it matters:
  - Acceptable if purely decorative; if thumbnails convey run state, screen readers miss context.
- Recommended fix:
  - Use descriptive alt from run event message or `aria-hidden` on decorative wrapper with text alternative nearby.
- Validation:
  - Manual screen reader pass on run console filmstrip.
- Status:
  - Needs Manual Verification

---

### Finding: No root `global-error.tsx` for catastrophic layout failures

- Severity: Low
- Confidence: High
- Category: Error handling / UX
- Files/Locations:
  - `apps/web/src/app/` — 18 route-level `error.tsx` under `(app)/` but no `global-error.tsx`
- Evidence:
  - Route errors handled; root layout failures have no dedicated Next.js global boundary.
- Why it matters:
  - Rare white-screen on root layout throw without recovery UI.
- Recommended fix:
  - Add `apps/web/src/app/global-error.tsx` with minimal recovery chrome.
- Validation:
  - Force root layout error in dev → global error UI renders.
- Status:
  - Open

---

### Finding: Missing automated tests for batch enqueue tenant isolation

- Severity: Medium
- Confidence: High
- Category: Tests / critical flows
- Files/Locations:
  - `apps/api/tests/test_tenant_isolation.py`
  - `apps/api/tests/test_security_controls.py:90` (resume activate only)
- Evidence:
  - Cross-tenant tests exist for jobs, runs, library, export; no test for `POST /api/batches/{id}/enqueue` cross-tenant.
- Why it matters:
  - Critical IDOR (Pass 2) lacks regression test.
- Recommended fix:
  - Add `test_cross_tenant_batch_enqueue_blocked` mirroring existing isolation tests.
- Validation:
  - pytest passes; enqueue cross-tenant → 404.
- Status:
  - Open

---

### Finding: Full-stack E2E does not cover billing, admin ops, or split-origin SSE

- Severity: Medium
- Confidence: High
- Category: Tests / critical flows
- Files/Locations:
  - `apps/web/e2e/*.fullstack.spec.ts` (6 specs)
  - No billing or Stripe webhook E2E
- Evidence:
  - E2E covers auth, core journey, document studio, recovery, settings; gaps on monetization and live run SSE under production-like origins.
- Why it matters:
  - Highest-risk flows identified in Pass 1–2 lack end-to-end regression.
- Recommended fix:
  - Add targeted E2E for settings usage limits, run console SSE (split-origin config), admin smoke.
- Validation:
  - CI fullstack job includes new specs green.
- Status:
  - Open

---

### Finding: Duplicate document client response typing

- Severity: Low
- Confidence: High
- Category: Maintainability
- Files/Locations:
  - `apps/web/src/lib/api/documents.ts`
  - `apps/web/src/lib/api/library.ts:100`
- Evidence:
  - Duplicate letter operations expect different response shapes (`GeneratedDocumentRead` vs `{ id }`) for similar endpoints.
- Why it matters:
  - Future API changes may fix one client and break the other.
- Recommended fix:
  - Consolidate document API types in shared module.
- Validation:
  - Single type source used by library and studio components.
- Status:
  - Open

---

### Finding: Empty first-run experience without demo/sample workspace

- Severity: Medium
- Confidence: High
- Category: UX / empty states
- Files/Locations:
  - `docs/screenshots/UI-REVIEW.md:329-331,380-385`
  - `apps/web/src/components/dashboard/dashboard-first-run.tsx`
- Evidence:
  - UI review documents empty charts and queue without sample data toggle; no `?demo=1` workspace mode implemented.
- Why it matters:
  - New production users land on empty dashboard/analytics; evaluators cannot see product value without manual setup.
- Recommended fix:
  - Optional demo workspace or guided import flow (documented as polish-pack follow-up).
- Validation:
  - New user sees actionable empty states with primary CTA to import or explore demo.
- Status:
  - Open

---

### Finding: Positive a11y investment — axe suites and keyboard tests exist

- Severity: Info
- Confidence: High
- Category: Accessibility (strength)
- Files/Locations:
  - `apps/web/e2e/a11y-app.spec.ts`, `a11y-auth.spec.ts`, `a11y-marketing.spec.ts`
  - `apps/web/src/components/workspace/workspace-nav.tsx:46,61-62` (aria labels, shortcuts)
- Evidence:
  - Zero axe violations asserted on major app/marketing routes; command palette keyboard open/close tested.
- Why it matters:
  - Strong foundation; gaps are coverage breadth not total absence of a11y work.
- Recommended fix:
  - Extend coverage per findings above.
- Validation:
  - CI a11y job green on all targeted routes.
- Status:
  - Open (informational — strength)

---

**Pass 5 summary:** 10 findings — 0 Critical, 5 Medium, 4 Low, 1 Info (strength). UX patterns largely consistent (`page-states.tsx`, design tokens); gaps in admin auth UX, locale, test coverage for critical security paths, and first-run onboarding.

---

## Final Validation Summary

**Cross-validation performed:** 2026-06-22. Re-read all passes; merged overlapping items; downgraded/clarified weak signals.

### Highest Priority Issues

1. **Batch tenant IDOR** (enqueue, skip, reorder, pause/resume, global concurrency) — cross-tenant data mutation
2. **Stripe unsigned webhooks** when secret unset — forged plan upgrades
3. **API auth header fallback** on misconfigured `AUTH_MODE` — authentication bypass
4. **Web middleware route gaps** — unauthenticated app/admin shell exposure
5. **SSRF in discovery/job extraction** — internal network probing
6. **Multipart upload auth gap** — broken uploads under native sessions
7. **Review API strips `cover_letter`** — broken review canvas integration
8. **SSE cross-origin cookies** — live run console may fail in production topology
9. **Batch orchestrator double-dispatch** — duplicate runs
10. **Pro checkout not implemented** — monetization incomplete despite marketing

### Confirmed Critical/High Issues

| Severity | Finding | Pass |
|----------|---------|------|
| Critical | Web middleware incomplete route protection | 1, 3, 5 |
| Critical | API auth dev-header fallback on misconfiguration | 1, 3 |
| Critical | Unsigned Stripe webhooks without secret | 1, 2, 3 |
| Critical | Batch enqueue tenant IDOR | 2 |
| Critical | Batch skip/reorder tenant IDOR | 2 |
| High | Pro billing / no Stripe Checkout | 1 |
| High | Google OAuth UI disabled by default | 1 |
| High | Notification toggles non-functional | 1 |
| High | Legal pages draft state | 1 |
| High | Web dev auth bypass build-time risk | 1, 3 |
| High | Batch pause/concurrency not tenant-scoped | 2 |
| High | Upload fetch missing credentials/CSRF | 2 |
| High | Review schema drops `cover_letter` | 2 |
| High | SSE EventSource cross-origin auth | 2 |
| High | SSRF via user-supplied URLs | 3 |
| High | Batch orchestrator double-dispatch | 4 |
| High | Batch preview N+1 queries | 4 |

### Needs Manual Verification

| Item | Reason |
|------|--------|
| SSE failure in production Railway topology | Requires deployed split-origin web/API URLs |
| Canvas thumbnail `alt=""` appropriateness | Decorative vs informative intent |
| Stripe webhook behavior with real dashboard secret | Credentials required |
| Email delivery in production SMTP config | Requires live inbox |
| Full pytest + Playwright fullstack suites | Requires Docker, Postgres, Redis, MinIO |
| CSP report-only violation volume before enforcing | Requires production traffic |
| LLM provider active in production (`/api/llm/config`) | Requires deployed env |
| Railway worker beat + browserless connectivity | Requires deployed worker |

### Likely False Positives Removed or Downgraded

| Initial signal | Resolution |
|----------------|------------|
| `ListTodo` icon grep hits | Lucide icon name, not TODO marker — excluded |
| `templateStyle` / cover letter templates | Legitimate product feature — excluded |
| `FillDiffMock` / hero “demo” blocks | Labeled marketing fixtures — excluded |
| `TemplateLlmProvider` | Documented dev/CI fallback with UI banner — kept as Medium (production config), not Critical stub |
| `/documents` redirect | Intentional alias — Info only |
| `ReviewPackageRead` has `cover_letter_preview` | Partial mitigation; nested `cover_letter` still stripped — kept High |
| Empty alt on canvas thumbnails | May be intentional decorative — Needs Manual Verification |
| Clerk JWT aud issue | Downgraded relevance when deploy uses `AUTH_MODE=native` only — still Medium if Clerk ever enabled |

### Recommended Fix Order

1. **Security blockers (day 1–3):** Batch tenant scoping on all batch routes; require Stripe webhook secret in prod; fail-closed auth mode; expand web middleware; SSRF URL validator
2. **Integration blockers (day 3–5):** Upload `uploadFetch()` with credentials/CSRF; fix `ReviewPackageRead` schema; SSE proxy or fetch-stream
3. **Reliability (week 1):** Batch item atomic claim; fix N+1 preview; point health probes at `/readyz`
4. **Product honesty (week 1–2):** Hide or implement notification toggles; legal review; Google OAuth flag or remove disabled button; Pro checkout or remove upgrade CTAs
5. **CI/deploy (week 2):** Fix `use-media-query` lint; align pnpm versions; CI gate on `NEXT_PUBLIC_DEV_AUTH_BYPASS`
6. **Observability & hardening (ongoing):** Metrics endpoint, rate limits, upload size limits, enforcing CSP, web Sentry
7. **UX polish:** Search deep links, vault nav, demo workspace, date formatting

### Validation Checklist

Production-ready confirmation after fixes:

- [ ] `pytest apps/api/tests/test_security_controls.py apps/api/tests/test_tenant_isolation.py -q` — all green including new batch IDOR tests
- [ ] `pnpm lint:strict && pnpm typecheck && pnpm build` in `apps/web` — all green
- [ ] `ruff check && mypy src` in `apps/api` and `apps/worker` — all green
- [ ] Production env: `JOBER_ENV=production`, `AUTH_MODE=native`, `DEV_AUTH_BYPASS=false`, `COOKIE_SECURE=true`, `STRIPE_WEBHOOK_SECRET` set, `LLM_API_KEY` set — API boot succeeds
- [ ] Production env: API boot **fails** with placeholder secrets
- [ ] Logged-out requests to `/discover`, `/library`, `/admin` → redirect login
- [ ] Cross-tenant batch enqueue → 404
- [ ] Resume upload with session cookie → 200
- [ ] Run review API returns `cover_letter` when document exists
- [ ] Split-origin run console SSE connects (or proxied equivalent)
- [ ] Stripe webhook without signature → 400 in production
- [ ] SSRF probe URL blocked → 422
- [ ] Upload > size limit → 413
- [ ] `bash scripts/railway-smoke.sh` against staging/production — pass
- [ ] Playwright fullstack + a11y suites in CI — pass
- [ ] Legal pages without draft banner; counsel sign-off
- [ ] Signup receives verification email (`inbox_delivery: true`)
- [ ] No `NEXT_PUBLIC_DEV_AUTH_BYPASS` in production web build

---

**Total findings (deduplicated across passes):** 58 raw → **~45 unique issues** (+ 2 informational strengths)

| Severity | Count (unique) |
|----------|----------------|
| Critical | 5 |
| High | 16 |
| Medium | 19 |
| Low | 12 |
| Info | 2 |

**Audit artifact location:** `AUDIT_FINDINGS.md` (repository root)

---

## Pass 6 — Follow-up Delta Audit (2026-06-22)

**Purpose:** Re-verify prior Critical/High findings, scan worker/packages/CI for gaps missed in Passes 1–5, check git history for regressions or partial fixes.

**Commands run:**

| Command | Result |
|---------|--------|
| Re-read 8 prior Critical/High files at cited paths | All **still Open** (unchanged root cause) |
| `git log --oneline -10` | UI/analytics polish (`40ebc96`…`22aa6a0`); no security fixes on cited paths |
| `apps/api` — `ruff check src tests` | **Pass** |
| `apps/api` — `mypy src` | **Pass** (227 files) |
| `apps/web` — `pnpm lint:strict` | **Fail** — `use-media-query.ts:14`, `job-kanban.tsx:7` warning |
| `rg` — `dangerouslySetInnerHTML`, `eval(`, `exec(` | JsonLd (static), fill sandbox package |
| `rg` — pip-audit / npm audit / CodeQL in `.github` | **No dependency CVE scanning** beyond detect-secrets |

---

### Pass 6 Re-verification Summary (prior Critical/High)

All eight spot-checked items from Passes 1–4 remain **Open** with evidence unchanged:

| Prior finding | Status |
|---------------|--------|
| Web middleware route gaps (`middleware.ts:8,33-35`) | Open |
| API auth header fallback (`deps.py:39-45`) | Open |
| Unsigned Stripe webhooks (`webhooks.py:24-33`) | Open |
| Batch enqueue tenant IDOR (`batches.py:119-124`, `service.py:191-192`) | Open |
| Vault upload missing credentials/CSRF (`vault.ts:105-108`) | Open |
| `ReviewPackageRead` strips `cover_letter` (`verification.py:37-50`) | Open |
| Discovery SSRF (`board_parser.py:61-67`) | Open |
| Batch orchestrator double-dispatch (`batch_orchestrator.py:49-73`) | Open |

**Partial improvement (still Open):** `apps/web/src/lib/api/library.ts:121-124` now sets `credentials: "include"` on resume upload, but still omits CSRF token and dev bypass headers. `vault.ts` and `jobs.ts` unchanged.

**Resolved since Pass 1–5:** None.

---

### Finding: Worker fill context loads profile and resume without tenant scope

- Severity: Critical
- Confidence: High
- Category: Tenant isolation / worker / PII
- Files/Locations:
  - `apps/worker/src/jober_worker/fill_context.py:57-67`
  - `apps/worker/src/jober_worker/fill_context.py:104-112`
  - `apps/worker/src/jober_worker/fill_runner.py:204` (consumer)
- Evidence:
  - Profile query: `FROM user_profiles ORDER BY created_at DESC LIMIT 1` — no `tenant_id` filter.
  - Resume query: `FROM resume_assets WHERE is_active = true ORDER BY created_at DESC LIMIT 1` — no tenant filter.
  - Observations and cover letter queries correctly scope by `job_target_id`.
- Why it matters:
  - In multi-tenant production, browser form-fill can inject another tenant's name, email, sensitive answers, and resume file into live ATS submissions.
- Recommended fix:
  - Join `job_targets` on `job_target_id`; filter `user_profiles` and `resume_assets` by `job_targets.tenant_id` (and active user profile for tenant).
- Validation:
  - Two tenants with distinct profiles/resumes; fill run for tenant B job uses only tenant B PII and files.
- Status:
  - Open

---

### Finding: Worker extraction context joins resume skills without tenant scope

- Severity: High
- Confidence: High
- Category: Tenant isolation / worker
- Files/Locations:
  - `apps/worker/src/jober_worker/job_context.py:17-22`
- Evidence:
  - `LEFT JOIN resume_assets r ON r.is_active = true` with no `r.tenant_id = j.tenant_id`; `ORDER BY r.created_at DESC` picks globally newest active resume.
- Why it matters:
  - Job extraction and fit scoring may use another tenant's skills index.
- Recommended fix:
  - Join on `j.tenant_id = r.tenant_id AND r.is_active = true`.
- Validation:
  - Cross-tenant skills never appear in extraction context for a given job.
- Status:
  - Open

---

### Finding: Jobs spreadsheet import uploads still bypass session credentials and CSRF

- Severity: High
- Confidence: High
- Category: Integration / auth
- Files/Locations:
  - `apps/web/src/lib/api/jobs.ts:45-60`
- Evidence:
  - `previewJobsImport` and `commitJobsImport` use raw `fetch` without `credentials: "include"`, CSRF header, or dev bypass headers.
- Why it matters:
  - Queue XLSX import fails under native session auth in browser; inconsistent with JSON mutations via `apiFetch`.
- Recommended fix:
  - Route all multipart uploads through shared `uploadFetch()` mirroring `apiFetch`.
- Validation:
  - Import with session cookies → 200; without → 401.
- Status:
  - Open

---

### Finding: Stripe webhook handler has no event idempotency

- Severity: High
- Confidence: High
- Category: Billing / idempotency
- Files/Locations:
  - `apps/api/src/jober_api/routers/webhooks.py:17-37`
  - `apps/api/src/jober_api/services/billing/stripe_webhook.py:15-96`
- Evidence:
  - No persistence or dedup check of Stripe `event.id`. `apply_stripe_event` mutates tenant plan on every delivery; Stripe retries are at-least-once.
- Why it matters:
  - Duplicate or replayed events can cause incorrect plan state, redundant audit noise, or re-upgrade after cancellation.
- Recommended fix:
  - Store processed `event.id` with unique constraint; return 200 on replay without re-applying side effects.
- Validation:
  - Same event POST twice → plan changes once; second response indicates deduplicated.
- Status:
  - Open

---

### Finding: `tenants.stripe_customer_id` has no database index

- Severity: Medium
- Confidence: High
- Category: Performance / billing
- Files/Locations:
  - `apps/api/src/jober_api/models/tenant.py:28-29`
  - `apps/api/src/jober_api/services/billing/stripe_webhook.py:28-30`
- Evidence:
  - Column mapped without `index=True`; webhook lookup `Tenant.stripe_customer_id == customer_id` on every subscription event.
- Why it matters:
  - Full table scan on webhook bursts; slower processing increases Stripe retry pressure.
- Recommended fix:
  - Alembic migration adding index on `stripe_customer_id`.
- Validation:
  - `EXPLAIN` on webhook tenant lookup uses index scan.
- Status:
  - Open

---

### Finding: CI lacks dependency vulnerability scanning beyond detect-secrets

- Severity: Medium
- Confidence: High
- Category: CI / supply chain
- Files/Locations:
  - `.github/workflows/ci.yml:78-81`
  - No `pip-audit`, `pnpm audit`, CodeQL, or Dependabot config in repo
- Evidence:
  - CI runs `detect-secrets scan --baseline .secrets.baseline` only for secret patterns; no automated CVE gate on lockfiles.
- Why it matters:
  - Known vulnerable dependencies may ship without CI failure or automated bump PRs.
- Recommended fix:
  - Add `pip-audit` and `pnpm audit --prod` (with allowlist policy) plus Dependabot or Renovate.
- Validation:
  - Introduced CVE in lockfile fails CI or opens automated fix PR.
- Status:
  - Open

---

### Finding: Fill sandbox `exec()` has no timeout on Windows worker hosts

- Severity: Low
- Confidence: High
- Category: Worker reliability / packages
- Files/Locations:
  - `packages/fill/src/jober_fill/sandbox.py:112-116`
  - `packages/fill/src/jober_fill/sandbox.py:142-143`
- Evidence:
  - `_time_limit` no-ops when `signal.SIGALRM` absent (Windows). `run_sandboxed_snippet` calls `exec(compiled, …)`. Currently referenced from worker tests only, not production fill path.
- Why it matters:
  - Latent risk if LLM-generated snippets are sandboxed on Windows dev workers without cross-platform timeout.
- Recommended fix:
  - Threading/multiprocessing timeout before any production wiring.
- Validation:
  - Infinite-loop snippet terminates within timeout on Windows.
- Status:
  - Open

---

### Finding: JsonLd uses dangerouslySetInnerHTML with static marketing data only

- Severity: Info
- Confidence: High
- Category: XSS surface (controlled)
- Files/Locations:
  - `apps/web/src/components/marketing/json-ld.tsx:5`
- Evidence:
  - `dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}` with server-static structured data; no user-controlled props found in Pass 6 trace.
- Why it matters:
  - Safe today; pattern becomes dangerous if fed dynamic user content later.
- Recommended fix:
  - Keep data static; document constraint in component.
- Validation:
  - Grep confirms no user-controlled `JsonLd` props.
- Status:
  - Open (informational)

---

### Finding: Web strict lint still fails — CI web job blocked

- Severity: Medium
- Confidence: High
- Category: CI / build
- Files/Locations:
  - `apps/web/src/hooks/use-media-query.ts:14`
  - `apps/web/src/components/jobs/job-kanban.tsx:7`
- Evidence:
  - `pnpm lint:strict` fails on `react-hooks/set-state-in-effect` (synchronous `setMatches` in effect). Unused `QUEUE_EMPTY` warning in kanban.
  - Recent commits (`4b74a2e`, `22aa6a0`) touched related files but did not resolve lint error.
- Why it matters:
  - CI web lint gate remains red; blocks merge pipeline.
- Recommended fix:
  - Refactor hook to subscribe-only pattern; remove unused import.
- Validation:
  - `pnpm lint:strict && pnpm check:motion` passes.
- Status:
  - Open

---

## Pass 6 — Final Validation Update

### Highest Priority Issues (updated)

1. **Worker fill cross-tenant PII/resume** (`fill_context.py`) — **NEW Critical**; can submit wrong tenant data to live ATS forms
2. **Batch tenant IDOR** (enqueue, skip, reorder, pause, concurrency) — unchanged
3. **Unsigned Stripe webhooks** when secret unset — unchanged
4. **API auth header fallback** on misconfigured `AUTH_MODE` — unchanged
5. **Web middleware route gaps** — unchanged
6. **Worker extraction cross-tenant resume skills** (`job_context.py`) — **NEW High**
7. **SSRF in discovery/extraction** — unchanged
8. **Multipart upload auth gaps** (vault, jobs; library partial) — unchanged
9. **Review API strips `cover_letter`** — unchanged
10. **Stripe webhook idempotency** — **NEW High**

### Confirmed Critical/High Issues (Pass 6 cumulative)

| Severity | Count | New in Pass 6 |
|----------|-------|---------------|
| Critical | **6** | +1 (worker fill tenant leak) |
| High | **19** | +3 (job_context, jobs import, Stripe idempotency) |

All Pass 1–5 Critical/High items re-checked: **0 resolved**.

### Needs Manual Verification (added)

| Item | Reason |
|------|--------|
| Worker fill cross-tenant behavior in staging | Requires two tenants + live fill run |
| Full pytest + Playwright fullstack | Requires Docker stack |
| Stripe idempotency under replay | Requires Stripe CLI or test mode |

### Likely False Positives Removed or Downgraded (Pass 6)

| Signal | Resolution |
|--------|------------|
| `library.ts` upload “fixed” | Partial only — credentials added, CSRF still missing; finding remains Open |
| Fill sandbox `exec()` | Downgraded to Low — not on production fill path today |

### Recommended Fix Order (Pass 6 delta)

1. **Immediate:** Fix `fill_context.py` and `job_context.py` tenant scoping before any multi-tenant production traffic
2. **Same sprint as Pass 1–5 blockers:** Batch IDOR, webhook secret + idempotency, auth fallback, middleware, SSRF
3. **Integration:** Unified `uploadFetch()` for vault, library, jobs
4. **CI:** Fix `use-media-query` lint; add dependency CVE scanning

### Validation Checklist (Pass 6 additions)

- [ ] Worker fill for tenant B job uses tenant B profile and resume only (integration test)
- [ ] Extraction context skills scoped to job tenant
- [ ] Duplicate Stripe `event.id` POST → no double plan mutation
- [ ] `pnpm lint:strict` passes in CI
- [ ] `stripe_customer_id` index migration applied

---

**Total findings after Pass 6 (deduplicated):** ~**53 unique issues** (+ 3 informational)

| Severity | Count (cumulative) | Δ Pass 6 |
|----------|-------------------|----------|
| Critical | 6 | +1 |
| High | 19 | +3 |
| Medium | 21 | +2 |
| Low | 13 | +1 |
| Info | 3 | +1 |

**Pass 6 verdict:** No prior Critical/High finding was fixed. **New Critical worker tenant leak** in form-fill path is the highest-risk delta and should be addressed before multi-tenant production use.

---

## Remediation Log (2026-06-23)

Audit remediation landed on `main` (`6a46500` + follow-ups). Summary:

| Area | Status |
|------|--------|
| Critical/High (tenant isolation, auth, uploads, SSRF, Stripe idempotency, SSE proxy) | **Fixed** |
| Medium/Low (rate limits, readyz, env templates, CI audits, UX polish) | **Fixed** |
| Staging deploy | **Live** — `/readyz` green |
| Session idle timeout (`SESSION_IDLE_TIMEOUT_SECONDS`, default 1h) | **Fixed** |
| TUI stub menu | **Removed** — dev console lists working flows only |
| CSP enforcing | **Env toggle** `CSP_ENFORCE=true` on web (report-only retained) |
| Staging CD | **`.github/workflows/deploy-staging.yml`** (requires `RAILWAY_TOKEN`) |
| Production deploy | **Blocked** on `STRIPE_WEBHOOK_SECRET` (user action) |
| Stripe Checkout (P1), legal counsel (P2), notifications (P3), demo workspace (P4) | **Open** — product/legal |
| Demo workspace API + UI (P4) | **Fixed** — `POST /api/onboarding/demo-workspace` |
| In-app notifications (P3 partial) | **Fixed** — prefs + banner + batch toasts |
| Client error observability (L7) | **Fixed** — `client.error` analytics event |

Pre-deploy: run `alembic upgrade head` on production after Stripe vars are set; set `TRUST_PROXY_HEADERS=true` (done on Railway API).
