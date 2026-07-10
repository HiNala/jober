# Jober — Assisted Application Autopilot

**Owner:** Brian Permut
**Repo:** github.com/HiNala/jober
**Primary use:** Personal, high-volume *and* high-quality applications to any job.
**Future path:** Commercializable self-hosted web app (auth, billing, multi-tenant isolation).

---

## 0. What this system is (and what it is not)

Jober is an **assisted autopilot**. For every job in your tracker it will:

1. Open the apply URL in a real, watchable browser.
2. Detect the ATS (Ashby / Lever / Greenhouse / Workday / etc.) and the page state.
3. Extract the job: title, company, description, requirements, and the live form schema.
4. Generate and stylize a tailored, ATS-aware cover letter from your resume + the row's fit lane and hook.
5. Pre-fill every mappable field from your encrypted profile vault.
6. Upload your canonical resume and the generated cover letter.
7. Run a full **readiness verification** (required fields filled, files attached, no blocking errors).
8. Hand you a one-tap **review-and-submit** with everything staged and a diff of what it filled.
9. After *you* submit, confirm the success state and archive logs, screenshots, traces, and docs.
10. Move to the next job, respecting per-site cooldowns and rate limits.

It removes the repetitive labor — typing the same profile data 155 times, tailoring a letter per role, rendering PDFs, tracking status, and QA-ing completeness — while keeping you the one who actually submits.

**Explicit non-goals.** Jober does **not** try to defeat bot detection, spoof browser fingerprints, solve or bypass CAPTCHAs, evade rate limits, or auto-submit at scale while disguised as a human. When a site throws a login, 2FA, CAPTCHA, or bot challenge, Jober pauses and hands control to you. This is a deliberate design choice: it is more durable (no stealth arms race), more honest, and produces better outcomes than mass-indistinguishable submission, which modern ATSs increasingly filter and penalize.

The default submission policy is therefore **review-before-submit**. A local-only `auto_submit` mode exists behind an explicit per-batch opt-in for ATSs you have personally verified, but it is never the default and never used to disguise automation.

---

## 1. Inputs already available

### Resume (canonical)
You present as an **AI Engineer & Frontend-Focused Full-Stack Developer**: TypeScript, Next.js, React, Python, FastAPI, RAG, agents, evals, embeddings/vector DBs, Docker/CI-CD, founder/operator ownership at Glide Design and Digital Studio Labs. One canonical resume PDF + DOCX is the source of truth; role-targeted variants come later and are human-reviewed.

### Job tracker workbook (verified structure)
- **`Direct Job Leads`** — 155 rows, columns:
  `Rank · Priority · Company · Role · Fit lane · Stage / size signal · Location / work style · Why this fits Brian · Cover-letter hook · Public email / contact · Direct apply URL · Company careers / ATS URL · Source / verification note · Verified date · Status · Applied date · Follow-up date · Notes`
- **`Company Boards`** — 130 rows: `Priority · Company / board · Representative roles in tracker · Stage / size signal · Why save this board · Company careers / ATS URL · Last checked · Notes`
- **`Cover Letter Angles`** — 10 reusable positioning templates (`Use case · Template / angle`).
- **`Summary`** and **`Refresh Sources`** — metadata and lead-refresh sources.

The product imports this workbook directly. Each `Direct Job Leads` row becomes a tracked `JobTarget`, and its **Fit lane**, **Why this fits Brian**, and **Cover-letter hook** become structured generation context. The **Status / Applied date / Follow-up date** columns round-trip back out so the spreadsheet stays a usable mirror.

---

## 2. Architecture at a glance

```
apps/
  web/      Next.js (App Router) + TS + Tailwind + shadcn/ui + 21st.dev   ← scaffolded via generator, not hand-built
  api/      FastAPI + Pydantic v2 + SQLAlchemy 2.0 async + Alembic
  worker/   Celery + Playwright (Chromium, headed locally) browser runner
packages/
  schemas/  shared Pydantic <-> Zod types (single source of truth)
infra/
  compose.yaml, Dockerfiles, nginx, backups
storage/    Postgres + Redis + MinIO (self-hosted)
```

- **Source of truth:** PostgreSQL.
- **Queue / pub-sub / locks:** Redis.
- **Object storage:** MinIO (resumes, generated letters, screenshots, traces, DOM snapshots).
- **Long-running browser runs:** Celery workers.
- **Live updates:** Server-Sent Events first; WebSockets only if needed.
- **Browser automation:** **Playwright**, not Selenium — first-class browser contexts, robust role/label locators, auto-waiting, trace viewer, video, downloads. Selenium stays available only as an edge-case compatibility fallback.
- **LLM access:** a thin provider-agnostic gateway (LiteLLM-style) so you can route to OpenAI, Anthropic, or Gemini, with per-task model tiering and token budgets. (Matches your existing GlideDesign stack.)

