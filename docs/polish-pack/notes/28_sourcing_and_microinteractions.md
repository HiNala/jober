# Mission 28 — Sourcing, brand signature, and micro-interactions

**Date:** 2026-06-12

## Brand signature (chosen)

**Treatment:** mesh gradient + subtle animated grid (`BrandSignature`).

| Location | Component |
|----------|-----------|
| Marketing hero | `components/marketing/hero.tsx` |
| Auth brand panel | `components/auth/auth-brand-panel.tsx` |

`AnimatedBackground` is a deprecated re-export of `BrandSignature` — do not use elsewhere.

## Sourcing shortlist

Patterns adapted onto Jober tokens (no new animation runtime; CSS + existing `tw-animate-css`).

| Pattern | Inspiration | License / source | Implementation |
|---------|-------------|------------------|----------------|
| Mesh hero + grid | 21st.dev animated grid heroes, v0 marketing backgrounds | MIT-style community patterns; **rewritten** | `brand-signature.tsx`, `jober-brand-grid` in `globals.css` |
| Border-beam CTA | Magic UI / 21st.dev border-beam | MIT (common CSS mask technique) | `brand-border-beam`, `MarketingCtaLink` default variant |
| Skeleton shimmer | shadcn skeleton + Aceternity shimmer | MIT | `motionSkeleton`, `Skeleton` primitive |
| Stepper connector | Linear / 21st.dev step flows | N/A — gradient CSS | `brand-stepper-connector`, how-it-works steppers |
| Chart draw-in | Recharts default animation | MIT (recharts) | `useChartMotion()` + `isAnimationActive` |
| LIVE pulse | Hyper Agents live status | N/A — opacity/scale only | `motionLivePulse` on run console stream badge |

**Browsing limitation:** External 21st.dev/v0 URLs not fetched in CI; structures implemented from established open patterns and recorded here.

## Micro-interaction inventory (sweep)

| Surface | Element | Treatment | Status |
|---------|---------|-----------|--------|
| Global | `Button` | `motionMicro` + `motionPress` | **M28** |
| Global | `Input` | `motionMicro` + focus ring | **M28** |
| Global | `TableRow` | `motionMicro` hover | **M28** |
| Global | `TabsTrigger` | `motionMicro` + indicator `after:` | existing + **M28** |
| Global | `Skeleton` | `motionSkeleton` shimmer | **M28** |
| Marketing | Primary CTA | `brandBorderBeam` | **M28** |
| Marketing | Nav links | Larger type scale (1.0625–1.125rem) | **M28** |
| Marketing | Hero loading | `motionSkeleton` (not `animate-pulse`) | **M28** |
| Run console | LIVE badge | `motionLivePulse` (not shimmer) | **M28** |
| Analytics | Line/bar charts | 800ms draw-in, off if reduced motion | **M28** |
| Queue | Clickable rows | `motionTableRow` | **M28** |
| Toasts | Sonner | `cn-toast` → `jober-attention-enter` | pre-M28 |

## Reduced motion

All new keyframes gated by `prefers-reduced-motion` in `globals.css` and/or `motion-safe:` prefixes. Charts use `usePrefersReducedMotion()` via `useChartMotion()`.

## Before / after

Re-capture after deploy:

```bash
cd apps/web && PLAYWRIGHT_SKIP_WEB_SERVER=1 PLAYWRIGHT_BASE_URL=<prod> node scripts/capture-screenshots.mjs
```

Focus: `01-home.png`, `11-login.png`, `22-analytics.png`, run console (when demo data available).

## Bundle

No new dependencies. `pnpm check:bundles` must stay under budget after changes.
