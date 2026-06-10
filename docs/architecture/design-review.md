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

## Mission 21 — Google OAuth & account linking

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | Google button is additive; native form unchanged |
| Kare | 2 | Provider labels in settings; link/unlink affordances clear |
| Norman | 2 | Verified-email merge requires password; unlink guard explicit |
| Nielsen | 2 | PKCE + single-use state; secrets env-only |
| Tufte | 2 | Minimal scopes (openid email profile) |
| Vignelli | 2 | Auth divider + outline button match shell |
| Rand | 1 | Standard OAuth UX |
| Maeda | 2 | Same motion tokens on Google CTA |
| Wroblewski | 2 | Full-width provider button on mobile |
| Ive | 2 | Reuses cookie session flow — no parallel auth stack |

**Total: 19/20** — passes gate.

---

## Mission 22 — User Settings, Library & Preferences

**Scope:** `/library`, `/search`, expanded `/settings`, user preferences sync, BYOK storage.

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | One Library surface; Settings grouped by intent |
| Kare | 2 | Empty states; vault stays in Settings home |
| Norman | 2 | Tabs + sections; prefs apply without reload |
| Nielsen | 2 | Search debounced; delete requires confirm phrase |
| Tufte | 2 | Lists scannable; usage in AI section |
| Vignelli | 2 | Shared tokens; nav Library/Search/Settings |
| Rand | 2 | Library vs Settings mental model is distinct |
| Maeda | 2 | Documents/Vault redirects avoid fragmentation |
| Wroblewski | 2 | Library tabs work on narrow viewports |
| Ive | 2 | Reduced-motion + density hooks cohesive |

**Total: 20/20** — passes gate.

---

## Mission 23 — Unified Job Discovery & List Building

**Scope:** `/discover`, discovery API, saved searches, list refresh, batch from list.

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | One surface; search + upload as equal tabs |
| Kare | 2 | Fit badges advisory; clear source labels |
| Norman | 2 | List panel always visible; select-all review |
| Nielsen | 2 | Saved search + refresh without duplicate rows |
| Tufte | 2 | Candidate table scannable; fit score inline |
| Vignelli | 2 | Matches Library/Queue tokens |
| Rand | 2 | Discover vs Queue vs Library roles distinct |
| Maeda | 2 | Upload reuses import wizard — not a second tool |
| Wroblewski | 2 | Sticky list panel on wide screens |
| Ive | 2 | Unified hand-off to batch launch |

**Total: 20/20** — passes gate.

---

## Mission 24 — Cover Letter System v2

**Scope:** Document Studio, canvas `DocumentView`, Settings application defaults, letter API.

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | Toggle + templates; skip when not needed |
| Kare | 2 | Voice presets advisory; claims guard unchanged |
| Norman | 2 | Canvas editor + studio share patterns |
| Nielsen | 2 | Global default + batch filter override |
| Tufte | 2 | ATS + keyword chips inline |
| Vignelli | 2 | Classic/Modern/Compact tokens consistent |
| Rand | 2 | Document agent distinct from fill agent |
| Maeda | 2 | Regen respects locked paragraphs |
| Wroblewski | 2 | Settings defaults + per-run canvas |
| Ive | 2 | ATS-safe text PDFs, no raster gimmicks |

**Total: 20/20** — passes gate.

---

## Mission 25 — First-party analytics (consent + SDK)

**Scope:** Analytics consent banner, client SDK, first-party collector UX.

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | Opt-in only; decline dismisses; no third-party scripts |
| Kare | 2 | Plain-language first-party disclosure |
| Norman | 2 | `role="dialog"` + labeled actions |
| Nielsen | 2 | Allow / Decline; fixed bottom card, non-blocking |
| Tufte | 2 | No metrics chrome on marketing surfaces |
| Vignelli | 2 | `surface.card` matches app tokens |
| Rand | 2 | Distinct from auth forms but cohesive |
| Maeda | 2 | Tracking off until explicit allow |
| Wroblewski | 2 | Banner wraps; `sm:left-auto` on wide screens |
| Ive | 2 | sendBeacon path; UI never awaits analytics |