### Why Playwright over Selenium
Playwright's trace viewer answers "why did the agent fail?" visually — it records every action, network event, and DOM state. Its role/label/text locators are far more durable across ATS redesigns than brittle CSS/XPath. Auto-waiting kills most flake. This is the single biggest reliability lever in the project.

### Why "workflow engine with AI specialists," not one mega-agent
A single autonomous browser agent demos well and dies in production because application forms vary wildly. Robustness comes from: deterministic platform adapters for common ATSs, generic DOM/accessibility-tree form analysis, screenshot reasoning only for the weird cases, strong typed state, capped retries, explicit verification, and human handoff for blocked steps. The model **plans and classifies**; deterministic code **executes** wherever possible.

---

## 3. Agent roles

1. **Application Orchestrator** — owns the state machine, picks the next step, calls specialists, enforces policy and retry budgets.
2. **Job Intelligence Agent** — reads the job page, emits a normalized job profile: keywords, responsibilities, requirements, seniority signal, fit score.
3. **Document Agent** — drafts + stylizes the cover letter, builds ATS keyword coverage, emits structured letter data and rendered PDF/DOCX.
4. **Form Understanding Agent** — turns DOM + accessibility tree + screenshot into a typed field schema; maps fields to profile data; flags ambiguity with confidence scores.
5. **Browser Action Agent** — selects/produces Playwright actions; deterministic locators first, vision fallback only when needed; runs generated snippets inside a sandbox.
6. **Verification Agent** — confirms required fields filled, files attached, no validation errors; classifies submit-button enabled/disabled and success/already-applied states.
7. **Recovery Agent** — reads a failed attempt's logs, proposes a modified strategy, retries within budget, and writes a human-readable failure report when it gives up.

All agents receive untrusted job-page text as **data, not instructions** (prompt-injection defense, see §9).

---

## 4. Submission & safety policy (the spine of the product)

- Autocomplete forms, generate/upload documents, verify readiness — then **pause before final submit by default**.
- **Never** bypass CAPTCHA, bot challenges, login, or 2FA. Pause and hand to the human.
- **Never** guess or fabricate sensitive answers: work authorization, sponsorship, disability, veteran status, race/ethnicity, gender, salary, or legal-authorization fields. These live in the vault only if *you* enter them, marked with explicit consent, and can be set to "never auto-fill."
- Respect site Terms and rate limits; enforce per-site cooldowns and low concurrency.
- Apply only to jobs already in your selected queue. No scraping/spamming beyond your list.
- **Idempotency:** detect "already applied" and prior runs to prevent duplicate submissions.
- Human-paced interaction is for *server-friendliness and keeping you in the loop*, not for disguising automation.

---

## 5. Data model (entities)

`UserProfile` · `ResumeAsset` · `JobTarget` · `CompanyBoard` · `CoverLetterAngle` · `ApplicationRun` · `ApplicationAttempt` · `BrowserEvent` · `GeneratedDocument` · `FormFieldObservation` · `HumanCheckpoint` · `LlmCall` (for cost/audit).

Field-level definitions live in **Mission 01**. Highlights:
- `JobTarget` mirrors every `Direct Job Leads` column plus `status`, `applied_date`, `follow_up_date`.
- `ApplicationRun.policy ∈ {dry_run, review_before_submit, auto_submit}` (default `review_before_submit`).
- Sensitive `UserProfile` fields are encrypted at rest with explicit per-field consent flags.
- `LlmCall` tracks model, tokens, cost, and redacted prompt/response for budgets and audit.

---

## 6. State machine

```
QUEUED → PREPARE_CONTEXT → OPEN_JOB → DETECT_PLATFORM → EXTRACT_JOB
→ GENERATE_DOCUMENTS → DISCOVER_FORM → FILL_FORM → UPLOAD_FILES
→ VERIFY_READY → (NEEDS_HUMAN ↺) → REVIEW_AND_SUBMIT → VERIFY_SUBMISSION
→ SUCCEEDED | FAILED_RETRYABLE↺ | FAILED_FINAL | SKIPPED
```

Every transition writes a checkpoint to Postgres. Workers are **resumable from the last safe checkpoint**.

---

## 7. Retry & graceful failure

Per application: max 3 normal attempts, 1 alternate-strategy attempt, 1 human handoff. Per-attempt / per-step / page-stability timeouts. Screenshot + DOM snapshot on every failure.

