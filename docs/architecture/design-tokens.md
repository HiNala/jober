# Jober design tokens

Dark mode is the default for in-app surfaces. Marketing (`/`) may use richer motion; app routes stay calm and low-chroma.

## Palette (OKLCH)

| Token | Light | Dark (default app) | Use |
|-------|-------|-------------------|-----|
| `--background` | `oklch(1 0 0)` | `oklch(0.11 0.015 260)` | Near-black page canvas |
| `--foreground` | `oklch(0.14 0.015 240)` | `oklch(0.96 0.008 260)` | Body text |
| `--card` | `oklch(1 0 0)` | `oklch(0.16 0.018 260)` | Panels |
| `--primary` | `oklch(0.42 0.14 250)` | `oklch(0.72 0.12 250)` | Actions, focus |
| `--muted` | `oklch(0.96 0.005 240)` | `oklch(0.19 0.018 260)` | Subtle fills |
| `--muted-foreground` | `oklch(0.48 0.02 240)` | `oklch(0.65 0.02 260)` | Secondary text |
| `--accent` | `oklch(0.52 0.14 250)` | `oklch(0.62 0.14 165)` | Accents |
| `--live` | `oklch(0.55 0.14 165)` | `oklch(0.72 0.14 165)` | LIVE badges / pulse |
| `--canvas-ambient-from/mid/to` | soft lavender/peach/blue | softer multi-hue on black | AmbientCanvas |
| `--destructive` | `oklch(0.55 0.2 25)` | `oklch(0.62 0.18 25)` | Errors |
| `--border` | `oklch(0.91 0.006 240)` | `oklch(1 0 0 / 10%)` | Dividers |
| `--sidebar` | light elevated | `oklch(0.13 0.018 260)` | Nav rail |

## Type scale

| Class | Size | Use |
|-------|------|-----|
| `text-xs` | 12px | Meta, pills |
| `text-sm` | 14px | Tables, dense UI |
| `text-base` | 16px | Body |
| `text-[1.0625rem]` | 17px | Marketing nav (md) |
| `text-[1.125rem]` | 18px | Marketing nav (lg) |
| `text-lg` | 18px | Section titles, marketing logo |
| `text-2xl` | 24px | Page titles |
| `text-4xl` | 36px | Marketing hero only |

Font: **Geist Sans** (UI), **Geist Mono** (logs, IDs).

## Radius & motion

- `--radius`: `0.5rem` (8px) — cards, inputs
- Animations use `motion-safe:` / `@media (prefers-reduced-motion: reduce)` — marketing brand signature and border-beam disable decorative animation when reduced motion is set.
- **Brand signature** (`BrandSignature`): mesh gradient + grid — hero and auth only. See `docs/polish-pack/notes/28_sourcing_and_microinteractions.md`.

## Component surface families (Mission 10)

Three deliberate tiers — never blend marketing expressiveness with workspace density or terminal mono styling.

| Family | Token / API | Radius | Border | Typography | Use |
|--------|-------------|--------|--------|------------|-----|
| **Marketing** | `surface.marketing`, `<Surface family="marketing">` | `rounded-2xl` | soft / ring | sans, roomy | Bento, pricing, FAQ, funnel |
| **Workspace** | `surface.workspace`, `<Surface family="workspace">` | `rounded-lg` | quiet `border/60` | sans, dense | Tables, settings, admin, library |
| **Terminal** | `surface.terminal`, `surface.terminalMedia` | `rounded-lg` | inset shadow | mono `text-xs` | Event stream, live screenshots |

CVA definitions: `apps/web/src/lib/design/surface-variants.ts`. Terminal colors use CSS vars `--terminal-bg`, `--terminal-fg`, `--terminal-muted` in `globals.css`.

## Source of truth

CSS variables live in `apps/web/src/app/globals.css`. Tailwind v4 maps them via `@theme inline`. Runtime class strings: `apps/web/src/lib/design/tokens.ts`.
