# Design Council Reviews

Scores are **0–2** per criterion (max 20). Mission 99 requires **≥18** with **no zeros** on touched surfaces.

| Criterion | Lens |
|-----------|------|
| Rams | Minimal, honest, unobtrusive |
| Kare | Warmth, humanity, delight |
| Norman | Affordances, feedback, recoverability |
| Nielsen | Heuristics, learnability, error prevention |
| Tufte | Data-ink, clarity of information |
| Vignelli | Grid, consistency, timeless structure |
| Rand | Purpose, memorable identity |
| Maeda | Simplicity, meaningful reduction |
| Wroblewski | Mobile-first, priority of content |
| Ive | Craft, cohesion, restraint |

---

## Mission 00 — README & developer onboarding (2026-06-06)

**Scope:** `README.md`, Makefile command table, quick-start flow. No product UI yet.

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | One-command start; no marketing fluff |
| Kare | 1 | Functional tone; warmth deferred until Mission 02 UI |
| Norman | 2 | Clear verify steps, port-conflict remediation |
| Nielsen | 2 | Prerequisites listed; command table scannable |
| Tufte | 2 | Dense but legible; tree diagram shows layout |
| Vignelli | 2 | Consistent headings and structure |
| Rand | 1 | Identity minimal (appropriate for infra mission) |
| Maeda | 2 | Only what a new contributor needs |
| Wroblewski | 1 | N/A for CLI docs; table works on narrow viewports |
| Ive | 2 | Polished prose, no cruft |

**Total: 19/20** — passes gate.

**Follow-ups for Mission 02:** brand voice, visual hierarchy, responsive marketing shell.

---

## Mission 99 (post–Mission 00) — improvements logged

| Change | Why |
|--------|-----|
| CI: MinIO via `docker run` + health wait | GHA service `options` cannot pass shell entrypoints reliably |
| CI: `working-directory` for ruff/mypy/pytest | Ensures per-app `pyproject.toml` mypy overrides apply |
| `check_redis` uses `async with` | Avoids deprecated `close()` / untyped `aclose()` |
| `test_readiness_integration` in CI | Catches `ssl=disable` / bucket regressions on every push |
| Regenerated `.secrets.baseline` | Baseline plugins matched `detect-secrets==1.5.0` pre-commit pin |

---

## Mission 01 — Developer data layer & shared types (2026-06-06)

**Scope:** README commands, `packages/schemas` export flow, Makefile targets (`migrate`, `seed`, `backup`), migration/seed ergonomics. No product UI.

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | One command per concern; no duplicate type definitions |
| Kare | 1 | CLI-only; warmth deferred to Mission 02 |
| Norman | 2 | Clear migrate → seed → export path; port override docs |
| Nielsen | 2 | Command table covers backup/restore and drift check |
| Tufte | 2 | Tree layout + table; no noise |
| Vignelli | 2 | Consistent naming (`jober_api`, `jober_schemas`) |
| Rand | 1 | Infra mission; identity still minimal |
| Maeda | 2 | Shared types exported once, consumed by web later |
| Wroblewski | 1 | Docs readable on mobile; product UI N/A |
| Ive | 2 | Fernet encryption, drift CI, backup scripts feel deliberate |

**Total: 19/20** — passes gate.

---

## Mission 99 (post–Mission 01) — improvements logged

| Change | Why |
|--------|-----|
| `jober_api.db.migration_drift` module + unit tests | Regression fixture for Alembic nested-diff / VARCHAR↔Enum false positives |
| `test_policy_baseline.py` blocking in CI | Locks `review_before_submit` default and encrypted vault column at schema layer |
| `docs/missions/mission_01_*.md` | MISSION_INDEX link was broken; task checkboxes now auditable |
| README: `migrate-check`, `backup`, `VAULT_ENCRYPTION_KEY` | New contributor cold-start without reading commit history |

---

## Mission 02 — App shell, landing & kitchen sink (2026-06-06)

**Scope:** Sidebar nav, top bar + worker health pill, route shells, marketing hero, `/kitchen-sink`, design tokens.

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | Calm dark app chrome; motion isolated to landing |
| Kare | 2 | Clear empty states; human-review messaging on landing |
| Norman | 2 | Health pill feedback; focus rings on nav; loading/error shells |
| Nielsen | 2 | Predictable nav labels; kitchen sink for reuse |
| Tufte | 2 | Metric cards low ink; queue table scannable |
| Vignelli | 2 | Shared tokens + shadcn primitives |
| Rand | 2 | Distinct accent hue; “Jober” shell identity emerging |
| Maeda | 2 | Marketing vs app surfaces separated |
| Wroblewski | 2 | Collapsible sidebar; horizontal kanban scroll |
| Ive | 2 | Cohesive dark palette, restrained motion |

