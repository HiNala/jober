# Polish Pack — Continuation Log

## Loop after Mission 01 — 2026-06-10

### Re-verification (Mission 01 acceptance criteria)

| Criterion | Result |
|-----------|--------|
| Working tree clean; in-flight work landed | **Green** — 6 logical commits on `main` |
| API/worker/web lint/type/test gates | **Green** — ruff, mypy, pytest (api 58 passed / worker 22 passed), web typecheck/lint/test/build |
| Dockerized web dev on Windows | **Green** — `docker compose --profile full up -d web`; `http://localhost:3002` → 200 |
| No dead code on `main` | **Green** — empty `announcement-banner.tsx` removed, not committed |

### Improvements made (this loop)

- `fix(auth): narrow cookie samesite type for mypy [pack-01]` — unblocks `mypy src` after SameSite=None change.
- Amended mislabeled screenshot commit message before landing minio + polish-pack commits.

### Deferrals

| Item | Owner |
|------|-------|
| `infra/railway/minio.railway.toml` deploy | Mission 30 |
| Push to `origin/main` + CI confirmation | Operator (6 commits ahead locally) |
| Full gate set (`make test-fixtures`, e2e) | Mission 02 |

### Spot check (docs)

- Verified README Quick start documents root `compose.yaml` and `docker compose --profile full up -d web`.
- Verified `docs/screenshots/UI-REVIEW.md` header links polish-pack missions 04–10 and 27–28.

### Gate summary

Mission 01 validation commands rerun green. Mission 02 canonical `gates.md` not yet written.

### Deployment decision

**Not deploying.** Mission 01 Production Guidance: dev-local and docs only; MinIO Railway change waits for Mission 30. No production contract changes in this mission.

---

## Loop after Mission 02 — 2026-06-11

### Re-verification (Mission 02 acceptance criteria)

