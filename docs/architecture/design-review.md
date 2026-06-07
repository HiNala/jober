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