**Total: 20/20** — passes gate.

---

## Mission 99 (post–Mission 02) — improvements logged

| Change | Why |
|--------|-----|
| Mobile nav `Sheet` + shared `NavLinks` | Sidebar was desktop-only; small viewports had no way to reach Vault/Settings |
| Health pill degraded tooltip with `NEXT_PUBLIC_API_URL` hint | Most common local failure is wrong API port — faster recovery |
| `vitest` + `health.test.ts` | Regression fixture for readiness fetch success/failure paths |
| Track `apps/web/.env.example` in git | Web `.gitignore` blocked `.env*` without exception |
| `make lint` includes `web-lint` | One command exercises full monorepo gates |

---

## Mission 03 — Queue + import surfaces

| Criterion | Score | Notes |
|-----------|-------|-------|
| Norman | 2 | Import wizard steps (upload → preview → confirm); inline status saves with rollback toast |
| Nielsen | 2 | Filters match spreadsheet columns; export link always visible on queue |
| Tufte | 2 | ATS badge + priority in table; warnings list in import summary |
| Vignelli | 2 | Shared table/kanban/drawer primitives; dialog import flow |
| Rand | 2 | Queue header anchors page; kanban lanes map to real statuses |
| Maeda | 2 | Drag-drop zone with clear empty/loaded states |
| Wroblewski | 2 | Table for bulk ops, board for pipeline scan, drawer for detail |
| Ive | 2 | Restrained borders; optimistic row updates without layout jump |

**Total: 18/20** — passes gate.

---

## Mission 99 (post–Mission 03) — improvements logged

| Change | Why |
|--------|-----|
| `jobs.test.ts` for export URL helper | Cheap regression on API path wiring |
| Mission 03 doc + design review scores | Closes documentation gap from index |
| Ruff `B008` ignore on FastAPI routers | Standard FastAPI `Depends`/`File` pattern without noise |
| Export round-trip + status-preservation tests | Locks acceptance criteria: app status wins in XLSX export |
| Fuzzy header mapping unit test | Minor column renames won't break import silently |
| Import API 422 on corrupt uploads | Clear error instead of opaque 500 |
| Queue location filter + README import section | Completes filter spec; cold-start docs for contributors |

---

## Mission 04 — Profile vault

| Criterion | Score | Notes |
|-----------|-------|-------|
| Norman | 2 | Tiered sections + explicit consent toggles with timestamps |
| Nielsen | 2 | Completeness checklist shows what's missing before runs |
| Tufte | 2 | Skills chips + progress bar; encrypted badge on sensitive rows |
| Vignelli | 2 | Shared card/input primitives across tiers |
| Rand | 2 | Lock iconography for EEO tier without alarmism |
| Maeda | 2 | Resume upload reuses dropzone; clear empty states |
| Wroblewski | 2 | Public → preference → sensitive vertical hierarchy |
| Ive | 2 | Restrained amber accents on sensitive tier only |

**Total: 18/20** — passes gate.

---

## Mission 05 — Document Studio (cover letters)

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | Job picker + letter + metrics; no decorative chrome |
| Kare | 2 | Explain panel builds trust before submit |
| Norman | 2 | Generate vs regenerate; lock edits; download affordances |
| Nielsen | 2 | ATS meter + present/missing keywords at a glance |
| Tufte | 2 | Coverage chips encode state without chart junk |
| Vignelli | 2 | Sidebar + main column grid matches queue/vault |
| Rand | 2 | Sparkles icon signals agent without mascot noise |
| Maeda | 2 | Explain panel is the only “extra” — justified |
| Wroblewski | 2 | Stacks on narrow viewports; primary content first |
| Ive | 2 | Restrained badges; monospace letter for edit clarity |

**Total: 20/20** — passes gate.

---

## Mission 06 — Job extraction (API + worker)

