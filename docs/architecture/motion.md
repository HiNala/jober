# Motion system

Jober uses a **CSS-first motion vocabulary** — no framer-motion. All feature surfaces import tokens from `apps/web/src/lib/design/motion.ts`; CSS variables and keyframes live in `apps/web/src/app/globals.css`.

## Principles

| Layer | Duration | Use |
|-------|----------|-----|
| Micro | 150ms (`--motion-micro`) | Hover, press, focus, pill color |
| Fast | 200ms (`--motion-fast`) | Press settle, sidebar width |
| View | 300ms (`--motion-view`) | Cross-fades, route enter, filmstrip |
| Layout | 400ms (`--motion-layout`) | Filmstrip expand, pane chrome |
| Max | 500ms (`--motion-max`) | Hard ceiling for view transitions |

- **Easing:** `--ease-organic` (ease-out) for most; `--ease-spring` for drag release only.
- **Properties:** Animate `opacity` and `transform` only — never layout properties during SSE screenshot bursts.
- **Reduced motion:** `prefers-reduced-motion: reduce` collapses all durations globally; `motion-safe:` prefixes gate non-essential animation.

## Token exports

| Export | Purpose |
|--------|---------|
| `motionMicro` | Color/border/opacity/transform transitions |
| `motionPress` | Active scale feedback (0.97) |
| `motionView` | Panel/cross-fade transitions |
| `motionLayout` | max-height / chrome expand |
| `motionFadeIn` | Enter (4px translateY) |
| `motionShimmer` | Agent “Reasoning…” state |
| `motionStreamReveal` | New terminal line |
| `motionStatusEnter` | Status pill lifecycle change |
| `motionSpringSettle` | Kanban card / filmstrip select |
| `motionAttentionEnter` | Checkpoint + toast enter |
| `motionLivePulse` | LIVE stream badge pulse |
| `motionAmbientDrift` | Ambient canvas gradient slow drift |
| `motionSkeleton` | Unified skeleton shimmer |
| `brandBorderBeam` | Marketing primary CTA border accent |
| `brandStepperConnector` | How-it-works stepper connector |
| `motionTableRow` | Clickable table row hover |
| `motionEmptyPulse` | Empty-state icon (once, no loop) |
| `motionDragHandle` | Resize separator affordance |
| `motionDragItem` | Grab cursor + lift on drag |

## Components

| Component | Path |
|-----------|------|
| `BrandSignature` | `components/marketing/brand-signature.tsx` — **marketing hero + auth only** |
| `ReasoningShimmer` | `components/motion/reasoning-shimmer.tsx` |
| `StreamingText` | `components/motion/streaming-text.tsx` |
| `StatusPill` | `components/motion/status-pill.tsx` |
| `MotionCrossfade` | `components/motion/motion-crossfade.tsx` |
| `RouteTransition` | `components/motion/route-transition.tsx` |
| `AmbientCanvas` | `components/design-system/ambient-canvas.tsx` |
| `StatusLivePill` | `components/design-system/status-live-pill.tsx` |
| `SkeletonStream` | `components/design-system/skeleton-stream.tsx` |

## Lint / CI

- ESLint rule `joberMotion/no-raw-motion-duration` on `src/**` except `ui/`, `marketing/`, and `motion.ts`.
- `pnpm check:motion` — script duplicate guard for CI.
- Run both via `pnpm lint:strict && pnpm check:motion`.

## Live-run profiling note

Screenshot frames use `jober-screenshot-frame` (opacity-only, 150ms) keyed by URL — no layout animation during SSE bursts. Filmstrip uses `max-height` transition (layout token) which is acceptable off the hot path.

Event terminal lines use `shouldRevealStreamLine()` (`lib/motion/event-stream-reveal.ts`): per `runId`, the first populated batch sets a seq baseline; only lines with `seq > baseline` play `motionStreamReveal`. Historical catch-up stays static.

## Status tone map

`runStatusTone()` maps API statuses → visual tones: `queued`, `running`, `review`, `submitted`, `failed`, `idle`. `StatusPill` re-animates on tone change via React `key`.