| Criterion | Result |
|-----------|--------|
| Every gate passes locally twice | **Green** — api pytest 58 passed ×2, worker 22, policy 12, fixtures, full web stack, e2e 13 |
| CI green on `main` | **Green** — [run 27315598137](https://github.com/HiNala/jober/actions/runs/27315598137) |
| `gates.md` accurate | **Green** — created with env table, Windows notes, durations |
| No undocumented blockers | **Green** |

### Improvements made (this loop)

- Documented Windows harness notes in `gates.md`: keep infra up during gate runs; delete `apps/web/.next` after Docker web dev before typecheck.

### Deferrals

| Item | Owner |
|------|-------|
| `make doctor` on Windows (no Make) | Documented manual equivalent in `gates.md` |

### Spot check (states)

- Confirmed e2e `golden-path-smoke.spec.ts` and `a11y-marketing.spec.ts` pass in CI web job (13 tests total).

### Gate summary

Full gate set per `docs/polish-pack/notes/gates.md` — all green locally and on GitHub Actions.

### Deployment decision

**Not deploying.** Mission 02 Production Guidance: gate certification only; no production defect fix in this mission.

---

## Loop after Mission 03 — 2026-06-11

### Re-verification (Mission 03 acceptance criteria)

| Criterion | Result |
|-----------|--------|
| Every journey segment recorded | **Green** — matrix in `03_golden_path_findings.md` |
| Production smoke + signup walkthrough | **Green** — smoke PASS; register/login documented |
| LLM provider answered | **Green** — production `openai` / `gpt-4o-mini` |
| Findings mapped to missions | **Green** — GP-001…011 |
| No code beyond trivial blockers | **Green** — one test harness fix (GP-003) |

### Improvements made (this loop)

- Re-ran `test_golden_path_integration.py` after harness fix (2 passed).
- Seamed audit §7 with Mission 03 evidence.

### Deferrals

| Item | Owner |
|------|-------|
| Full manual UI golden path on prod (authenticated) | Mission 03 notes — automated + API probes sufficient for this mission |

### Spot check (chaos)

- Production register with invalid `/api/auth/signup` → 500 vs correct `/register` → 200 (GP-011).

### Gate summary

`test_golden_path_integration.py` + `test-fixtures` green locally. CI [27316536462](https://github.com/HiNala/jober/actions/runs/27316536462) **success** on push (backend + policy + web).

### Deployment decision

**Not deploying.** Mission 03 observes production only; no prod defect at severity-critical level (email gap already tracked GP-001).

---

## Loop after Mission 04 — 2026-06-11

### Re-verification (Mission 04 acceptance criteria)

| Criterion | Result |
|-----------|--------|
| No persistent toast; sheet once per device | **Green** — `ConsentSheet` via vaul; `key={pathname}` remount for undecided |
| Settings control reverses choice | **Green** — `AnalyticsConsentSection` |
| SDK gating (unset / decline / DNT) | **Green** — `consent.test.ts` + `consent-state.test.ts` |
| Screenshot overlap | **Deferred** — re-capture post-deploy (UI-REVIEW closure note added) |
| a11y + reduced-motion | **Green** — drawer uses design tokens; existing marketing axe suite |

### Improvements made (this loop)

- Fixed drawer z-index so Accept/Decline buttons are clickable (removed erroneous `z-40` on content).
- `fix(e2e): dismiss consent sheet in marketing smoke tests [pack-31 after 04]` — `e2e/helpers/consent.ts`; `a11y-marketing.spec.ts` + `golden-path-smoke.spec.ts` call `dismissAnalyticsConsent` after `goto` so fresh profiles do not block skip-link keyboard test.

### Deferrals

| Item | Owner |
|------|-------|
| Re-capture `01-home.png` / `14-dashboard.png` without consent overlap | Post-deploy (Mission 04 doc requirement) |
| Production deploy of consent UX | Batch with next deployable mission or owner approval |
| Local `migrate-check` drift | Pre-existing local DB vs model indexes; CI uses fresh Postgres |

### Spot check (a11y)

- Re-ran full e2e (15 passed): consent sheet + skip-link keyboard coexist after dismiss helper; consent spec still asserts dialog + cookie on accept.

### Gate summary

Web: typecheck, lint:strict, test (62), e2e (15) green locally. Worker: ruff, mypy, pytest 22 passed. API ruff + mypy green. CI [27318382739](https://github.com/HiNala/jober/actions/runs/27318382739) **success** on push (backend + policy + web e2e).

### Deployment decision

**Not deploying yet** — Mission 04 permits deploy when full gates + smoke pass; batching with next web deploy. Screenshot re-capture should follow deploy.

---

## Loop after Mission 05 — 2026-06-11

### Re-verification (Mission 05 acceptance criteria)

| Criterion | Result |
|-----------|--------|
| State inventory all compliant | **Green** — `05_states_inventory.md` |
| Zero dev-only copy (`make seed` grep) | **Green** — `apps/web/src` clean |
| Empty states have golden-path CTAs | **Green** — queue import, dashboard first-run, library/doc links |
| Skeleton loading + error retry | **Green** — library skeletons; `AppRouteError` on all `(app)` routes touched |
| Screenshots confirm changes | **Deferred** — PNG refresh post-deploy (UI-REVIEW row closed in prose) |

### Improvements made (this loop)

- None required — Mission 05 landed clean; gates green on first pass.

### Deferrals

| Item | Owner |
|------|-------|
| Re-capture screenshots `14–23` | Post-deploy (Missions 04 + 05) |
| Sample data toggle on empty states | Mission 05 — no public seed API |
| `runs/[id]` route-level `error.tsx` | Low priority — `RunConsole` has inline `PageError` |

### Spot check (states)

- `onboarding-copy.test.ts` asserts no `make seed` / `make up` in user-facing strings; queue empty copy names import action.
- Re-ran e2e (15 passed) — no regressions from empty-state refactors.

### Gate summary

Web: typecheck, lint:strict, test (64), check:motion, e2e (15) green locally. Worker: ruff, pytest 22 passed. CI [27319174508](https://github.com/HiNala/jober/actions/runs/27319174508) **success** (Mission 05); [27319457908](https://github.com/HiNala/jober/actions/runs/27319457908) **success** (loop log push).

### Deployment decision

**Not deploying yet** — batch Missions 04 (consent sheet) + 05 (first-run onboarding) for one web deploy; then `railway-smoke.sh` + screenshot re-capture (`01-home`, `14-dashboard`, `15-queue`).

---

## Loop after Mission 06 — 2026-06-11

### Re-verification (Mission 06 acceptance criteria)

| Criterion | Result |
|-----------|--------|
| Five auth routes share brand zone + trust strip | **Green** — `(auth)/layout.tsx`, `AuthBrandPanel`, `TrustStrip` |
| Designed error/edge states | **Green** — `AuthFormError`, `AuthEdgeState`, `AuthOAuthAlert`, `parseAuthError` |
| No false email promises | **Green** — `copy.test.ts`; `06_auth_email_copy_for_mission_11.md` for Mission 11 |
| Auth axe + keyboard | **Green** — `a11y-auth.spec.ts` (7 tests); 22 e2e total |
| Design Council ≥18/20 | **Deferred** — visual sign-off post-deploy screenshot review |
| Screenshots 11–13 | **Deferred** — UI-REVIEW rows closed in prose; PNG refresh post-deploy |

### Improvements made (this loop)

- None required — Mission 06 landed clean; CI green on first push.

### Deferrals

| Item | Owner |
|------|-------|
| Auth screenshots `11–13` + reset-password | Post-deploy |
| Design Council score on auth surfaces | Operator review after deploy |
| Consent sheet on auth routes (post-session) | Mission 04 follow-up |
| Email copy refresh when SMTP ships | Mission 11 (`06_auth_email_copy_for_mission_11.md`) |

### Spot check (docs)

- Verified Mission 11 handoff doc lists signup/forgot-password copy to update when email ships.
- `test_auth.py` + `test_auth_cookies.py` (7 passed) — no auth API contract drift from UI-only mission.

### Gate summary

Web: typecheck, lint:strict, test (69), check:motion, build, e2e (22) green locally. API auth tests (7) green. CI [27320555203](https://github.com/HiNala/jober/actions/runs/27320555203) **success** on Mission 06 push.

### Deployment decision

**Recommend deploying soon** — Missions 04–06 are visual/UX-only with full gates green; batch as one web deploy, run `railway-smoke.sh`, manually verify production login first, then re-capture screenshots (`01`, `11–15`, consent overlap check).

---

## Loop after Mission 07 — 2026-06-11

### Re-verification (Mission 07 acceptance criteria)

| Criterion | Result |
|-----------|--------|
| `/` matches §18 structure (centered hero, dominant differentiator, larger nav/type) | **Green** — `landing-page.tsx`, `hero.tsx`, `marketing-shell.tsx` |
| Hero shows product working + reduced-motion fallback | **Green** — `ProductVisual` loop; e2e `reduced motion: hero renders` |
| Zero placeholder testimonials on `/` | **Green** — `social-proof.tsx` removed; `founder-proof.tsx`; `landing-content.test.ts` |
| `check:motion` + `check:bundles` | **Green** — 2459/2800 KB |
| Marketing axe spec | **Green** — 22 e2e (marketing + auth + consent + golden-path) |
| CTA/UTM analytics wired | **Green** — `MarketingCtaLink` features on hero/footer (`cta.test.ts`) |
| Design Council ≥18/20 | **Deferred** — post-deploy visual review |
| `01-home.png` re-captured | **Deferred** — post-deploy `capture-screenshots.mjs` |

### Improvements made (this loop)

- `chore(marketing): remove orphaned value-sections [pack-31 after 07]` — dead file after Mission 07 removed `ValueSections` from landing composition.

### Deferrals

| Item | Owner |
|------|-------|
| Hero video capture vs animated terminal | Future fixture recording pipeline |
| Customer quotes | When permissioned testimonials exist |
| `01-home.png` + Design Council score | Post-deploy screenshot review |
| Consent sheet overlap with footer CTA | Re-capture after deploy (Mission 04) |

### Spot check (a11y)

- Rotated from docs (Mission 06 loop) → **marketing + auth axe** via full e2e suite: 9 marketing routes + skip-link keyboard + reduced-motion hero + 7 auth axe/keyboard tests — all green after clearing stale `:3000` listener.

### Gate summary

Infra restarted mid-loop (postgres had stopped — caused initial API connection errors). Full set green after recovery:

- migrate-check, api ruff/mypy/pytest **58 passed**, worker **22 passed**
- fixtures **23+8** passed, policy **12 passed**
- web typecheck, lint:strict, test **73**, build, check:motion, check:bundles, e2e **22** — all green locally

**Note:** e2e fails if a stale process holds `localhost:3000` with `reuseExistingServer` (non-CI). Use `CI=true pnpm test:e2e` or free the port first.

### Deployment decision

**Recommend deploying** — batch Missions 04–07 as one web deploy (consent sheet, onboarding states, auth shell, landing hero). Run `railway-smoke.sh`, verify production login + home hero, then re-capture `01-home.png` and auth screenshots (`11–13`).

---

## Loop after Mission 08 — 2026-06-11

### Re-verification (Mission 08 acceptance criteria)

| Criterion | Result |
|-----------|--------|
| UI-REVIEW rows 02–06 closed | **Green** (prose) — bento, stepper, pricing waitlist, FAQ columns, blog typography; PNG refresh **deferred** post-deploy |
| Pro waitlist replaces dead card; limits match API | **Green** — `ProWaitlistForm` → `POST /api/waitlist/pro`; `plans.test.ts` mirrors `entitlements.py` |
| Marketing axe + bundle budgets | **Green** — e2e 22 passed; 2471/2800 KB |
| Visual continuity with Mission 07 | **Green** — shared `MarketingPageHeader`, mono eyebrows, type scale |
| Design Council ≥18/20 | **Deferred** — post-deploy screenshot review |
| Waitlist docs (`08_waitlist.md`, README) | **Green** |

### Improvements made (this loop)

- None required — Mission 08 landed clean; CI green on first push.

### Deferrals

| Item | Owner |
|------|-------|
| Screenshots `02–06` + `01` | Post-deploy re-capture |
| Design Council per-page scores | Operator review after deploy |
| Blog newsletter capture | Out of scope (Mission 08) |
| Production waitlist smoke | Operator immediately after deploy |

### Spot check (chaos / contract)

- Rotated from a11y (Mission 07 loop) → **public API contract**: confirmed `/api/waitlist/` in `PUBLIC_API_PREFIXES` (middleware + RBAC enforcement); migration `q9r0s1t32u63` applied in CI Alembic step; `test_waitlist.py` covers create, dedupe, consent-required.
- Local Docker Desktop returned 500 (engine unavailable) — backend DB gates not re-run locally; CI is authoritative this loop.

### Gate summary

**CI:** [27324654433](https://github.com/HiNala/jober/actions/runs/27324654433) **success** (backend migrate + pytest incl. waitlist, policy, web 22 e2e).

**Local (web):** typecheck, lint:strict, test 73, build, check:motion, check:bundles, e2e 22 — green. API ruff + mypy green (no DB).

**Local blocker:** Docker engine 500 — `make migrate-check` / `pytest` not rerun on host; defer to CI + next loop with healthy Docker.

### Deployment decision

**Deploy recommended** — batch Missions 04–08 as one release. **Requires migration** `q9r0s1t32u63` before/at web deploy. After deploy: submit test email on `/pricing`, confirm `pro_waitlist_entries` row, run `railway-smoke.sh`, re-capture screenshots `01–06` and auth `11–13`.

---

## Loop after Mission 09 — 2026-06-10

### Re-verification (Mission 09 acceptance criteria)

| Criterion | Result |
|-----------|--------|
| Split-pane only on `/runs/[id]`; editorial elsewhere | **Green** — `layoutModeForPath` + `layout.test.ts`; editorial shell hides canvas pane |
| Bottom bar removed; ⌘K palette with nav + page actions | **Green** — `workspace-command-bar.tsx` deleted; palette has `APP_NAV`, queue import/export, run canvas/focus |
| Keyboard shortcuts + layout prefs on ops-desk | **Green** — ⌘B nav, ⌘K/⌘/ palette, ⌘\ canvas + Shift-⌘F focus ops-desk-only; separate panel storage ids |
| UI-REVIEW rows closed (prose) | **Green** — identical split + bottom bar struck; PNG refresh **deferred** post-deploy |
| Design Council ≥18/20 | **Deferred** — post-deploy screenshot review |
| README workspace section updated | **Green** |

### Improvements made (this loop)

- `feat(web): workspace layout discipline and command palette [pack-09]` — landed Mission 09 (19 files).
- `docs(missions): mission 17 shell doc reflects palette [pack-31 after 09]` — stale command-bar checklist lines updated.

### Deferrals

| Item | Owner |
|------|-------|
| Screenshots `14–23` re-capture | Post-deploy (`capture-screenshots.mjs`) |
| Design Council in-app scores | Operator review after deploy |
| Per-page max-width/density tuning | Mission 10 (component tiering) |
| Search page as ⌘K modal | Mission 10 / future UX |
| Authenticated app axe (GP-009) | Mission 26 |

### Spot check (states)

- Rotated from chaos (Mission 08 loop) → **loading/error/empty state inventory** on `(app)` routes.
- Confirmed `PageLoading` uses `role="status"` + `aria-live="polite"`; dedicated `loading.tsx` on dashboard, queue, discover, library, analytics, settings, vault, documents, search.
- Queue retains inline `PageLoading` / `PageError` inside editorial center column (no canvas squeeze); palette `?import=1` opens import dialog without breaking error retry path.
- `onboarding-copy.test.ts` green — empty-state copy unchanged by layout refactor.

### Gate summary

**Local (web, ×2 consecutive e2e):** typecheck, lint:strict, test **75**, build, check:motion, check:bundles **2461/2800 KB**, e2e **22+22** — all green.

**Local (api/worker lint):** ruff + mypy — green (no DB).

**Local blocker:** Docker Desktop engine 500 — `make migrate-check`, `pytest`, `test-fixtures`, `test-policy` not rerun on host; defer to CI (same class as Mission 08 loop).

### Deployment decision

**Deploy recommended** — batch **Missions 04–09** as one web release. Mission 09 is the largest structural UI change; deploy only after CI green on push. **Requires migration** `q9r0s1t32u63` (Mission 08 waitlist). After deploy: manual pass all `(app)` routes at 1440px, verify ⌘K on dashboard/queue/run, run `railway-smoke.sh`, re-capture screenshots `01–06`, `11–13`, and **`14–23`**.

---

## Loop after Mission 10 — 2026-06-10

### Re-verification (Mission 10 acceptance criteria)

| Criterion | Result |
|-----------|--------|
| Three families in code + `design-tokens.md` | **Green** — `surface-variants.ts`, `Surface`, `tokens.ts` |
| Migration table complete; duplicates consolidated | **Green** — sweep doc; `SettingsSection` added; vault/import/documents aligned this loop |
| No raw hex outside token layer | **Green** — grep clean in `components/`; `no-raw-color-literal` eslint rule |
| `/kitchen-sink` reference + production-hidden | **Green** — three-family page; `robots` disallow; sitemap test |
| All gates green | **Green** — see below |

### Improvements made (this loop)

- `fix(web): workspace surface on vault import documents [pack-31 after 10]` — `profile-vault`, `import-wizard`, `document-studio` bare `Card` → `surface.workspace`.
- README — Mission 10 surface families paragraph.
- `10_component_sweep.md` — vault/import/documents rows closed.

### Deferrals

| Item | Owner |
|------|-------|
| Screenshots `01–23` re-capture | Post-deploy batch (Missions 04–10) |
| Design Council scores | Operator review after deploy |
| `Card` + `surface.workspace` double-wrap in admin/analytics | Mission 22 |
| `design-review.md` stale `surface.card` references | Mission 29 docs pass |
| Authenticated app axe (GP-009) | Mission 26 |
| Search as ⌘K modal | Future UX |

### Spot check (a11y)

- Rotated from states (Mission 09 loop) → **marketing + auth axe via full e2e** (22 specs incl. axe per marketing route, skip-link keyboard, reduced-motion hero, auth axe/keyboard).
- `SettingsSection` preserves `h2` + `aria-labelledby`; `Surface` exposes `data-surface-family` for debugging only (no axe impact).

### Gate summary

**CI:** [27326577218](https://github.com/HiNala/jober/actions/runs/27326577218) **success** (Mission 10 — api pytest, policy, web e2e).

**Local (web, ×2 consecutive e2e):** typecheck, lint:strict, test **79**, build, check:motion, check:bundles **2437/2800 KB**, e2e **22+22** — all green.

**Local (api/worker):** ruff + mypy — green (no DB).

**Local blocker:** Docker not rerun — `make migrate-check` / pytest deferred to CI (unchanged).

### Deployment decision

**Deploy recommended** — batch **Missions 04–10** as one web release after CI green. Includes Mission 08 migration `q9r0s1t32u63`. Mission 09 (layout) + Mission 10 (surfaces) are visually wide but behaviorally inert. After deploy: `railway-smoke.sh`, manual all-routes pass, re-capture all **23** screenshots.

---

## Loop after Mission 11 — 2026-06-11

### Re-verification (Mission 11 acceptance criteria)

| Criterion | Result |
|-----------|--------|
| Signup verification + password reset end-to-end in production | **Pending operator** — code landed; Railway `EMAIL_BACKEND=smtp` + creds on API **and** worker required |
| Dev/CI never attempt network email | **Green** — default `console` backend; `test_email.py` (8) with `no_db` marker |
| Resend rate-limited; tokens expire; honest UI states | **Green** — Redis resend limit, `/verify-pending` + dynamic copy via `/api/auth/email-delivery` |
| Env/docs updated; boot validation | **Green** — `.env.example`, `variables.example.env`, `11_email_decision.md`, deploy runbook |
| No tracking pixels in emails | **Green** — text-first templates only |

### Improvements made (this loop)

- `feat(api): transactional email for verify and reset flows [pack-11]` — full Mission 11 delivery.
- `tests/conftest.py` — `no_db` marker skips `seed_default_tenant` so email unit tests run without Postgres.
- `pyproject.toml` — register `no_db` pytest marker.

### Deferrals

| Item | Owner |
|------|-------|
| Production inbox verify + reset walk (GP-001/002) | Operator post-deploy — set Railway SMTP, run loops, `railway-smoke.sh` |
| API integration test for `email-delivery` + resend 429 | Mission 25 |
| Email-change confirmation | Not in scope (no token flow found) |
| Screenshots `11-signup`, `13-forgot-password`, new verify routes | Post-deploy batch |
| Full api pytest locally | CI (Docker/Postgres not running locally) |

### Spot check (states)

- Rotated from a11y (Mission 10 loop) → **auth email states**: signup redirects to `/verify-pending` when `inbox_delivery`; forgot-password subtitle switches via `fetchEmailDelivery()`; verify-pending shows unavailable path when console backend; resend 60s cooldown wired.
- Build output confirms `/verify-email` and `/verify-pending` routes present.

### Gate summary

**Local:** api ruff + mypy + `test_email` (8); web typecheck, lint:strict, test (80), build, check:motion, check:bundles (2457/2800 KB), e2e **22** — all green.

**Local blocker:** `make migrate-check` / full api pytest deferred to CI (no local Docker).

### Deployment decision

**Deploy recommended for Mission 11** — requires **API + worker** env together: `EMAIL_BACKEND=smtp`, `EMAIL_FROM`, `SMTP_*`. Web can deploy independently (honest copy already). After deploy: send real verification + reset to a test inbox, complete both loops, update GP-001/002 in golden-path findings, re-capture auth screenshots.

### Refinement pass (same day)

**Re-verification:** Mission 11 criteria unchanged — production inbox still operator-blocked; all code-path criteria green.

**Improvements:** `test(e2e): axe verify-email and verify-pending routes [pack-31 after 11]` — closes Mission 11 blast-radius gap in `a11y-auth.spec.ts` (22 → **24** specs). Golden-path walkthrough steps 3–4 annotated as pre–Mission 11.

**Spot check (a11y):** Rotated from states → **auth axe** on `/verify-email` (no-token error state) and `/verify-pending` (unavailable fallback when API unreachable in e2e).

**Gates:** api ruff+mypy+test_email (8); worker ruff+mypy; web full stack; e2e **24×2** consecutive — green. **Blocker:** Docker Desktop unavailable (`500` on engine pipe) — `make migrate-check` / full api pytest deferred to CI.

**Deployment:** unchanged — deploy Mission 11 after Railway SMTP on API+worker.

---

## Loop after Mission 12 — 2026-06-11

### Re-verification (Mission 12 acceptance criteria)

| Criterion | Result |
|-----------|--------|
| Inventory complete; every form compliant on five columns | **Green (scoped)** — all **Y** rows in `12_forms_inventory.md` verified; **P** rows reassigned to Mission 25 |
| 422 inline via shared mapper on migrated forms | **Green** — auth, waitlist, uploads, vault/settings mutations |
| Every submit has pending state | **Green** — `useFormSubmit` on auth + waitlist; mutations use `isPending` / `busy` |
| No input loss on failure | **Green** — e2e `forms-validation.spec.ts` + controlled vault answers |
| All gates green | **Green** — see below |

### Improvements made (this loop)

- `fix(web): link-google useFormSubmit + errors.test [pack-31 after 12]` — last auth form aligned; `formatApiError` regression tests for 422/402.
- Inventory — link-google → **Y**; explicit Mission 25 owner for **P** workspace forms.

### Deferrals

| Item | Owner |
|------|-------|
| Discover/documents/library/admin inline field errors | Mission 25 |
| Upload cancel / progress bar | API lacks abort — future |
| Full api pytest / migrate-check locally | CI (Docker unavailable) |

### Spot check (docs)

- Rotated from a11y (Mission 11 loop) → **docs/commands**: `AGENTS.md` § Forms matches `mapApiErrors` / `useFormSubmit` / `FormField` paths; inventory legend and deferral table consistent with code.

### Gate summary

**Local:** api ruff+mypy; web typecheck, lint:strict, test **94**, build, check:motion, check:bundles (2486/2800 KB), e2e **26×2** — all green.

### Deployment decision

**Deploy recommended** — Mission 12 is contract-neutral UX improvement. Safe to batch with Missions 09–11 web releases. Smoke: auth signup validation, file upload rejection (wrong type), settings vault save toast on error.

---

## Loop after Mission 13 — 2026-06-11

### Re-verification (Mission 13 acceptance criteria)

| Criterion | Result |
|-----------|--------|
| Axe e2e on marketing + core app routes; zero unwaived serious/critical | **Green** — `a11y-marketing`, `a11y-auth`, `a11y-app` (12 route scans + open-palette axe + keyboard + consent); waivers in `13_a11y_waivers.md` |
| Golden path keyboard-operable; focus visible/restored | **Partial (deferred)** — palette Escape + analytics tabs covered in e2e; full import→submit keyboard path → Mission 26 |
| Charts text alternatives; run-console announcements without spam | **Green** — `ChartAccessibleFigure`; `RunStreamAnnouncer` wired in `run-console.tsx`; log is `role="log"` only |
| Contrast fixes token-level and documented | **Green** — `--muted-foreground` in `globals.css`; waiver documents token validation |
| All gates green | **Green (scoped)** — see below |

### Improvements made (this loop)

- `fix(web): command palette separator aria + open-palette axe e2e [pack-31 after 13]` — seam sweep found critical `aria-required-children` when palette open (cmdk `role="separator"` inside `listbox`); `CommandSeparator` now decorative (`role="none"`); added `axe clean: command palette when open` to `a11y-app.spec.ts`.
- `docs(pack): assign keyboard golden path to Mission 26 [pack-31 after 13]` — explicit deferral in `26_e2e_validation_expansion.md` Context.

### Deferrals

| Item | Owner |
|------|-------|
| Full keyboard golden path (import → checkpoint → submit) | Mission 26 |
| NVDA spot-check on `/queue` and `/runs/[id]` with fixture data | Manual / Mission 26 |
| `make migrate-check`, api/worker pytest, fixtures, policy | CI — Docker Desktop unavailable locally (500 on engine API) |

### Spot check (states)

- Rotated from docs (Mission 12 loop) → **route states**: verified `/queue` uses `PageLoading` / `PageError` / table content via `loading.tsx` + query branches; `/runs/[id]` uses `RunConsoleSkeleton` + `PageError` in `run-console.tsx`. E2e axe on both routes green without API (chrome + skeleton/error paths).

### Gate summary

**Local:** api ruff+mypy; worker ruff+mypy; web typecheck, lint:strict, test **94**, build, check:motion, check:bundles (**2489**/2800 KB), e2e **38×2** — all green.

**CI (expected):** full gate set including migrate-check + pytest per `.github/workflows/ci.yml`.

### Deployment decision

**Deploy recommended** — Mission 13 is low-risk accessibility improvement (palette crash fix, chart alts, live-region tuning). Batch with prior web polish (Missions 09–12). Smoke after deploy: open command palette (⌘K), analytics page tabs, queue import dialog. Not deploying from this host — push to CI and deploy via runbook when ready.

---

## Loop after Mission 14 — 2026-06-11

### Re-verification (Mission 14 acceptance criteria)

| Criterion | Result |
|-----------|--------|
| Findings table resolved to per-surface targets | **Green** — `14_responsive_findings.md` complete |
| No horizontal body overflow at 375/768 (e2e) | **Green** — `responsive-smoke.spec.ts` (26 tests after loop) |
| Run console operable on tablet | **Green (scoped)** — Work\|Canvas tabs + header canvas button switch at 375/768; live checkpoint resolve → Mission 26 |
| Mobile nav + touch palette trigger | **Green** — e2e asserts nav menu, Search palette, marketing menu |
| Mobile screenshots + gates green | **Green** — 5 PNGs in `docs/screenshots/mobile/`; see gates below |

### Improvements made (this loop)

- `test(e2e): extend responsive smoke for run console + marketing menu [pack-31 after 14]` — run tabs on phone and tablet; header “Show canvas” switches tab; marketing mobile menu visibility.
- `docs: README responsive section + Mission 26 checkpoint deferral [pack-31 after 14]`.

### Deferrals

| Item | Owner |
|------|-------|
| Live checkpoint resolve e2e at 768 with fixture API | Mission 26 |
| Card-list queue fallback, PWA, pixel-perfect admin on phone | Out of scope per Mission 14 |
| `make migrate-check`, api/worker pytest, fixtures, policy | CI — Docker Desktop unavailable locally |

### Spot check (a11y)

- Rotated from states (Mission 13 loop) → **responsive + a11y names**: `RunOpsDeskShell` tablist `aria-label="Run console views"`; touch triggers use explicit `aria-label`s; full axe suites (marketing + auth + app) still green in combined e2e run (64 tests).

### Gate summary

**Local:** api ruff+mypy; worker ruff+mypy; web typecheck, lint:strict, test **94**, build, check:motion, check:bundles (**2500**/2800 KB), e2e **64×2** — all green.

### Deployment decision

**Deploy recommended** — Mission 14 is layout/CSS only. Smoke on real phone: `/`, `/signup`, nav drawer, dashboard Search icon, run console tabs at tablet width. Batch with Missions 09–13 web polish. Not deploying from this host — push to CI and run `scripts/railway-smoke.sh` after deploy.

---

## Loop after Mission 15 — 2026-06-10

### Re-verification (Mission 15 acceptance criteria)

| Criterion | Result |
|-----------|--------|
| Every chaos condition recorded (no lost events, reconnect state, conflicts) | **Green** — `15_console_chaos.md` (automated + code-path evidence) |
| 500+ event run stays responsive | **Green** — `prune-events.test.ts`, `MAX_STREAM_EVENTS=500` |
| All run end states render designed summaries | **Green** — `run-end-state-summary.tsx` |
| SSE survives idle (heartbeat) | **Green** — `test_sse_emits_heartbeat_when_idle`; 15s in production |
| Resume-from-seq + resolve idempotency tests; gates green | **Green** — 3 new API tests; web vitest + e2e |

### Improvements made (this loop)

- `feat(web): run console SSE reconnect and checkpoint hardening [pack-15]` — landed Mission 15 (15 files).
- `fix(web): review canvas checkpoint conflict sync [pack-31 after 15]` — `review-canvas-view.tsx` mirrors `checkpoint-card` 422 “already resolved” → `reconnect()`.
- `docs(missions): assign Mission 15 e2e/screenshot deferrals [pack-31 after 15]` — Mission 26 (checkpoint resolve + SSE e2e), Mission 24 (run/admin screenshots).

### Deferrals

| Item | Owner |
|------|-------|
| `/runs/[id]` screenshots (active, checkpoint, end state) | Mission 24 / 26 capture pass with seeded fixture run |
| Staging chaos re-verify (kill API, Slow 3G, two-tab) | Post-deploy — `railway-smoke.sh` + manual |
| `make migrate-check`, api/worker pytest, fixtures, policy | CI — Docker Desktop unavailable locally |

### Spot check (chaos)

- Rotated from a11y (Mission 14 loop) → **run console chaos checklist**: re-mapped each row in `15_console_chaos.md` to test or code evidence; 17/17 **Pass** or **Pass (code)** with staging manual called out in follow-ups.

### Gate summary

**Local:** api ruff+mypy; worker ruff+mypy; web typecheck, lint:strict, test **102**, build, check:motion, check:bundles (**2508**/2800 KB), e2e **66×2** — all green.

**Local blocker:** Docker engine unavailable — `make migrate-check`, `pytest`, `test-fixtures`, `test-policy` not rerun on host; CI authoritative.

### Deployment decision

**Deploy recommended** — Mission 15 hardens the signature surface (SSE reconnect contract, checkpoint idempotency). **Deploy API and web together** (SSE + resolve semantics). After deploy: verify a real run stream ≥5 min idle, resolve a checkpoint once, run `bash scripts/railway-smoke.sh`, capture `/runs/[id]` screenshots when fixture run available.

---

## Loop after Mission 16 — 2026-06-10

### Re-verification (Mission 16 acceptance criteria)

| Criterion | Result |
|-----------|--------|
| All entry paths batch-ready; journey matrix green | **Green** — `16_journey_findings.md` (manual single-job documented gap) |
| `/search` vs `/discover` explicit in UI | **Green** — page subtitles, nav tooltips, cross-links, `discover-journey.spec.ts` |
| Export → re-import loss-free for app-owned columns | **Green (API)** — `test_xlsx_round_trip.py` in CI |
| Batch policy choices unmistakable | **Green** — `BatchPreviewDialog` dry_run vs review_before_submit + auto-submit note |
| All gates green | **Green (scoped)** — see below |

### Improvements made (this loop)

- `chore(import): add Discover handoff on import complete [pack-31 after 16]` — import wizard done state links to **Build a list** (`/discover`).
- `docs(missions): assign Mission 16 fixture batch e2e to Mission 26 [pack-31 after 16]`.

### Deferrals

| Item | Owner |
|------|-------|
| Fixture batch preview e2e (included/excluded API) | Mission 26 |
| Manual XLSX round-trip UI on production | Operator post-deploy |
| Manual single job add API | Future (documented in `16_journey_findings.md`) |
| `make migrate-check`, api pytest, `test-policy`, fixtures | CI — Docker unavailable locally |

### Spot check (states)

- Rotated from chaos (Mission 15 loop) → **route states** on acquisition surfaces: `/queue` retains `PageLoading` / `PageError` + `QueuePolicyBanner`; `/discover` renders shell with tabs and list panel without API (e2e chrome green); import wizard preview/done steps show warnings and CTAs.

### Gate summary

**Local:** api ruff+mypy; worker ruff+mypy; web typecheck, lint:strict, test **104**, build, check:motion, check:bundles (**2548**/2800 KB), e2e **68×2** — all green.

**Local blocker:** Docker engine unavailable — `make migrate-check`, `pytest`, `test-policy`, `test-fixtures` deferred to CI.

### Deployment decision

**Deploy recommended** — Mission 16 is UX/copy + batch preview (no policy logic changes). Safe to batch with Missions 04–16 web polish. **Post-deploy:** disposable-account dry-run XLSX import, verify batch preview exclusions on a list with mixed job statuses, `bash scripts/railway-smoke.sh`.

---

## Loop after Mission 17 — 2026-06-10

### Re-verification (Mission 17 acceptance criteria)

| Criterion | Result |
|-----------|--------|
| Findings table fully green; lock-preservation test-enforced | **Green** — `17_studio_findings.md`; `merge-paragraphs.test.ts` + API `test_merge_paragraphs_preserves_locked` (CI) |
| Stub mode and 402 honestly labeled | **Green** — `LlmProviderBanner`, `LlmBudgetExceeded` in studio + canvas |
| Studio and canvas share components and behavior | **Green** — `paragraph-controls`, `keyword-coverage-panel`, shared download naming |
| Micro-interactions pass `check:motion` + reduced-motion | **Green** — motion tokens only; no new raw durations |
| All gates green; screenshot 18 re-captured | **Green (scoped)** — web gates + e2e; PNG refresh **deferred** post-deploy |

### Improvements made (this loop)

- `test(e2e): axe library document studio route [pack-31 after 17]` — closes blast-radius gap: studio sub-nav + error/empty chrome axe-clean without API.
- `docs(pack): seam sweep after Mission 17 [pack-31 after 17]` — README studio URL; screenshot script `18-library-letters` → `view=studio`; Mission 26 deferral for fixture letter cycle; forms inventory 402 panel note.

### Deferrals

| Item | Owner |
|------|-------|
| Screenshot `18-library-letters.png` re-capture | Post-deploy (`capture-screenshots.mjs` path updated) |
| Fixture generate→lock→regen→download e2e | Mission 26 (`document-studio.spec.ts` chrome-only) |
| `make migrate-check`, api/worker pytest, fixtures, policy | CI — Docker Desktop engine 500 locally |

### Spot check (a11y)

- Rotated from states (Mission 16 loop) → **authenticated app axe** on new `/library?tab=letters&view=studio` surface (paragraph controls, LLM banners, job picker or error empty).

### Gate summary

**Local:** api ruff+mypy; worker ruff+mypy; web typecheck, lint:strict, test **107**, build, check:motion, check:bundles (**2547**/2800 KB), e2e **71×2** — all green.

**Local blocker:** Docker engine unavailable — Mission 17 API validation (`test_cover_letter_v2.py`, etc.) and `make migrate-check` deferred to CI.

### Deployment decision

**Deploy recommended** — Mission 17 is web-only UX (no API contract change). Batch with Missions 04–17 web polish. **Post-deploy:** open Library → Document Studio with a job + resume, verify template banner when no LLM key, run `bash scripts/railway-smoke.sh`, re-capture screenshot `18-library-letters.png`.

---

## Loop after Mission 18 — 2026-06-10

### Re-verification (Mission 18 acceptance criteria)

| Criterion | Result |
|-----------|--------|
| One documented envelope; inventory shows routers conforming | **Green** — `errors.md`, `18_error_inventory.md` |
| No error body leaks internals (test-enforced) | **Green** — `test_error_contract.py` opaque 500 + leak markers |
| Cross-tenant 404 convention | **Green** — unchanged; `tenant_guard` + isolation tests (CI) |
| Downstream outages → deliberate 503; `/readyz` truth | **Green** — resume upload + documents generate; readiness unchanged |
| All gates green incl. policy | **Green after fix** — CI `[pack-18]` failed on middleware; fixed below |

### Improvements made (this loop)

- `fix(api): pure ASGI correlation middleware [pack-31 after 18]` — replaces `BaseHTTPMiddleware` on correlation IDs (CI run 27357876037).
- `fix(api): pure ASGI auth middleware [pack-31 after 18]` — `AuthMiddleware` also used `BaseHTTPMiddleware`; stacked middleware triggered pytest-asyncio `Runner.run()` errors on all async tests (CI run 27361588075 still red — root cause was conftest, not middleware).
- `fix(test): seed tenant in db_engine fixture [pack-31 after 18]` — removed autouse `seed_default_tenant` that called `getfixturevalue("db_engine")` inside an async fixture (nested `Runner.run()` during setup). CI 284 passed / 4 failed on `7ee082d`.
- `fix(api): error envelope follow-ups [pack-31 after 18]` — Starlette 404 handler registration; leak check only on opaque 500; import 422 message sanitized; error-contract tests use seeded DB + auth. CI `d655e8f`: 286 passed / 2 failed.
- `fix(test): revert asyncio loop scope to function [pack-31 after 18]` — session loop scope caused 174 failures with per-test engine dispose.
- `fix(api): isinstance StarletteHTTPException + run_console factory patch [pack-31 after 18]` — routing 404s still returned 500 (`isinstance(exc, HTTPException)` too narrow); SSE used module-level pool on wrong event loop.
- `docs(architecture): note ASGI middleware choice in errors.md`.

### Deferrals

| Item | Owner |
|------|-------|
| Bulk `detail=str(exc)` normalization | Incremental / Mission 25 |
| Celery enqueue → 503 | Mission 23 |
| `make migrate-check`, full api pytest locally | CI authoritative (Docker unavailable locally) |

### Spot check (chaos)

- Rotated from a11y (Mission 17 loop) → **downstream failure / readiness**: `/readyz` still reports per-dependency checks; runtime MinIO outage on resume upload maps to **503** `dependency_unavailable` without leaking driver text (`test_error_contract.py`).

### Gate summary

**CI progression:** 280 errors (`getfixturevalue` in autouse fixture) → 4 failures (`7ee082d`) → 2 failures (`1398911`) → **green** (`6676845`, run [27368885194](https://github.com/HiNala/jober/actions/runs/27368885194)): api **288** passed, web **71** e2e, policy/quarantine jobs ran.

**Local:** api ruff+mypy; web typecheck, lint:strict, unit **108**, build, check:motion — green. `make migrate-check` / local api pytest deferred (Docker engine 500 on host); CI authoritative.

### Deployment decision

**Deploy API + web together** — Mission 18 Production Guidance. **Ready to batch** with Missions 04–18 (CI green on `6676845`). Post-deploy: stop MinIO → resume upload returns 503 with retry copy; restart MinIO → upload succeeds without API restart; `bash scripts/railway-smoke.sh`.

---

## Loop after Mission 19 — 2026-06-11

### Re-verification (Mission 19 acceptance criteria)

| Criterion | Result |
|-----------|--------|
| Auth matrix complete with evidence per row | **Green** — `19_auth_matrix.md`; middleware 401 row added this loop |
| CSRF test-enforced on mutating routes + exempt list | **Green** — `test_csrf_coverage.py` parametrizes OpenAPI routes; exempt = `PUBLIC_API_PREFIXES` |
| Cookie flags + SameSite rationale documented | **Green** — `test_auth_cookies.py`; Railway `None`+`Secure` documented |
| Logout + password-change revocation tested | **Green** — `test_logout_invalidates_session_server_side`, `test_password_change_revokes_other_sessions` |
| Login/signup/reset rate-limited; gates green | **Green** — `check_rate_limit` on auth routes; `test_lockout_after_failed_logins`; CI **364** api + **71** e2e + policy |

### Improvements made (this loop)

- `docs(pack): auth matrix middleware 401 row [pack-31 after 19]` — documents `e9a5b9e` behavior in matrix.

### Deferrals

| Item | Owner |
|------|-------|
| Manual prod cookie devtools + CSRF negative curl | Post-deploy verification (Mission 19 Production Guidance) |
| `make migrate-check`, full local api pytest | CI authoritative (Docker engine 500 on host) |
| Separate idle session timeout | Future hardening (`19_auth_matrix.md` § Open) |
| Clerk-mode dead code decision | Product owner |

### Spot check (a11y)

- Rotated from chaos (Mission 18 loop) → **auth surface axe**: `e2e/a11y-auth.spec.ts` **9/9** locally (login, signup, forgot/reset, verify, link-google, keyboard tab order).

### Gate summary

**CI:** run [27373012507](https://github.com/HiNala/jober/actions/runs/27373012507) on `e9a5b9e` — backend, web **71** e2e, policy, quarantine **success**.

**Local:** api ruff+mypy; web typecheck, lint:strict, unit **108**, build, check:motion; a11y-auth **9** — green.

### Deployment decision

**Deploy API promptly** — Mission 19 Production Guidance (session hardening protects live users). Web unchanged in pack-19 (CSRF header already in `client.ts`). **Post-deploy:** devtools cookie flags on prod login; logout → old cookie rejected; OAuth link smoke; `bash scripts/railway-smoke.sh`; keep `docs/runbooks/rollback.md` handy for cookie misconfig.

---

## Loop after Mission 20 — 2026-06-11

### Re-verification (Mission 20 acceptance criteria)

| Criterion | Result |
|-----------|--------|
| Fresh-DB replay + drift check green | **Green** — `88462e6`…`74f9b7b`; migrate-check on Postgres `:5435` |
| Hot paths indexed | **Green** — `r1a2b3c34d65`; `test_db_hot_paths.py` (`pg_indexes` + EXPLAIN) |
| Retention deletes DB + storage | **Green** — `test_purge_storage.py`, `test_artifact_retention.py` (MinIO mocked) |
| Backup/restore drill | **Documented** — `restore-backup.md` + `20_db_hygiene.md`; full destroy-restore deferred (port conflicts) |
| Pool settings | **Green** — `DATABASE_POOL_SIZE=5`, `DATABASE_MAX_OVERFLOW=5` (`a79bc37`) |

### Improvements made (this loop)

| Commit | Summary |
|--------|---------|
| `88462e6` | `feat(db): composite queue indexes [pack-20]` |
| `a79bc37` | `chore(api): database pool defaults [pack-20]` |
| `74f9b7b` | `fix(api): ProWaitlistEntry in drift check [pack-20]` |
| `bc6d77a` | `test(api): hot-path indexes and retention purge [pack-20]` |
| `d3ec0ca` | `docs(pack): 20_db_hygiene drill log [pack-20]` |
| `105bfc7` | `chore(api): bump fastapi minimum [pack-31 after 20]` |
| `e458e77` | `docs(pack): continuation loop after Mission 20 [pack-31 after 20]` |
| `44e8df3` | `fix(test): planner-chosen index in EXPLAIN [pack-31 after 20]` — CI flake on `ix_job_targets_status` |

### Deferrals

| Item | Owner |
|------|-------|
| Full local api pytest (30 fails) | Host MinIO port 9000 owned by another stack (`InvalidAccessKeyId`); CI authoritative |
| Backup destroy-restore loop on Windows | Git Bash drill in runbook; Mission 29 |
| `CREATE INDEX CONCURRENTLY` at scale | Re-evaluate when `job_targets` > ~100k rows |

### Spot check (docs)

- Rotated from performance (Mission 20 draft) → **runbook accuracy**: `restore-backup.md` `make backup` / `make restore` targets match `Makefile`; Windows requires Git Bash/WSL for `.sh` scripts.

### Gate summary

**Local:** migrate-check, api ruff+mypy, worker ruff+mypy+pytest **22**, web typecheck — green. Api full pytest **342 passed / 30 failed** (MinIO/Redis infra on host, not pack-20 regressions).

**CI:** run [27382928455](https://github.com/HiNala/jober/actions/runs/27382928455) on `44e8df3` — migrate-check, api **372** passed, worker **22**, web **71** e2e, policy **36** — **success**. (Prior run `27380709893` failed one EXPLAIN assertion — fixed in `44e8df3`.)

### Deployment decision

**Deploy API** — CI green on `44e8df3`. Production backup before `r1a2b3c34d65` index migration. Plain `CREATE INDEX` at current scale. Smoke queue + admin runs filter post-deploy; `bash scripts/railway-smoke.sh`.

---

## Loop after Mission 21 — 2026-06-11

### Re-verification (Mission 21 acceptance criteria)

| Criterion | Result |
|-----------|--------|
| Threat-model controls probed with evidence | **Green** — `21_security_matrix.md` (19 rows, all pass) |
| Dependency audits clean or waived | **Green** — postcss transitive via Next waived; API audit on CI clean install |
| Security headers baseline | **Green** — API middleware + web `next.config.ts` (CSP report-only) |
| Policy suite green | **Green** — CI policy job **44** passed (`+8` from `test_security_controls.py`) |
| `threat-model.md` current | **Green** — Mission 21 deltas (headers, webhooks, startup guards) |

### Improvements made (this loop)

No code changes — Mission 21 landed complete on `4387b97`; this loop re-verifies and records gates.

| Commit (prior) | Summary |
|----------------|---------|
| `3df6e29` | `feat(api): security headers [pack-21]` |
| `4ad4ff8` | `test(api): security probes [pack-21]` |
| `784b930` | `chore(web): CSP report-only [pack-21]` |
| `4387b97` | `docs(pack): security matrix [pack-21]` |

### Deferrals

| Item | Owner |
|------|-------|
| Enforce CSP (remove report-only) | After console clean across routes (Mission 21 guidance) |
| PostCSS transitive advisory | Next.js upgrade / Mission 22 |
| `pre-commit run --all-files` locally | CI `detect-secrets` job is authoritative |
| Full local api pytest / policy DB probes | Host Postgres/MinIO unavailable; CI authoritative |

### Spot check (chaos)

- Rotated from docs (Mission 20 loop) → **downstream failure**: invalid Stripe webhook signature returns **400** with generic detail and no `whsec` substring (`test_stripe_webhook_rejects_invalid_signature` — 5 local unit probes green).

### Gate summary

**CI:** run [27384431210](https://github.com/HiNala/jober/actions/runs/27384431210) on `4387b97` — migrate-check, api **380** passed, worker **22**, web **71** e2e, policy **44**, quarantine — **success**.

**Local:** api ruff+mypy; worker ruff+pytest **22**; web typecheck; Mission 21 unit probes **5** — green.

### Deployment decision

**Deploy API + web together** — Mission 21 Production Guidance (headers/CSP touch both surfaces). Post-deploy: login smoke, browser console for CSP reports, artifact download, `bash scripts/railway-smoke.sh`. Batch with Mission 20 index migration if not yet deployed.

---

## Loop after Mission 22 — 2026-06-12

### Re-verification (Mission 22 acceptance criteria)

| Criterion | Result |
|-----------|--------|
| Marketing LCP &lt; 2.5s, CLS &lt; 0.1 (prod mobile) | **Deferred** — Lighthouse CLI interstitial on `jober.app`; manual PSI post-deploy (`22_perf_baseline.md`) |
| No app-only heavy deps in marketing/auth chunks | **Green** — `check-bundle-budget.mjs` import guard (re-run 2026-06-12) |
| `/analytics` + `/runs/[id]` dynamic imports | **Green** — `dynamic()` on panels + `RunConsole` (source re-verified) |
| Budgets tightened; `check:bundles` protective | **Green** — 2650 KB cap, measured **2560 KB** |
| Compositor-clean animations; gates green | **Green** — `check:motion` + full web validation |

Mission 22 validation re-run verbatim: typecheck, lint:strict, test **108**, build, check:motion, check:bundles, test:e2e — all green on `4cca814`.

### Seam sweep (provider blast radius)

- Root `layout.tsx` → `ShellProviders` only; `(app)` + `(auth)` → `AppProviders`; legacy `Providers` wrapper retained for tests.
- Marketing/blog/legal routes inherit shell-only stack (no QueryClient/auth bootstrap on first paint).
- `/kitchen-sink` remains shell-only (no `useAuth` / `useQuery`); note unchanged.
- No screenshot re-capture — visual surfaces unchanged (bundle/route-tree only).

### Improvements made (this loop)

| Commit | Summary |
|--------|---------|
| `4259b94` | `perf(web): marketing-first provider split and hero deferral [pack-22]` |
| `4cca814` | `docs(pack): Mission 22 performance baseline [pack-22]` |
| (this loop) | `docs(pack): continuation loop after Mission 22 [pack-31 after 22]` — gates.md Windows e2e port note |

### Deferrals

| Item | Owner |
|------|-------|
| Lighthouse/PSI table for `/`, `/features`, `/pricing`, `/signup` | Operator post-deploy PSI |
| Below-fold marketing `dynamic()` if LCP still high | Mission 28 |
| `/kitchen-sink` + `AppProviders` if React Query needed later | note only |

### Spot check (a11y)

- Rotated from performance (Mission 22 close) → **marketing hero**: `section` has `aria-labelledby="hero-heading"`; H1 `id` matches; decorative icons + lazy-load pulse `aria-hidden`; CTAs remain real links with visible text. No regressions from hero `dynamic()` deferral.

### Gate summary

**CI:** run [27389964744](https://github.com/HiNala/jober/actions/runs/27389964744) on `4cca814` — backend, web (**71** e2e), policy, quarantine — **success**.

**Local (pack-31 re-run):** typecheck, lint:strict, test **108**, build, check:motion, check:bundles **2560/2650**, test:e2e **70 passed + 1 flaky** (`document-studio.spec.ts`); repeat `×3` on that spec → **6/6** green (environmental timing; CI clean).

### Deployment decision

**Deploy web** — Mission 22 Production Guidance: client-only perf wins; no API contract change. Batch with any pending Mission 20/21 deploy if not yet live. Post-deploy: PSI mobile on `/` and `/signup`, fill `22_perf_baseline.md` Lighthouse table, `bash scripts/railway-smoke.sh`.

---

## Loop after Mission 23 — 2026-06-12

### Re-verification (Mission 23 acceptance criteria)

| Criterion | Result |
|-----------|--------|
| Latency table recorded; fixed endpoints show measured improvement; p95 targets at seeded volume | **Green** — `23_backend_perf.md` + guards in `test_load_smoke.py` (`test_hot_paths_at_perf_volume`) |
| Every list endpoint paginates with enforced limits | **Green** — library, job-lists, documents, resumes (`max 200`); job-targets (`max 2000`); inventory in notes |
| Rollup linear-ish in event count | **Green** — `test_analytics_rollup_scales_linearly` (2k &lt; 2s, 10k &lt; 8s, &lt; 8× ratio) |
| Worker pacing/lock drills pass; SSE fan-out zero loss at N=10 | **Green** — `test_domain_lock_serializes_same_host`, `test_sse_fanout_no_event_loss`; batch enqueue in `test_batch_ops.py` |
| Regression guards in `test_load_smoke.py`; all gates green | **Green** — CI on `5800cc0` |

Mission 23 validation re-run: api `ruff` + `mypy` green locally; worker `ruff` + `mypy` + pytest **22** (Python 3.12). Full pytest load suite authoritative on CI (`backend` job).

### Seam sweep (pagination + dashboard blast radius)

- Web `library.ts` / `jobs.ts` consume `{ items }` only — added `limit`/`offset` metadata is backward compatible (no web change required).
- Dashboard `queue_depth_priority_a` now SQL `COUNT` via `JobTargetRepository.count_filtered` — runbook `queue-backed-up.md` updated (high depth = real backlog).
- Perf volume seed: `apps/api/scripts/seed_perf_volume.py` + `services/dev/perf_volume.py` — dev/CI only.
- No user-facing screenshot re-capture (API/worker-only mission).

### Improvements made (this loop)

No code changes — Mission 23 commits (`7311a87`…`5800cc0`) verified complete; tree was clean at loop start.

### Deferrals

| Item | Owner |
|------|-------|
| Production latency sampling (Railway) | Mission 24 / operator |
| Redis response caching for dashboard | Out of scope (Mission 23) |
| `job-targets` `total` field (page size vs DB count) | Future API hygiene |
| Local full API pytest on Windows host (port conflicts) | CI authoritative; use `POSTGRES_HOST_PORT=5434` per `gates.md` |

### Spot check (chaos)

Rotated from a11y (Mission 22) → **backend contention drills**: `test_domain_lock_serializes_same_host` asserts same-host batches serialize via Redis lock; `test_sse_fanout_no_event_loss` asserts 10 concurrent SSE consumers receive all 30 events with no loss. Runbook cross-check: `queue-backed-up.md` documents domain-lock diagnosis path.

### Gate summary

**CI:** run [27396078702](https://github.com/HiNala/jober/actions/runs/27396078702) on `5800cc0` — backend, web, policy, quarantine — **success**.

**Local:** api ruff + mypy green; worker ruff + mypy + pytest **22** (py 3.12). Web gates unchanged since Mission 22 (no web diff in M23).

### Deployment decision

**Deploy API** — Mission 23 Production Guidance: gates green; pagination is backward compatible (web reads `items` only). Safe to deploy API without web if M20 index migration (`r1a2b3c34d65`) is already live; otherwise batch API deploy with M20 backup + migrate. Post-deploy: `bash scripts/railway-smoke.sh`, spot-check `/api/dashboard/summary` latency. Batch with pending M21/M22 web deploy if not yet live (independent surfaces).

---

## Loop after Mission 24 — 2026-06-12

### Re-verification (Mission 24 acceptance criteria)

| Criterion | Result |
|-----------|--------|
| Admin-overview metrics spot-verified | **Green** — `24_observability.md` truth table; `test_observability.py` run-count reconciliation |
| Alert classes fire + email-failure alerting | **Green** — `test_ops_alerting.py` + new email enqueue/send classes with runbook links |
| Sentry decision documented | **Green** — optional `SENTRY_DSN`; `send_default_pii=False`; worker does not init |
| Three log questions answerable | **Green** — `batch_item_failed`, `llm_budget_exceeded`, `run_purged` structured fields |
| Correlation id web → API → worker | **Green** — middleware + `celery_enqueue` headers + worker `task_prerun` |
| Uptime on schedule with failure alerting | **Fixed** — `uptime.yml` job-level `secrets` `if` caused workflow validation failure; step-level skip when `UPTIME_API_URL` unset |

### Improvements made (this loop)

| Commit | Summary |
|--------|---------|
| `db2530e` | `feat(ops): observability alerts, correlation ids [pack-24]` |
| `fe8fc40` | `docs(pack): Mission 24 baseline + uptime schedule [pack-24]` |
| (this loop) | `fix(ci): uptime workflow skip when secrets unset [pack-31 after 24]` |

### Deferrals

| Item | Owner |
|------|-------|
| Set `UPTIME_*` GitHub secrets for live 5m smoke | Operator |
| Production webhook drill (`POST /api/admin/ops/test-alert`) | Operator post-deploy |
| Enable `SENTRY_DSN` on Railway | Operator optional |
| Grafana/Prometheus | Out of scope |

### Spot check (docs)

- Rotated from chaos (Mission 23) → **runbook cross-links**: alert payloads reference `email-delivery.md`, `uptime-monitoring.md`, `queue-backed-up.md`, `cost-spike.md`, `worker-stuck.md` per `24_observability.md` matrix.

### Gate summary

**CI:** run [27400717154](https://github.com/HiNala/jober/actions/runs/27400717154) on `0b2c08a` — backend, web **71** e2e, policy, quarantine — **success**. Uptime [27401070968](https://github.com/HiNala/jober/actions/runs/27401070968) — **success** (skips smoke until `UPTIME_API_URL` secret set).

**Local:** api ruff+mypy; `test_observability.py` + `test_ops_alerting.py` **7 passed** (2 skipped); worker pytest **22** — green.

### Deployment decision

**Deploy API** — Mission 24 Production Guidance: ops/alerting + log fields only; configure `OPS_ALERT_WEBHOOK_URL` on Railway before relying on alerts. Post-deploy: `POST /api/admin/ops/test-alert`, set GitHub `UPTIME_*` secrets, `bash scripts/railway-smoke.sh`. Batch with pending M20–M23 API deploy if not yet live.

---

## Loop after Mission 25 — 2026-06-12

### Re-verification (Mission 25 acceptance criteria)

| Criterion | Result |
|-----------|--------|
| Coverage map complete; paths covered or waived | **Green** — `25_coverage_map.md` matrix + waivers |
| Web tests for pack-introduced behavior | **Green** — consent, forms, page states, reconnect labels, palette, document lock |
| Zero flakes across 3× runs | **Green** — `pnpm test` **125** ×3 local |
| Mutation spot-checks (fill policy + redaction) | **Green** — `test_coverage_critical.py` + JWT/bearer in `test_privacy_redaction.py` |
| CI duration within +25%; gates green | **Pending CI** — +12 web / +5 api unit tests only |

### Improvements made (this loop)

| Commit | Summary |
|--------|---------|
| `7e69a8e` | `test(web): critical-path unit coverage [pack-25]` |
| `48f1860` | `test(api): critical-path coverage and mutation spot-checks [pack-25]` |
| `24de4db` | `docs(pack): Mission 25 coverage map [pack-25]` |
| `e9dc3b3` | `fix(test): bearer redaction assertion [pack-31 after 25]` — CI [27403227110](https://github.com/HiNala/jober/actions/runs/27403227110) |

Mission 25 work was uncommitted at loop start — triaged and landed in clustered commits.

### Deferrals

| Item | Owner |
|------|-------|
| `useRunStream` reconnect timer e2e | Mission 26 |
| React mount tests (ConsentSheet, DocumentStudio) | Mission 26 |
| Form inventory **P** inline field errors | Incremental / Mission 12 |
| Full API pytest 3× on Windows host | CI authoritative |

### Spot check (states)

Rotated from docs (Mission 24) → **page-state contracts**: `page-state-contracts.ts` ARIA roles (`status`/`alert`) wired into `page-states.tsx`; `page-state-contracts.test.ts` asserts loading busy + empty-state copy has actionable descriptions.

### Gate summary

**Local:** web typecheck + lint:strict + test **125**; api ruff + `test_coverage_critical` **4**; worker pytest **22**.

**CI:** [27403227110](https://github.com/HiNala/jober/actions/runs/27403227110) failed — `test_scrub_text_masks_bearer_and_jwt_tokens` (`Authorization:` triggers pair rule); fixed in `e9dc3b3`. [27403821913](https://github.com/HiNala/jober/actions/runs/27403821913) on `5be82f6` — **success** (backend, web **71** e2e, policy).

### Deployment decision

**Not deploying** — Mission 25 Production Guidance: test-only changes. No production surface change.

---

## Loop after Mission 26 — 2026-06-12

### Re-verification (Mission 26 acceptance criteria)

| Criterion | Result |
|-----------|--------|
| Five full-stack Playwright specs (core, recovery, studio, settings, auth) | **Green** — 4 specs pass in CI; `auth-journey` skipped unless `E2E_AUTH_NATIVE=1` (documented waiver) |
| `e2e-fullstack` CI job with Postgres/Redis/MinIO/API/worker/fixtures | **Green** — 5 passed on [27433804816](https://github.com/HiNala/jober/actions/runs/27433804816) |
| Docs (`26_e2e_map.md`, gates §8, testing.md) | **Green** |
| Marketing e2e unchanged and green | **Green** — 71 passed on prior CI web job |

### Improvements made (this loop)

| Area | Fix |
|------|-----|
| `fill-form` 500 in CI | `PLAYWRIGHT_HEADED=false` on `e2e-fullstack` job — Python fill-runner was launching headed Chromium on a headless runner |
| Batch preview stuck on “Loading preview…” | `BatchPreviewBody` effect depended on unstable `onClose` callback → infinite cancel/reload; stabilized with ref |
| Recovery drawer missing failure panel | Duplicate workbook imports created multiple “Company N” rows; test now clicks `[data-job-id]` |
| E2E web build auth | `NEXT_PUBLIC_DEV_AUTH_BYPASS` + dev tenant/user IDs baked at `pnpm build` in fullstack job |

Prior loop commits (`0ff067d`…`22acfde`) landed Mission 26 infrastructure; this loop closes the remaining CI seams.

### Deferrals

| Item | Owner |
|------|-------|
| `auth-journey.fullstack.spec.ts` in CI | Mission 26 waiver — requires `E2E_AUTH_NATIVE=1` + native auth stack |
| Fullstack 3× local flake burn-in | Optional — CI authoritative when Docker stack available |
| `fill_from_fixture_html` tenant-scoped `UserProfileRepository` | Incremental hardening (not blocking once headed=false) |

### Spot check (a11y)

Rotated from states → **a11y**: command-palette axe flake fixed earlier (`test.setTimeout(60_000)` + explicit dialog wait in `a11y-app.spec.ts`); marketing e2e **71** passed locally with port 3000 cleared.

### Gate summary

**Local:** `pnpm typecheck`, `lint:strict` (changed files), prior loop `pnpm test` **125**, build/motion/bundles green.

**CI (pre-fix):** [27417131507](https://github.com/HiNala/jober/actions/runs/27417131507) — backend/web/policy green; `e2e-fullstack` **2 passed, 3 failed** (checkpoint `fill-form` 500, recovery panel, settings batch policy).

**CI (post-fix):** Full CI green on [27433804816](https://github.com/HiNala/jober/actions/runs/27433804816) — `e2e-fullstack` **5 passed**, marketing e2e **71 passed**, backend/policy green.

**Commits (this loop):** `39abf77`…`3523766` (10 commits).

**Root causes fixed:** `PLAYWRIGHT_HEADED=false` for API fill-runner; missing `Content-Type` on browser JSON POSTs; batch preview effect re-fetch loop; extraction login-gate failure report embed; `/queue?job=` drawer deep-link; consent sheet dismiss stability.

### Deployment decision

**Not deploying** — Mission 26 is test/CI infrastructure only; production unchanged with full `e2e-fullstack` green.

---

## Loop after Mission 27 — 2026-06-12

### Re-verification (Mission 27 acceptance criteria)

| Criterion | Result |
|-----------|--------|
| P0 copy bugs fixed; zero dev/CMS/placeholder copy (`grep apps/web/src`) | **Green** — queue/dropzone closed Mission 05; vault error + blog comment fixed M27 |
| Marketing copy implements §17 one-liner and pillars | **Green** — `POSITIONING_ONE_LINER` on hero + home metadata |
| Public routes: unique metadata, JSON-LD, sitemap/robots/canonicals | **Green** — `SoftwareApplication` `/`, `FAQPage` `/faq`, `BlogPosting` `/blog/*`; `ROBOTS_DISALLOW_PATHS`; OG images deferred |
| Voice guide + sweep table | **Green** — `docs/polish-pack/notes/27_voice_guide.md` |
| All gates green | **Green** — see Gate summary |

### Improvements made (this loop)

| Commit | Change |
|--------|--------|
| `2683b46` | P0: vault user-facing error; blog CMS comment removed |
| `26006cd` | Legal “In short” summaries; JSON-LD home/blog; robots disallow workspace paths |
| `f4d7394` | Voice guide + UI-REVIEW P0 copy rows closed |
| `22bbf9c` | Hero wired to §17 one-liner constants |
| `65ec6fb` | Email template voice pass (ruff-clean) |

**Seam fix:** `templates.py` password-reset line wrapped for ruff E501 before API lint gate.

### Deferrals

| Item | Owner |
|------|-------|
| Per-route OG image assets | Mission 28 or post-launch |
| Prod screenshot re-capture (`capture-screenshots.mjs`) | After deploy — hero copy changed |
| `auth-journey` fullstack in CI | Mission 26 waiver (unchanged) |

### Spot check (docs)

Rotated from a11y → **docs**: verified `27_voice_guide.md` sweep table matches shipped files; `seo.test.ts` guards sitemap/robots overlap; `landing-content.test.ts` asserts §17 one-liner.

### Gate summary

**Local (py 3.12, infra on `:5434`/`:6381`/`:9010`):**

| Gate | Result |
|------|--------|
| `migrate-check` | Green |
| API `ruff` + `mypy` + `pytest` | 83 passed, 313 skipped |
| Worker `ruff` + `mypy` + `pytest` | 22 passed |
| `test-fixtures` | 23 + pipeline + browser green |
| `test-policy` | 19 passed |
| Web `typecheck`, `lint:strict`, `test`, `build`, `check:motion`, `check:bundles` | 127 tests green |
| `CI=true pnpm test:e2e:marketing` | **71 passed** |

### Deployment decision

**Deploy recommended** — Mission 27 Production Guidance: copy and metadata are low-risk, high-polish. After push: deploy per `docs/runbooks/deploy.md`, `bash scripts/railway-smoke.sh`, fetch production `/` + `/faq` head for JSON-LD, re-capture `docs/screenshots/prod/01-home.png` and legal pages.

---

## Loop after Mission 28 — 2026-06-12

### Re-verification (Mission 28 acceptance criteria)

| Criterion | Result |
|-----------|--------|
| One brand signature on marketing + auth only | **Green** — `BrandSignature` on hero + `auth-brand-panel`; grep shows no other usages |
| Sourced patterns token-native, documented, in budget | **Green** — `28_sourcing_and_microinteractions.md`; bundles 2564 KB / 2650 KB |
| Nav/type scale Linear direction | **Green** — marketing shell `1.0625rem`–`1.125rem` nav, taller header |
| Micro-interactions deliberate + reduced-motion safe | **Green** — Button/Input/Table/Tabs/Skeleton/LIVE/charts; `check:motion` OK |
| Screenshot set + Design Council | **Deferred** — re-capture post-deploy (M28 Production Guidance); Design Council manual |

### Improvements made (this loop)

| Commit | Change |
|--------|--------|
| `854131a` | `BrandSignature` mesh + grid; hero + auth |
| `bd88cfd` | Motion tokens + globals keyframes + skeleton shimmer |
| `8ff7e06` | Border-beam CTAs + stepper connector wiring |
| `07db7df` | Chart draw-in + `usePrefersReducedMotion` |
| `1e7f34c` | Primitive micro-interaction sweep |
| `98badfe` | Marketing nav type scale |
| `9f508b5` | Sourcing doc + architecture + UI-REVIEW themes 1/4 |

### Deferrals

| Item | Owner |
|------|-------|
| Prod + mobile screenshot re-capture | Post-deploy same day as M28 release |
| Design Council ≥18/20 formal score | Mission 30 launch gate |
| Performance trace hero/analytics | Optional — animations are compositor-only (opacity/transform) |

### Spot check (states)

Rotated from docs → **states**: verified `Skeleton` uses `motionSkeleton` (queue/dashboard loading paths inherit via `page-states`); `ContentReveal` + `RunConsoleSkeleton` unchanged but shimmer unified at primitive layer.

### Gate summary

**Local:** `typecheck`, `lint:strict`, `test` **128 passed**, `check:motion`, `check:bundles` (2564 KB), `build`, `CI=true pnpm test:e2e:marketing` **71 passed**.

**Backend:** unchanged by M28 — prior M27 loop gates still valid; full CI on push.

### Deployment decision

**Deploy recommended — single coherent release.** Mission 28 Production Guidance: most visible polish pack deploy. After push: deploy web, `bash scripts/railway-smoke.sh`, re-capture `01-home.png`, `11-login.png`, `22-analytics.png` same day; 5-second hero test on live site.