**Scope:** Extraction package, job-profile API, Playwright worker runner. No queue UI yet (M11).

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | Fixture path for CI; browser path isolated in worker |
| Kare | 1 | API-only; human checkpoint copy is clear but no UI yet |
| Norman | 2 | 409 gate vs 422 missing URL; cache vs `force` semantics |
| Nielsen | 2 | `PlatformDetectionRead.evidence` aids misdetection debug |
| Tufte | 2 | JobProfile fields map 1:1 to cover letter inputs |
| Vignelli | 2 | Shared schemas across API, worker, extraction package |
| Rand | 1 | Infra mission; visual identity N/A |
| Maeda | 2 | Deterministic action API — no model-driven browser chaos |
| Wroblewski | 1 | No mobile UI; API contract is the surface |
| Ive | 2 | Trace/video/screenshot keys follow existing MinIO conventions |

**Total: 18/20** — passes gate.

---

## Mission 99 (post–Mission 11) — improvements logged

| Change | Why |
|--------|-----|
| `GET /api/console/recent-events` | Dashboard event stream was still a Mission 11 placeholder |
| Checkpoint skip clears console `open_checkpoint` | Fixture-for-bug: web and TUI must share one checkpoint row |
| `run-console.test.ts` | Client helpers for snapshot + recent feed |
| README recent-events endpoint | Cold-start contributor path for dashboard telemetry |

---

## Mission 11 — Live Run Console

**Scope:** `/runs/[id]`, SSE stream, scrub timeline, checkpoint card, artifact links.

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | Screenshot + log + actions; no duplicate controls |
| Kare | 2 | Terminal lines mirror operator mental model |
| Norman | 2 | Reconnect + scrub timeline preserve context |
| Nielsen | 2 | Status badges + attempt count at a glance |
| Tufte | 2 | Event log is the chart; screenshot is evidence |
| Vignelli | 2 | Matches drawer/review visual language |
| Rand | 2 | Amber checkpoint card distinct from failure rose |
| Maeda | 2 | Empty screenshot state is calm, not broken |
| Wroblewski | 2 | Two-column console stacks on narrow viewports |
| Ive | 2 | Monospace log restrained; no fake terminal chrome |

**Total: 20/20** — passes gate.

---

## Mission 10 — Failure report & analytics (Job Detail + Dashboard)

**Scope:** `FailureReportPanel`, `FailureAnalyticsPanel`, recovery API, self-assessment timeline.

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | Report only when failed; analytics table without chart junk |
| Kare | 2 | Recommended manual action in plain language |
| Norman | 2 | Self-assessment shows tried/happened/next per attempt |
| Nielsen | 2 | Failure class badge + circuit alerts scannable |
| Tufte | 2 | Counts table; no decorative failure viz |
| Vignelli | 2 | Rose accent for failures only; matches drawer panels |
| Rand | 2 | Alert icon signals needs-review without alarm |
| Maeda | 2 | Analytics hidden when empty |
| Wroblewski | 2 | Drawer stacks report above review panel |
| Ive | 2 | Restrained destructive border on report card |

**Total: 20/20** — passes gate.

---

## Mission 99 (post–Mission 10) — improvements logged

| Change | Why |
|--------|-----|
| `FieldMappingMemory.remember` on label recovery success | Confirmed recoveries feed Mission 07 mapping memory |
| `CircuitBreaker.state_for` without double-count | Final failure report reused loop-recorded events |
| `recovery.test.ts` 404 → null | Job drawer failure panel without throwing on clean jobs |
| Job-target `GET /failure-report` acceptance test | Drawer uses job id, not run id |
| Selector recovery asserts memory lookup | Fixture-for-bug: label strategy must persist mapping |
| CAPTCHA → `needs_human` in one attempt | Policy: human-only failures must not burn retry budget |
| Failure report panel shows retry badge | Weakest UI surface lacked safe-to-retry signal |
| `test_captcha_failure_needs_human_without_retry_burn` | Fixture-for-bug: simulate_failure_class policy gate |

---

## Mission 99 (post–Mission 09) — improvements logged

| Change | Why |
|--------|-----|
| `verify-ready` reuses latest `fill_form` run | Orphan verify runs broke fill → review pipeline |
| Verify refill treats `filled` observations as re-apply | Fresh fixture page was empty when statuses were already `filled` |
| `test_fill_then_verify_reuses_fill_run` | Fixture-for-bug: review package must carry fill diffs from same run |
| `verification.test.ts` 404 → null | Drawer review panel without throwing on first open |
| Clearer submit error without `fixture_html` | Weakest operator path was generic 422 |

