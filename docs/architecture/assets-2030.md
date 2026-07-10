# 2030 visual assets

Generated for perfection pack marketing and empty states. Prefer **code-built UI chrome** for product mocks that must show accurate copy (run console, fill diff). Use these images only as **ambient atmosphere**.

| File | Use | Mission |
|------|-----|---------|
| `apps/web/public/images/2030/hero-ambient.jpg` | Marketing hero backdrop / AmbientCanvas texture | M36 |
| `apps/web/public/images/2030/unlock-ambient.jpg` | Pro unlock modal illustration | M38 |
| `apps/web/public/images/2030/empty-ambient.jpg` | Dashboard / command-center empty state glow | M39 |

## Usage rules

- Keep opacity low (≈15–40%) when used as full-bleed backgrounds so type remains WCAG AA.
- Always provide a solid near-black fallback color.
- Honor `prefers-reduced-motion` (static image is fine; do not add aggressive Ken Burns).
- Do not put critical text inside the image files — text lives in React.

## Future assets (build in code)

- `HeroRunPreview` / fill-diff mock — components, not PNGs
- OG social cards — prefer `opengraph-image.tsx` or static designed cards with real copy
