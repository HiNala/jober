# Mission 10 — Component tiering sweep

## Families (code)

| Family | CVA / component | Traits |
|--------|-----------------|--------|
| Marketing | `surface.marketing` / `<Surface family="marketing">` | `rounded-2xl`, soft ring, expressive padding |
| Workspace | `surface.workspace` / `<Surface family="workspace">` | Dense, quiet border, data-first |
| Terminal | `surface.terminal` / `<Surface family="terminal">` | Mono, `--terminal-*` tokens, status accents |

Source: `lib/design/surface-variants.ts`, `components/ui/surface.tsx`, `lib/design/tokens.ts`.

## Migration table

| Directory | Action | Result |
|-----------|--------|--------|
| `lib/design/` | Added CVA variants + tests | **Done** |
| `components/ui/` | `Surface` component | **Done** |
| `components/canvas/` | `surface.workspace` panels; `surface.terminalMedia` for screenshots | **Done** |
| `components/run-console/` | Terminal family + `terminalMedia` frames | **Done** |
| `components/marketing/` | `surface.card` → `surface.marketing` (11 files) | **Done** |
| `components/admin/` | `surface.card` → `surface.workspace` | **Done** |
| `components/analytics/` | `surface.card` → `surface.workspace` | **Done** |
| `components/dashboard/` | `surface.card` → `surface.workspace` | **Done** |
| `components/discover/` | `surface.card` → `surface.workspace` | **Done** |
| `components/documents/` | Bare `Card` → `surface.workspace` (Mission 31) | **Done** |
| `components/import/` | Bare `Card` → `surface.workspace` (Mission 31) | **Done** |
| `components/jobs/` | `surface.card` → `surface.workspace` | **Done** |
| `components/library/` | `surface.card` → `surface.workspace` | **Done** |
| `components/settings/` | Consolidated 4 sections → `SettingsSection`; workspace surfaces | **Done** |
| `components/vault/` | Bare `Card` → `surface.workspace` (Mission 31) | **Done** |
| `components/workspace/` | (layout only, Mission 09) | **N/A** |
| `app/blog/` | `surface.marketing` | **Done** |
| `app/kitchen-sink/` | Three-family reference page | **Done** |

## Consolidation

- **Added:** `SettingsSection` — replaces duplicated `section` + `surface.workspace` + heading boilerplate in 4 settings files.
- **Added:** `Surface` + `surfaceVariants` — single CVA source (replaces ambiguous `surface.card`).
- **Removed:** `surface.card` token usage (deprecated alias remains → workspace).

## Lint

- `eslint-rules/no-raw-color-literal.mjs` — bans `#hex` in feature components (wired in `lint:strict`).

## Production visibility

- `/kitchen-sink` — `robots.ts` disallow; excluded from `marketingSitemapPaths` (test added).

## Deferred

- Tailwind semantic colors (`amber-600`, etc.) for status — acceptable; not raw hex.
- `Card` + `surface.workspace` double-wrap in admin/analytics — structural; migrate to `<Surface>` in Mission 22 perf pass if needed.