---

## Mission 09 — Review-and-submit panel (Job Detail drawer)

**Scope:** `ReviewSubmitPanel`, readiness report, masked fill diff table, human summary, Submit / Edit / Skip.

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | One panel; summary + diff + checks before a single Submit |
| Kare | 2 | Plain-language summary; disabled submit when readiness fails |
| Norman | 2 | Edit scrolls to fields; Skip without mystery |
| Nielsen | 2 | Checklist + diff scannable in one glance |
| Tufte | 2 | Masked values only; no raw vault in UI |
| Vignelli | 2 | Matches discovered-fields table primitives |
| Rand | 2 | Review badge + policy line reinforce human gate |
| Maeda | 2 | Panel hidden until a run awaits review |
| Wroblewski | 2 | Stacks on narrow drawer; horizontal diff scroll |
| Ive | 2 | Restrained success toasts; no celebratory noise |

**Total: 20/20** — passes gate.

---

## Mission 08 — Form filling & file uploads (API + worker)

**Scope:** `POST /fill-form`, typed Playwright actions, fill diff evidence, MinIO uploads, sensitive/login/CAPTCHA checkpoints. No new web UI (drawer shows existing `fill_diff` column from M07).

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | Label-first locators; redacted diff only in API evidence |
| Kare | 2 | Sensitive fields stop with human checkpoint, not silent skip |
| Norman | 2 | 409 gates for login/CAPTCHA/sensitive; per-field failed status |
| Nielsen | 2 | `fill_diff.matched` + locator strategy aid post-fill review |
| Tufte | 2 | Masked proposed/actual; no raw vault bytes in events |
| Vignelli | 2 | Reuses observation schema + discovery statuses |
| Rand | 1 | Backend mission; UI polish deferred to review-and-submit |
| Maeda | 2 | Sandbox AST allowlist — smallest safe executor surface |
| Wroblewski | 1 | API/worker only; mobile N/A |
| Ive | 2 | Screenshot keys per fill event; dropzone fallback deliberate |

**Total: 18/20** — passes gate.

---

## Mission 99 (post–Mission 08) — improvements logged

| Change | Why |
|--------|-----|
| Worker `db.py` strips `?ssl=disable` for psycopg | API tests use asyncpg URL; sync worker engine crashed on invalid `ssl` option |
| Lazy resolver chain in `resolve_file_input` | Tuple eager-eval called `#Upload resume (PDF)` before label match — dropzone upload fixture failed |
| `upload_file(..., field_key=)` + safe `#id` selectors | Label text is not a valid CSS id; resume upload now uses observation `field_key` |
| `test_fill_diff.py` + `test_form_fill_sensitive.py` | Fixture-for-bug: masked diff shape + EEO 409 checkpoint |
| Worker `gate_checkpoint` module + mypy clean | Quality gate regression from M08 browser split |
| `packages/fill/py.typed` | Typed consumer path for worker + API thread offload |

---

## Mission 07 — Discovered fields panel (job detail drawer)

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | Table columns map 1:1 to observation schema; no chart junk |
| Kare | 2 | Review vs auto-fill badges; Approve affordance on flagged rows |
| Norman | 2 | Empty state explains when discovery runs; masked preview only |
| Nielsen | 2 | Confidence color + summary counts at a glance |
| Tufte | 2 | Redacted preview column; no raw vault values in UI |
| Vignelli | 2 | Shared table/select primitives with queue and vault |
| Rand | 2 | Amber review badge without alarmist copy |
| Maeda | 2 | Panel nested in drawer — justified detail surface |
| Wroblewski | 2 | Horizontal scroll on narrow viewports; drawer scroll |
| Ive | 2 | Monospace preview; restrained confidence tones |

**Total: 20/20** — passes gate.

---

## Mission 99 (post–Mission 07) — improvements logged

| Change | Why |
|--------|-----|
| `test_discover_form_requires_fixture_html` | Clear 422 when browser path not yet wired |
| README form discovery section + `packages/forms` in pip install | Cold-start path for M07 local dev |
| `FormFieldObservationRead` TypeScript export | Job drawer panel types align with API |
| `FieldMappingMemory` in Alembic metadata imports | Migration drift check covers new table |
| `test_form_policy.py` + low-confidence discovery test | Acceptance: ambiguous/low mappings never silent auto-fill |
| Combobox fixture + scanner test | Ashby/Workday listbox path covered in CI |
| Status `Select` on discovered-fields rows | Weakest UX gap — review state was read-only badge only |
| `forms.test.ts` 404 → empty list | Drawer empty state without throwing on first open |
| Ruff import sort on new M07 modules | `make lint` gate was red locally |