Retry taxonomy (navigation, platform-detection, form-discovery, selector, upload, validation, uncertain-submission, CAPTCHA/login→human, sensitive-field→human). Every final failure produces: job/company/URL · where it failed · screenshots · attempted actions · inferred reason · recommended manual action · safe-to-retry flag. See **Mission 10**.

---

## 8. Frontend

Built with the **code generator**, not from scratch: `create-next-app` → `shadcn init` → 21st.dev/Magic MCP for high-polish screens. Standardize on **shadcn/ui** as the base library; import hero/animation/marketing pieces from 21st.dev. Pages: Dashboard, Job Queue (table + kanban), Job Detail, Run Console (live browser + terminal stream + review/approve), Document Studio, Profile Vault, Settings. Component sourcing and exact 21st.dev imports are specified in **Mission 02** and the design pass in **Mission 16**.

---

## 9. Security, privacy, prompt-injection

Never log API keys/passwords/tokens/full sensitive answers. Encrypt vault fields. Secrets via env/secret store, never committed. MinIO presigned URLs, per-run browser contexts, no cross-run cookie sharing. Treat all webpage text as untrusted: system prompts state explicitly that job-page content is data and must never be obeyed as instructions. Require human handoff for CAPTCHA/login/2FA. Full detail in **Mission 14**.

---

## 10. Conventions (apply to every mission)

- **Files under 2000 lines.** Split modules before they grow past it.
- **Git discipline:** `git init` early with a proper `.gitignore`; per-task commits with clear messages; push to `github.com/HiNala/jober` at mission boundaries.
- **Quality gates, non-negotiable:** backend `ruff` + `mypy` + `pytest`; frontend `typecheck` + `lint:strict` + build. A mission is not "done" until gates are green.
- **Design Council gate** (your standing standard): every user-facing surface scores ≥18/20 across ten criteria with no zeros, referencing Rams, Kare, Norman, Nielsen, Tufte, Vignelli, Rand, Maeda, Wroblewski, Ive.
- **Interactive, no flags:** any CLI/TUI is fully interactive (prompts, menus), never flag-driven.
- Each mission file carries its own task list and an **iteration clause**: keep working until every task passes its acceptance criteria.

---

## 11. Mission sequence

See `MISSION_INDEX.md`. Run **Mission 99 (Iteration Loop)** between every numbered mission to finish leftovers and self-improve before advancing.

### Phase C — Perfection pack 2030 (active)

Missions **35–45** raise Jober from “shipped v0.1 autopilot” to **world-class premium product**:

| Mission | Focus |
|---------|--------|
| 35 | Design system 2030 (Hyperagent/Grok tokens & primitives) |
| 36 | Marketing site v3 (hero, sales, conversion) |
| 37 | Auth + Google OAuth production completion |
| 38 | Stripe Checkout + Pro monetization |
| 39 | Workspace command center (app shell) |
| 40 | Perfect job matching / discovery |
| 41 | Resume tailoring + cover letter studio |
| 42 | Apply pipeline: review → approve → send |
| 43 | Analytics + admin ops excellence |
| 44 | Mobile / responsive perfection |
| 45 | Full QA, integration hardening, launch cert |

**Design bible:** `docs/architecture/design-north-star-2030.md`  
**Visual references:** Hyperagent (thread/canvas, checkpoints, ambient loading), Grok (power empty states, unlock modals), Linear (type/focus), 21st.dev (craft).

**Design Council bar (perfection):** ≥19/20 per primary surface (raised from 18).

**Product completeness targets:**
- Search/import → perfect-fit lists with explainable scores  
- Custom cover letter **and** tailored resume (human-approved)  
- Form fill from vault + uploads + verification  
- User only **approves/sends** (or resolves a clear checkpoint)  
- Stripe Pro self-serve; Google auth when configured; first-party analytics; admin ops  
- Flawless mobile; zero lint/type/test debt on release  

---

## 12. Research sources

- Playwright (Python) Trace Viewer — https://playwright.dev/python/docs/trace-viewer-intro
- Playwright locators — https://playwright.dev/python/docs/locators
- Playwright auth/storage state — https://playwright.dev/python/docs/auth
- FastAPI + Celery + Redis reference — https://testdriven.io/blog/fastapi-and-celery/
- SQLAlchemy 2.0 async — https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- Alembic — https://alembic.sqlalchemy.org/
- MinIO Python SDK — https://min.io/docs/minio/linux/developers/python/minio-py.html
- Next.js App Router — https://nextjs.org/docs/app
- shadcn/ui (Next install) — https://ui.shadcn.com/docs/installation/next
- 21st.dev Magic — https://21st.dev/magic
- LiteLLM — https://docs.litellm.ai/