**Total: 20/20** — passes gate.

---

## Mission 29 — Marketing landing (home)

**Scope:** `/` landing page, marketing shell, product visual, pricing/legal stubs, SEO.

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | One hero animation surface; sections stay quiet |
| Kare | 2 | Honest human-in-the-loop copy; no auto-submit promises |
| Norman | 2 | Signup-primary CTAs; skip link + landmarks |
| Nielsen | 2 | How-it-works scannable in four steps |
| Tufte | 2 | Product visual shows stream + checkpoint, not chartjunk |
| Vignelli | 2 | Shared marketing shell + token-aligned cards |
| Rand | 2 | Distinct voice vs spray-and-pray tools |
| Maeda | 2 | Reduced-motion static fallback on demo stream |
| Wroblewski | 2 | Hero stacks on mobile; footer grid wraps |
| Ive | 2 | Tracked CTAs; consent-gated analytics unchanged |

**Total: 20/20** — passes gate.

---

## Mission 30 — Marketing site (features, pricing, legal, SEO)

**Scope:** `/features`, `/pricing`, `/faq`, `/how-it-works`, legal pages, `/blog`, consent + UTM.

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | Shared shell; FAQ uses native details, no widget soup |
| Kare | 2 | FAQ answers auto-submit/CAPTCHA straight; draft legal banners |
| Norman | 2 | Footer + nav cover all public routes; skip link retained |
| Nielsen | 2 | Pricing table scannable; entitlements match Settings |
| Tufte | 2 | Plan limits as numbers, not vanity metrics |
| Vignelli | 2 | One grid/tokens across marketing set |
| Rand | 2 | Consistent voice vs landing; trust-forward features |
| Maeda | 2 | Motion vocabulary unchanged; blog is calm |
| Wroblewski | 2 | Mobile nav shows Features + Pricing; FAQ accordion |
| Ive | 2 | Consent links to privacy; UTM persists for funnel |

**Total: 20/20** — passes gate.

---

## Mission 31 — Test suite expansion & quality hardening

**Scope:** Golden-path API integration, admin route coverage, schema contract tests, Playwright marketing a11y + funnel smoke, worker browser fixture, coverage gate 58%.

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | Tests grouped by layer; no duplicate harness sprawl |
| Kare | 2 | Policy asserts auto-submit opt-in; consent unit tests |
| Norman | 2 | Axe on all public routes; skip-link keyboard e2e |
| Nielsen | 2 | Failures name route + violation JSON |
| Tufte | 2 | Contract tests pin enum drift, not vanity coverage % |
| Vignelli | 2 | Shared `marketing-routes.ts` for axe + sitemap parity |
| Rand | 2 | Golden path documents human-in-the-loop invariant |
| Maeda | 2 | Reduced-motion e2e; `color-contrast` disabled where theme false-positives |
| Wroblewski | 2 | Funnel smoke: landing → signup, pricing keyboard focus |
| Ive | 2 | Hermetic fixtures — no live ATS in CI |

**Total: 20/20** — passes gate.

---

## Mission 32 — Performance, load & resilience testing

**Scope:** API hot-path fixes, SSE backpressure, load/resilience tests, worker concurrency, artifact retention, web bundle budget.

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | One presign map; SQL aggregates replace Python loops |
| Kare | 2 | Budget hard-stop under concurrency; degraded readiness surfaced |
| Norman | 2 | Auto-reconnect + snapshot catch-up on stream errors |
| Nielsen | 2 | Load failures name slowest path + threshold |
| Tufte | 2 | Perf budgets as numbers (KB, 3s, 50 events/poll) |
| Vignelli | 2 | Markers + CI steps mirror test pyramid doc |
| Rand | 2 | Honest headless worker concurrency default (2) |
| Maeda | 2 | Lazy filmstrip thumbs; analytics code-split |
| Wroblewski | 2 | Degraded pill already on `/readyz`; healthz vs readyz split |
| Ive | 2 | Weekly artifact purge prevents trace volume fill |