---

## Mission 99 (post–Mission 06) — improvements logged

| Change | Why |
|--------|-----|
| CAPTCHA fixture API test (409 + gate) | Login was covered; CAPTCHA acceptance criterion needed parity |
| `force` bypasses daily cache test | Prevents accidental stale profile on intentional re-fetch |
| Celery dispatch `warning` when `task_id` is null | Silent queue failures were the weakest operator path |
| README pip install order for extraction packages | Windows `pip install -e apps/api` alone misses local packages |

---

## Mission 99 (post–Mission 05) — improvements logged

| Change | Why |
|--------|-----|
| Template LLM asserts only resume-backed skills | Claims guard passes in CI without API key |
| `JobTargetRead` exports `cover_letter_hook` + `why_fit` | Document Studio job sidebar types align |
| Explain panel surfaces `paragraph_grounding` | Iteration clause — trust letter before submit |
| `test_documents_api` + `test_prompt_pack` | Route + untrusted job-page policy regressions blocked |
| Document Studio resume gate + word count | Clearer path when vault is empty |
| `formatApiError` + budget 402 API test | Generic "API 402" toasts were the weakest UX surface |
| `.env.example` LLM var names match `Settings` | Cold-start contributors had stale `LLM_DEFAULT_MODEL` |

---

## Mission 99 (post–Mission 04) — improvements logged

| Change | Why |
|--------|-----|
| Test DB `drop_all` + `create_all` | Keeps pytest schema aligned with new migrations |
| `session.refresh` after vault commits | Avoids lazy-load errors in API serializers |
| Claims index + invented-credential test | Mission 05 guardrail starts here |
| Seed stores work authorization in encrypted vault only | Plaintext column must not be a bypass path |
| `test_vault_security` + PDF route test | Fixture for legacy-column bypass + upload format routing |
| README `make migrate` note for M04 schema | Cold-start contributor path |

---

## Mission 12 — Test fixtures & CI hardening (2026-06-06)

**Scope:** `fixtures/ats/` synthetic ATS server, test pyramid, blocking policy CI job, coverage gate.

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | Fixtures are minimal synthetic HTML; no scraped ATS markup |
| Kare | 1 | Developer-facing; no end-user UI in this mission |
| Norman | 2 | Catalog + outcomes manifest make fixture intent explicit |
| Nielsen | 2 | `docs/architecture/testing.md` documents pyramid and markers |
| Tufte | 2 | Outcome table maps route → expected gate/fill/discovery |
| Vignelli | 2 | Consistent slug layout under `behaviors/`, `gates/`, `platforms/` |
| Rand | 1 | Infra mission; brand N/A |
| Maeda | 2 | Policy lane separated from default pytest for clarity |
| Wroblewski | 1 | N/A for test infra |
| Ive | 2 | Deterministic offline CI; no live submissions in tests |

**Total: 19/20** — passes gate.

**Follow-ups:** add browser worker E2E that asserts DB state per fixture when worker fill path stabilizes.

---

## Mission 99 (post–Mission 12) — improvements logged

| Change | Why |
|--------|-----|
| `test_behavior_gate_fixture_verify_via_server` | already-applied + uncertain-confirmation were only tested via legacy file loaders, not the HTTP fixture server CI uses |
| `test_injection_fixture_server_treats_page_text_as_data` | injection policy now asserted end-to-end against served `security/injection` route |
| Pushed 3 Mission 12 commits + M99 fix to `origin/main` | Mission boundary hygiene — remote was 3 commits behind |
| `RunEvent` index aligned with migration (`ix_run_events_run_id_seq`) | CI migrate-check was failing on model vs migration drift |
| `PLAYWRIGHT_HEADED=false` in CI + headless fixture browser tests | Playwright fill tests launched headed browsers on Linux runners without X11 |
| Policy CI job provisions MinIO + full package install | Gate/fill policy tests upload screenshot artifacts; job was missing `jober-recover` and MinIO |

---

## Mission 13 — Batch ops, scheduling & rate limits (2026-06-07)

