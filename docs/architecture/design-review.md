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