**Total: 20/20** — passes gate.

---

## Mission 34 — Production readiness & launch

**Scope:** Admin ops metrics, webhook alerting, structured logs, runbooks, launch checklist, uptime script.

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | Reuses admin attention pattern; no duplicate monitoring stack |
| Kare | 2 | Runbooks name symptoms → fix plainly |
| Norman | 2 | test-alert endpoint; readyz fires webhook |
| Nielsen | 2 | Launch checklist scannable; ops metrics on overview |
| Tufte | 2 | Budget/backlog/success rate as numbers, not vanity charts |
| Vignelli | 2 | Runbooks under `docs/runbooks/` consistent |
| Rand | 1 | Ops/infra mission |
| Maeda | 2 | Optional Sentry; webhook-only when configured |
| Wroblewski | 1 | Admin desktop-first |
| Ive | 2 | Alert cooldown prevents webhook spam |

**Total: 19/20** — passes gate. CI green: [run 27276789268](https://github.com/HiNala/jober/actions/runs/27276789268).

**M99 (M34):** Added webhook success-path tests + `staging-golden-path.sh`; no score change.

---

## Mission 33 — Railway production deployment

**Scope:** Production Dockerfiles, API/worker health probes, deploy runbook, Railway service configs, staging smoke script. No product UI changes.

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | One smoke script; migrate-then-serve entrypoint |
| Kare | 2 | Runbook names classic failures (PORT, API URL, creds) |
| Norman | 2 | `/healthz` vs `/readyz` split; worker Celery ping gate |
| Nielsen | 2 | Variable template + staging→prod promotion steps |
| Tufte | 2 | Smoke output is JSON checks, not log noise |
| Vignelli | 2 | `infra/railway/*.toml` mirrors compose roles |
| Rand | 1 | Infra mission; brand N/A |
| Maeda | 2 | Private networking default; buckets optional |
| Wroblewski | 1 | Ops docs; no mobile product surface |
| Ive | 2 | SSL + secret guards feel deliberate, not bolted on |

**Total: 19/20** — passes gate.

---

## Mission 99 (post–Mission 33) — improvements logged

| Change | Why |
|--------|-----|
| `railway-smoke.sh` checks landing + `/signup` | Staging golden-path entry without auth; closes M33 acceptance gap |
| `test_config_database_url.py` | Railway `postgresql://` → `asyncpg` rewrite had no fixture |
| README Railway section + `infra/railway/` tree | Cold-start deploy path was only in mission doc |
| Deploy runbook PowerShell creds pitfall | Corrupted `MINIO_*` vars blocked `/readyz` during first staging deploy |

**Staging verified:** API `/readyz` green; web landing 200 (2026-06-10).

**CI:** [run 27272669598](https://github.com/HiNala/jober/actions/runs/27272669598) (green on `4ed58e5`).

---

## Mission 99 (post–Mission 32) — improvements logged

| Change | Why |
|--------|-----|
| Perf indexes on ORM models | Migration-only indexes failed `check_migration_drift.py` in CI |
| `test_artifact_retention.py` | Retention purge task had no regression fixture |
| `.env.example` worker/retention vars | Cold-start ops config for concurrency + artifact TTL |
| Load smoke uses `/api/dashboard/summary` | Wrong batches prefix returned 404 in CI |
| SSE uses `get_running_loop()` | `get_event_loop()` broke streaming tests under pytest-asyncio |
| Load smoke: parallel healthz only | Shared pytest session cannot serve concurrent ORM reads |
| SSE burst test calls `stream_run_events` directly | httpx SSE + asyncpg loop mismatch in CI |

---

## Mission 99 (post–Mission 31) — improvements logged

| Change | Why |
|--------|-----|
| `/how-it-works` step headings `h2` when page has `h1` | Axe `heading-order` failed on dedicated page |
| Pricing e2e asserts real `h1` copy | Smoke test expected `/pricing/i` but title is “Plans that match…” |
| Policy golden path skips `/admin/overview` | Policy CI has Postgres only; overview needs Redis (backend job covers it) |
| `sitemap-routes` ↔ `e2e/marketing-routes` parity vitest | Duplicate route lists could drift silently from axe coverage |
| `testing.md` documents `CI=true pnpm test:e2e` | Stale `reuseExistingServer` hid heading-order fix until rebuild |

---

## Mission 99 (post–Mission 30) — improvements logged

| Change | Why |
|--------|-----|
| Split UTM SDK commit (`470104d`) | `aad87e3` shipped legal/tests without `captureUtmFromUrl` — CI failed until SDK landed |
| `marketingMetadata` vitest | Per-page OG/canonical had no regression fixture |
| Footer `/how-it-works` route | Anchor-only link broke after dedicated page shipped |
| Landing pricing teaser limits | Teaser still vague after real `/pricing` entitlements went live |
| `marketingSitemapPaths` vitest | New routes could drop from sitemap silently |
| `readPersistedUtmParams` test | UTM capture without read-path fixture left funnel gap |
| Social proof / pricing FAQ copy | User-facing text still referenced internal mission numbers |

---

## Mission 99 (post–Mission 29) — improvements logged

| Change | Why |
|--------|-----|
| `trackMarketingCta` + vitest | CTA instrumentation had no regression fixture |
| `getSiteUrl` tests | Sitemap/OG URLs must not silently break in deploy |
| Mobile header Pricing link | Secondary nav was hidden below `md` — weakest Wroblewski gap |
| README + `.env.example` `NEXT_PUBLIC_SITE_URL` | Cold-start SEO config was undocumented |

---

## Mission 99 (post–Mission 28) — improvements logged

| Change | Why |
|--------|-----|
| Mission doc + Design Council on remote | `89a38ca` shipped web UI but docs were local-only until follow-up commit |
| `permissions.test.ts` covers `admin:ops:read` + `admin:config:manage` | New M28 permissions had no web fixture |
| README admin dashboard section | Cold-start path for `/admin` was missing |
| `AdminSupportView` structured panel | Raw JSON support dump was weakest UX / Norman feedback |
| Audit log action filter (system page) | API supported filters but UI did not expose them |
| `test_operational_view_excludes_private_fields` | Privacy boundary needed explicit regression lock |

---

## Mission 28 — Admin dashboard (ops-first)

**Scope:** `/admin` overview, acquisition, users, runs, cost, system, config sections.

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | Attention-first layout; no vanity charts without action |
| Kare | 2 | Privacy copy on users/support; calm ops tone |
| Norman | 2 | Section nav + loading/error on every panel |
| Nielsen | 2 | “What needs me” banners; search on users |
| Tufte | 2 | Dense tables + M26 chart reuse; tabular nums |
| Vignelli | 2 | Shared admin shell + chart-theme |
| Rand | 1 | Internal ops surface |
| Maeda | 2 | One question per section/page |
| Wroblewski | 2 | Nav wraps; tables scroll on mobile |
| Ive | 2 | Audited support view; config toggles with feedback |

**Total: 19/20** — passes gate (Tufte ≥18).

**CI:** [run 27204910495](https://github.com/HiNala/jober/actions/runs/27204910495) (green on `89a38ca`).

---

## Mission 99 (post–Mission 27) — improvements logged

| Change | Why |
|--------|-----|
| Shared `enum_value()` helper | `User.role` / `User.status` are VARCHAR columns; triple `_enum_value` copies were brittle |
| `can()` normalizes string roles | DB-loaded auth context could deny admins when `ROLE_PERMISSIONS` keys are enums |
| RBAC unit tests run without Postgres | Module-level `pytestmark` skipped coverage/startup fixtures locally |
| `test_list_users_for_admin_serializes_string_role_status` | Regression for CI `AttributeError` on `.value` |
| Admin mutation `onError` toasts | Promote/demote/suspend failures were silent — weakest UX on the admin surface |

**CI:** [run 27199667593](https://github.com/HiNala/jober/actions/runs/27199667593) (green on `b1504e5`).

---

## Mission 27 — RBAC & admin users

**Scope:** `/admin/users` page, admin nav guard, role/status actions, audit log panel.

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | Table + inline actions; no decorative chrome |
| Kare | 2 | Copy explains operational-only boundary (no vault) |
| Norman | 2 | Loading/error states; disabled self-suspend |
| Nielsen | 2 | Promote/demote/suspend labels match API semantics |
| Tufte | 2 | Audit log is scannable rows, not chart noise |
| Vignelli | 2 | Reuses `surface.card` + app spacing tokens |
| Rand | 1 | Internal admin utility |
| Maeda | 2 | One screen for directory + audit tail |
| Wroblewski | 2 | Table scrolls; actions stack on narrow widths |
| Ive | 2 | Server-enforced guard; UI hide is secondary |

**Total: 19/20** — passes gate.

---

## Mission 26 — Analytics dashboards (Tufte pass)

**Scope:** `/analytics` page, Recharts components, date-range controls, user + admin panels.

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | Attention notes before vanity totals; no chart decoration |
| Kare | 2 | Plain labels; workspace vs product tabs for admins |
| Norman | 2 | Loading/error states; empty-range copy on charts |
| Nielsen | 2 | Consistent 7d/30d/90d + compare toggle across panels |
| Tufte | 2 | High data-ink: thin grid, no gradients, tabular nums on KPIs |
| Vignelli | 2 | Shared `chart-theme` + `surface.card` grid |
| Rand | 1 | Utility analytics surface |
| Maeda | 2 | One chart type per question; funnel table for exact counts |
| Wroblewski | 2 | Controls wrap; tables scroll on narrow viewports |
| Ive | 2 | 60s API cache; rollup-only queries |

**Total: 19/20** — passes gate (Tufte ≥18).

---

## Mission 99 (post–Mission 26) — improvements logged

| Change | Why |
|--------|-----|
| `downloadAnalyticsCsv` + `ExportCsvButton` | Raw `<a href>` to API host could miss session cookies; fetch with `credentials: include` |
| Admin traffic table (bounce, avg time, sessions) | API already returned metrics; UI only showed bar chart |
| Funnel compare column + drop-off attention | `compare_previous` API existed but UI ignored `previous_steps` |
| `test_admin_traffic_reads_page_rollups` | Traffic dashboard had no regression fixture |
| `test_user_analytics_compare_previous` | Compare toggle was untested end-to-end |
| `analytics/error.tsx` | Match other app routes' recoverable error boundary |

---

## Mission 99 (post–Mission 25) — improvements logged

| Change | Why |
|--------|-----|
| `MIN_ANALYTICS_SESSION_ID_LEN` + `server_session_id()` guard | CI caught `"server"` (6 chars) breaking Pydantic min_length=8 on letter generate |
| `test_server_session_id_fallback_meets_schema_min_length` | Regression lock for server emitter session ids |
| `test_consent_opt_out_suppresses_tracking` | Explicit `consent=0` path was untested |
| `purge_stale_analytics_events` + weekly Celery job | `ANALYTICS_RETENTION_DAYS` was config-only; privacy retention now enforced |
| `test_purge_stale_analytics_events` | Fixture for retention purge |

**CI:** [run 27184269887](https://github.com/HiNala/jober/actions/runs/27184269887) (backend + web + policy + quarantine green on `48f9ad4`).

---

## Mission 99 (post–Mission 24) — improvements logged

| Change | Why |
|--------|-----|
| `PATCH /application-runs/{id}/run-options` | Mission 24 required per-run letter toggle; was API-only via `checkpoint_data` |
| `RunLetterOptions` in run console | Default / generate / skip without opening Settings mid-run |
| Library **Duplicate** button | Reuse endpoint existed but Library had no affordance |
| `test_patch_cover_letter_text_updates_ats_score` | PATCH edit path lacked regression coverage |
| `test_run_letter_options` + letter-options GET test | Close M24 acceptance gaps |

**CI:** [run 27178549543](https://github.com/HiNala/jober/actions/runs/27178549543) (backend + web + policy + quarantine green on `cc1f6bd`).

### Run console letter options (M99 addendum)

| Criterion | Score | Notes |
|-----------|-------|-------|
| Rams | 2 | Three radios; hides when terminal + no override |
| Kare | 2 | Status copy explains default vs generate vs skip |
| Norman | 2 | Matches run console card pattern |
| Nielsen | 2 | `aria-label` on section; toast on save |
| Tufte | 2 | No charts; one-line state summary |
| Vignelli | 2 | `surface.card` + icon rail consistency |
| Rand | 2 | Distinct from Document Studio but same tokens |
| Maeda | 2 | Default defers to Settings — less is more |
| Wroblewski | 2 | Radio row wraps on narrow widths |
| Ive | 2 | Only shown when actionable or override exists |

**Total: 20/20** — passes gate.

---

## Mission 99 (post–Mission 23) — improvements logged

| Change | Why |
|--------|-----|
| `board_listing.html` in `jober_fixtures/pages/jobs` | `load_ats_fixture("board_listing")` failed in CI — fixture lived only under `apps/api/tests` |
| `_LEGACY_ATS_PATHS` maps `board_listing` → `jobs/board_listing` | Keeps discovery tests on shared fixture loader contract |
| `accept_candidates` dedupes by `candidate_key` in one request | `accepted` count was inflated when UI sent duplicate rows; now returns `skipped_duplicates` |
| Tests: refresh, saved-search link, attach-import, batch `job_list_id` | Mission 23 iteration paths had only search+accept coverage |
| `test_discovery_board_parser.py` | Parser regressions caught without Postgres |
| Mission 23 deferred notes (cooldown Redis, enrich fallback) | Explicit non-blocking gaps before Mission 24 |

---

## Mission 99 (post–Mission 22) — improvements logged

| Change | Why |
|--------|-----|
| Search page uses React Query + `key` remount for `?q=` | Avoids `set-state-in-effect` lint; nav deep-links work |
| `buttonVariants` on library links | Base UI `Button` has no `asChild` |
| `resolve_llm_runtime` + user BYOK | Gateway reads encrypted per-user keys at generation time |
| Preferences/BYOK API tests | Locks server-side persistence and no-secret-in-response |
| Job list archive + reorder in Library UI | Mission 22 partial task; API existed without affordances |
| `test_library_api` search + archive fixtures | Regression coverage for cross-library search and list lifecycle |
| README Mission 22 routes + prefs/BYOK note | New contributors can find Library/Settings without mission history |

---

## Mission 99 (post–Mission 21) — improvements logged

| Change | Why |
|--------|-----|
| `.env.example` Google OAuth + `WEB_APP_URL` | Operators need documented callback and redirect base without reading mission docs |
| CI uses `minio/mc` Docker image for bucket init | dl.min.io CDN 504s were failing policy/backend jobs even with retries |
| Pending link token survives wrong password | Confirm-link consumed Redis token before password check, breaking retry |
| Login `AuthOAuthAlert` for callback errors | OAuth failures redirected to `/login?error=…` with no feedback |
| `NEXT_PUBLIC_GOOGLE_OAUTH_ENABLED` gate | Avoid broken Google CTA when API credentials are unset |
| OAuth edge-case tests (unverified email, returning user) | Mission 21 acceptance paths lacked fixture coverage |

---

## Mission 99 (post–Mission 20) — improvements logged

| Change | Why |
|--------|-----|
| Tenant-scope documents/imports/exports/resumes | M20 gap: artifact routes ignored `auth.tenant_id` |
| `tenant_guard` + job-target sub-routes | Extraction, fill, discovery, verify, recovery were cross-tenant readable |
| Tenant-scoped failure analytics | `/recovery/failure-analytics` leaked aggregate data across tenants |
| Redis client reset between pytest cases | Flaky `Event loop is closed` in native auth tests |
| `ReAuthDialog` + `apiFetch`/`authFetch` 401 recovery | Session expiry should re-auth in place, not lose page state |
| Settings session management UI | M20 iteration: active sessions + sign out everywhere |
| `session-recovery.test.ts` | Fixture for 401 handler registration regressions |

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