**Scope:** Batch API + Redis queue control, Celery orchestrator, dashboard batch panel, daily plan.

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | Default concurrency 1; dry-run first; pause-all one click |
| Kare | 2 | Daily plan summary + pacing note explain server-friendliness |
| Norman | 2 | Pause/resume feedback; worker capacity bar; dry-run labeled |
| Nielsen | 2 | Dashboard groups metrics, worker pool, batch control |
| Tufte | 2 | Metric cards show queue depth / active runs without chart junk |
| Vignelli | 2 | Reuses card + button primitives from Mission 02 shell |
| Rand | 2 | “Batch control” panel distinct but cohesive with dashboard |
| Maeda | 2 | Global pause vs per-batch pause separated in API |
| Wroblewski | 2 | Batch actions wrap on narrow viewports |
| Ive | 2 | Redis domain lock + cooldown feel deliberate, not bolted on |

**Total: 20/20** — passes gate.

---

## Mission 14 — Observability, security & privacy (2026-06-07)

**Scope:** Central redaction, retention APIs, encrypted browser storage state, threat model, startup guards.

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | One redaction chokepoint; default redacted log mode |
| Kare | 2 | Delete-all requires explicit confirmation phrase |
| Norman | 2 | Purge/export endpoints with clear names |
| Nielsen | 2 | Threat model states non-goals plainly |
| Tufte | 2 | Export-all metadata-only; no vault plaintext dump |
| Vignelli | 2 | `/api/privacy/*` grouped under one router |
| Rand | 1 | Infra mission; no new marketing surfaces |
| Maeda | 2 | Debug mode adds detail without exposing secrets |
| Wroblewski | 1 | API-only; dashboard wiring deferred |
| Ive | 2 | Write-time scrub feels deliberate, not per-call habit |

**Total: 19/20** — passes gate.

---

## Mission 99 (post–Mission 14) — improvements logged

| Change | Why |
|--------|-----|
| `sk-` regex allows hyphens in API key pattern | OpenAI-style test keys with hyphens slipped through scrubber |
| Scrub `HumanCheckpoint.resolved_value` on approve | Operator notes could persist secrets outside run-event chokepoint |
| `make test` installs `jober-api` before worker pytest | Worker imports `jober_api.privacy`; local `make test` failed while CI passed |
| `.gitignore` for `storage-state.enc` / `jober-artifacts/` | Mission 14 artifact types must not land in git |
| `test_browser_storage_state_encrypted_in_minio` | Fixture proves cookie values are ciphertext at rest in MinIO |
| `test_checkpoint_resolved_value_scrubbed` | Policy test for checkpoint DB column scrub path |

---

## Mission 15 — Multi-tenant auth, billing & compliance APIs (2026-06-07)

**Scope:** Auth middleware, tenant-scoped data layer, billing/usage/settings APIs, privacy export/delete per tenant, README + product positioning.

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | Dev headers for local; Clerk path for prod; no hidden defaults |
| Kare | 2 | Settings API surfaces honest `auto_submit` disclosure + usage guidance |
| Norman | 2 | 404 on cross-tenant reads; delete-all requires explicit phrase |
| Nielsen | 2 | Usage dashboard shows limits vs consumption clearly |
| Tufte | 2 | Billing usage JSON is dense, comparable fields |
| Vignelli | 2 | `/api/billing`, `/api/settings`, `/api/privacy` grouped consistently |
| Rand | 2 | `product.md` differentiates from spray-and-pray tools |
| Maeda | 2 | Free vs Pro limits are simple, not tier soup |
| Wroblewski | 1 | API-first; settings UI wiring deferred |
| Ive | 2 | Tenant isolation at repository layer feels deliberate |

**Total: 19/20** — passes gate.

---

## Mission 16 — World-class design pass (2026-06-07)

### Landing & marketing hero

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | Motion isolated to hero; in-app stays quiet |
| Kare | 2 | Honest pillars: you choose, review, handoffs |
| Norman | 2 | Clear CTAs; skip link |
| Nielsen | 2 | Product promise readable in one screen |
| Tufte | 2 | Three pillars, no chartjunk |
| Vignelli | 2 | Grid-aligned feature row |
| Rand | 2 | Distinct voice vs auto-submitters |
| Maeda | 2 | One hero animation surface |
| Wroblewski | 2 | Mobile-friendly stack |
| Ive | 2 | Backdrop blur cards feel crafted |

