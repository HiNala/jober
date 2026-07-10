# Mission 35 — Design System 2030 (Hyperagent Shell Foundations)

> **Phase:** Perfection pack (post-launch primary missions 00–34)  
> **Depends on:** Missions 02, 16–19, polish-pack 10 & 28  
> **Run Mission 99 after this mission**

## Purpose

Establish the **2030 design system** so every subsequent perfection mission builds on one coherent visual and interaction language: Hyperagent-grade dark shell, Grok-grade empty states, Linear-grade type, token-enforced motion. This mission is foundations only — not full page redesigns.

## Context

Primary missions shipped a solid shadcn/token base and polish-pack closed many “generic SaaS” issues. Remaining gap: product still does not feel like the **job-applying site of the future**. Binding design bible: [`docs/architecture/design-north-star-2030.md`](../architecture/design-north-star-2030.md). Owner references: Hyperagent thread/canvas, Grok SuperGrok surfaces.

## Scope

### In scope
- Dark-first token refresh (app + marketing defaults)
- New primitive components listed in north star §4
- Surface family enforcement + kitchen-sink examples
- Sidebar/shell scaffolding tokens (implementation of full shell is M39)
- Motion tokens for ambient canvas, skeleton stream, checkpoint
- Design token + architecture doc updates
- ESLint rules remain green (`no-raw-color-literal`, `no-raw-motion-duration`)

### Out of scope
- Full marketing rewrite (M36)
- Full workspace shell swap (M39)
- Stripe/auth product work (M37–38)
- New product features beyond design primitives

## Starting checklist
- [ ] Read `design-north-star-2030.md` end-to-end
- [ ] Capture current `/kitchen-sink`, `/dashboard`, `/` screenshots as baseline
- [ ] Confirm `apps/web/src/lib/design/{tokens,motion,surface-variants}.ts` and `globals.css` locations

## Tasks

### 1. Token refresh
- [ ] Shift app canvas to near-black Hyperagent range; sidebar elevated; soft primary
- [ ] Add `--canvas-ambient-*` CSS variables (multi-stop gradient)
- [ ] Add `--live` / live-pulse color tokens
- [ ] Update light theme only if marketing stays dual-theme; default ship dark marketing
- [ ] Sync `design-tokens.md` and `tokens.ts` with CSS

### 2. New primitives (components)
- [ ] `AmbientCanvas` — full-bleed soft gradient + optional slow drift
- [ ] `SkeletonStream` — Hyperagent-style rounded loading bars (left/right alignment variants)
- [ ] `StatusLivePill` — Live / Idle / Needs you
- [ ] `CommandComposer` presentational shell (Plan menu + attach + send; wire later)
- [ ] `CheckpointCard` presentational (question + radio options + Skip/Send)
- [ ] `SuggestionChips`
- [ ] `ApproveSendBar` presentational sticky bar
- [ ] `UnlockModal` layout shell (illustration slot + 3 feature cards + CTA)

### 3. Kitchen-sink & enforcement
- [ ] Document all new primitives on `/kitchen-sink` (dev-only; 404 in prod)
- [ ] Ensure no raw hex/rgb outside tokens in new files
- [ ] Reduced-motion: ambient drift and decorative beams disable

### 4. Docs
- [ ] Update `docs/architecture/design-tokens.md`
- [ ] Update `docs/architecture/motion.md` with new motion keys
- [ ] Link north star from `MISSION_INDEX.md` and README design section

## Validation
```bash
cd apps/web && pnpm typecheck && pnpm lint:strict && pnpm check:motion && pnpm build
cd apps/web && pnpm test
# visual
pnpm exec playwright test e2e/a11y-marketing.spec.ts e2e/a11y-app.spec.ts --project=chromium
```

## Acceptance criteria
- [ ] Dark tokens match north star ranges; kitchen-sink shows all new primitives
- [ ] No new raw color/motion lint violations
- [ ] Design Council score for design-system surfaces ≥19/20
- [ ] Docs updated; Mission 99 run

## Git workflow
- Branch optional; commits tagged `[m35]`  
- Push when gates green

## Production guidance
- Safe to deploy token changes if contrast verified (WCAG AA body text)
- Coordinate with M36/M39 deploys if marketing defaults flip dark

## Residual risks
- Existing light marketing pages may look wrong until M36 — ship dark marketing in same release train when possible
