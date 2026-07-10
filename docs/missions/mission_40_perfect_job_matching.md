# Mission 40 — Perfect Job Matching & Discovery Engine

> **Phase:** Perfection pack  
> **Depends on:** M03, M06, M23, M39  
> **Run Mission 99 after**

## Purpose

Make Discover → List → Queue the **best path to the perfect jobs to apply to**: strong fit signals, clean UX, reliable import/search, dedupe, and batch launch — so users build a high-signal list, not a spam pile.

## Context

M23 unified discovery exists (board search, XLSX attach, accept, lists, batch filter). Gaps for “perfection”:
- Fit scoring is basic keyword overlap — improve explainability and ranking UX
- Mobile/discover polish
- Saved search refresh reliability
- Clearer “why this fits” cards
- Seamless path: accept → tailor docs (M41) → apply (M42)
- Search vs Discover IA clarity

## Scope

### In scope
- Discovery UX redesign on workspace shell
- Fit score v2: skills + title + fit lane + location signals with explanation chips
- Candidate cards: company, role, source, fit, why-fit, ATS badge
- Bulk accept / reject; keyboard selection
- List detail: members, refresh, launch batch, export status columns
- Import wizard polish (column mapping already exists — UX upgrade)
- Dedup confidence display
- Empty/error/loading states
- API improvements only as needed for scoring explainability

### Out of scope
- Mass scraping of Indeed/LinkedIn at scale
- New ATS adapters
- Autonomous apply without queue selection

## Starting checklist
- [ ] Read discovery routers + board parser + frontend discover pages
- [ ] Confirm upsert keys for JobTarget
- [ ] Review library list models

## Tasks

### 1. Product logic
- [ ] Document fit algorithm in `docs/architecture/` short ADR: inputs, weights, non-goals
- [ ] Return `fit_score` (0–100) + `fit_reasons: string[]` on candidates
- [ ] Prefer jobs with direct apply URLs; flag boards-only
- [ ] Preserve policy: user-selected boards/URLs only

### 2. Discover UI
- [ ] Dual mode tabs: Search boards · Upload spreadsheet (single page)
- [ ] Filters: priority, location style, fit lane, has apply URL
- [ ] Candidate table/cards with bulk actions
- [ ] Side detail drawer: description excerpt, reasons, accept CTA
- [ ] Progress for enrich/extract

### 3. Lists & library
- [ ] Named lists with counts by status
- [ ] Refresh saved search → only new candidates
- [ ] One-click “Prepare batch” → queue with policy default review_before_submit

### 4. Import path
- [ ] Drag-drop XLSX; mapping preview; error rows explained
- [ ] Round-trip status columns still work (M03)

### 5. Tests
- [ ] API discovery + fit reason unit tests
- [ ] e2e `discover-journey.spec.ts` green
- [ ] Parser fixtures for ≥1 board listing format

## Validation
```bash
cd apps/api && pytest tests/test_discovery_api.py tests/test_discovery_board_parser.py tests/test_import_api.py tests/test_xlsx_import.py -q
cd apps/web && pnpm typecheck && pnpm lint:strict
pnpm exec playwright test e2e/discover-journey.spec.ts
```

## Acceptance criteria
- [ ] User can build a list from search **and** XLSX with clear fit explanations
- [ ] Batch launch from list works with entitlements
- [ ] Design Council ≥19/20 on Discover + Library
- [ ] No scrape beyond user-provided boards/URLs

## Production guidance
- Watch outbound fetch rate limits / SSRF validators on discovery
- Log fit algorithm version for debugging