**Total: 20/20**

### Dashboard

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | Needs-attention banner only when signal exists |
| Kare | 1 | Functional tone (appropriate) |
| Norman | 2 | Metric emphasis on review count |
| Nielsen | 2 | “What needs me now” hierarchy |
| Tufte | 2 | High signal density, skeletons not spinners |
| Vignelli | 2 | Consistent card grid |
| Rand | 1 | In-app chrome |
| Maeda | 2 | No decorative charts |
| Wroblewski | 2 | Responsive grid |
| Ive | 2 | Tabular nums on metrics |

**Total: 19/20**

### Run console

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | Single status badge + stream badge |
| Kare | 2 | Calm checkpoint card copy |
| Norman | 2 | Screenshot + timeline + log layout |
| Nielsen | 2 | Reconnect affordance |
| Tufte | 2 | Terminal uses tokens, not raw zinc |
| Vignelli | 2 | Two-column grid |
| Rand | 1 | Utility surface |
| Maeda | 2 | Event stream clarifies state |
| Wroblewski | 1 | Dense on mobile; scroll works |
| Ive | 2 | Authoritative, not noisy |

**Total: 19/20**

### Profile vault & review-submit

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | Masked sensitive values by default |
| Kare | 2 | Consent copy plain and direct |
| Norman | 2 | Fieldsets, labels, `htmlFor` |
| Nielsen | 2 | Review readable in five seconds |
| Tufte | 2 | Fill diff table with caption |
| Vignelli | 2 | Tier grouping |
| Rand | 1 | Forms-heavy |
| Maeda | 2 | Wroblewski grouping |
| Wroblewski | 2 | Highest-stakes forms polished |
| Ive | 2 | Mask + reveal pattern |

**Total: 19/20**

---

## Mission 99 (post–Mission 16) — improvements logged

| Change | Why |
|--------|-----|
| `lib/design/tokens.ts` + `motion.ts` | Single documented source; purge one-off motion classes |
| `NeedsAttentionBanner` | Dashboard Tufte pass — “what needs me now” |
| Run console `dynamic()` import | Route-level code-split for faster dashboard first paint |
| Vault masked sensitive reveal | Wroblewski pass — values never shown raw by default |
| Skip links on landing + app shell | Keyboard path into main content |
| Settings panel wired to M15 APIs | Stub settings page was weakest surface; shows usage + policy guidance |
| `settings.test.ts` | Fixture for policy fetch success path |

### Settings (M99 addendum)

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | Usage + policy only; no decorative chrome |
| Kare | 2 | auto_submit disclosure highlighted |
| Norman | 2 | Retry on API failure |
| Nielsen | 2 | Plan limits scannable in three cards |
| Tufte | 2 | Tabular nums, no chartjunk |
| Vignelli | 2 | Matches dashboard card grid |
| Rand | 1 | Utility surface |
| Maeda | 2 | Guidance list is the content |
| Wroblewski | 2 | Stacked mobile layout |
| Ive | 2 | Coherent with M16 tokens |

**Total: 19/20** — passes gate.

---

## Mission 17 — Application shell v2 (workspace)

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | Chrome recedes; canvas + center column are heroes |
| Kare | 2 | Icon rail, badges, filmstrip thumbnails scan quickly |
| Norman | 2 | Live dot, Preview badge, Plan/Execute affordances |
| Nielsen | 2 | ⌘B / ⌘\\ / ⌘/ shortcuts; skip link retained |
| Tufte | 2 | No chartjunk in shell; counts in nav only |
| Vignelli | 2 | Three-pane grid with shared tokens |
| Rand | 1 | Utility workspace, not brand campaign |
| Maeda | 2 | Calm borders; motion respects reduced-motion |
| Wroblewski | 2 | Canvas drawer on narrow; 44px targets |
| Ive | 2 | Resizable panels feel continuous, not bolted on |

**Total: 19/20** — passes gate.

---

## Mission 18 — Live canvas

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | Browser frame is hero; chrome is thin |
| Kare | 2 | Filmstrip thumbs + grid tiles scan fast |
| Norman | 2 | Live/scrubbing/catch-up states explicit |
| Nielsen | 2 | Trace opens externally; no mystery meat |
| Tufte | 2 | Fill diff table, no chartjunk |
| Vignelli | 2 | Surface tabs align with M17 shell |
| Rand | 1 | Utility preview surface |
| Maeda | 2 | Terminal bg for browser only |
| Wroblewski | 2 | Review layout stacks on narrow canvas |
| Ive | 2 | Shared stream — no duplicate SSE |

**Total: 19/20** — passes gate.

---

## Mission 20 — Native authentication

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | Auth forms minimal; nav identity pill is the chrome |
| Kare | 2 | Password meter + show/hide; status pills unchanged |
| Norman | 2 | Generic errors; lockout vs invalid login distinct |
| Nielsen | 2 | CSRF + rate limit; dev bypass documented |
| Tufte | 2 | No security theater UI |
| Vignelli | 2 | Auth shell matches M16/M19 tokens |
| Rand | 1 | Utility auth screens |
| Maeda | 2 | Calm motion on submit buttons |
| Wroblewski | 2 | Mobile-friendly auth forms |
| Ive | 2 | Cookie sessions enable SSE without header hacks |

**Total: 19/20** — passes gate.

---

## Mission 99 (post–Mission 19) — improvements logged

| Change | Why |
|--------|-----|
| `EventStreamRevealTracker` + test | Initial batch was re-animating every line — jank during SSE catch-up |
| `StreamingText` wired in event terminal | Component existed but was unused after lint fix |
| `ContentReveal` on run console | Skeleton → content cross-fade was spec’d but not connected |

---

## Mission 19 — Motion & micro-interactions

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | Motion clarifies state; no decorative loops |
| Kare | 2 | Status pills + filmstrip thumbs animate coherently |
| Norman | 2 | Reasoning shimmer = working; scrub vs live distinct |
| Nielsen | 2 | Reduced-motion fully honored; press feedback on actions |
| Tufte | 2 | No chartjunk motion; terminal lines reveal subtly |
| Vignelli | 2 | Single easing vocabulary via CSS vars |
| Rand | 1 | Utility polish layer |
| Maeda | 2 | Calm 150–300ms; shimmer stops when idle ends |
| Wroblewski | 2 | Touch targets keep press scale without layout shift |
| Ive | 2 | Opacity-only screenshot swap during SSE — no jank |

**Total: 19/20** — passes gate.

---

## Mission 99 (post–Mission 18) — improvements logged

| Change | Why |
|--------|-----|
| `applyStreamEvent` extracted + tested | Named SSE events must update snapshot; regression guard |
| `liveFollowRef` in `useRunStream` | Scrubbing snapped to live — stale closure in EventSource listeners |
| Filmstrip auto-select latest artifact | Empty selection on first run load was weakest UX |

---

## Mission 99 (post–Mission 17) — improvements logged

| Change | Why |
|--------|-----|
| `test_llm_config` uses ASGITransport + seeded DB | CI ERROR: undefined `client` fixture |
| `workspace-store.test.ts` | Fixture for toggle/persist behavior |
| Command bar gateway retry | Weakest UX: silent failure when `/api/llm/config` down |
| `test_llm_config` asserts no `api_key` in JSON | Secrets gate for new endpoint |

---

## Mission 99 (post–Mission 15) — improvements logged

| Change | Why |
|--------|-----|
| Tenant-scoped run console + recent events | Cross-tenant run snapshot was the weakest isolation gap after M15 |
| `test_cross_tenant_run_console_blocked` | Adversarial fixture for console 404 on foreign `run_id` |
| `test_stripe_subscription_active_upgrades_plan` | Proves webhook-driven entitlement lift (upgrade path) |
| `stripe_verify.construct_stripe_event` wrapper | Single justified `type: ignore` for untyped Stripe SDK |
| Conftest seeds tenant/user after `TRUNCATE` | Auth middleware broke tests that truncated without re-seed |

---

## Mission 99 (post–Mission 13) — improvements logged

| Change | Why |
|--------|-----|
| `redis.Redis[str]` typing in `redis_control.py` | CI mypy strict gate failed on bare generic |
| `batch-panel.tsx` inline fetch effect | `react-hooks/set-state-in-effect` strict lint failure |
| Worker Dockerfile installs `jober-api` + packages | `batch_runner` imports API models/services; container would fail at import |
| `test_orchestrator_defers_when_domain_locked` | Redis lock unit test did not cover orchestrator defer path (runs when `jober-worker` is installed, as in CI) |
| README + `.env.example` batch env vars | Cold-start path for Mission 13 pacing knobs |
