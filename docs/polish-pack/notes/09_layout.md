# Mission 09 — Workspace layout discipline

## Layout modes

| Mode | Routes | Shell |
|------|--------|-------|
| `ops-desk` | `/runs/[id]` | Nav + center work + resizable canvas |
| `editorial` | All other `(app)` routes | Nav + full-width content (no canvas pane) |

Declared in `apps/web/src/lib/workspace/layout.ts`, consumed by `app-chrome.tsx`.

## Command palette

- **Shortcuts:** ⌘K / Ctrl+K, ⌘/ / Ctrl+/
- **Component:** `workspace-command-palette.tsx` (cmdk `CommandDialog`)
- **Actions:** global nav (`APP_NAV`) + page-contextual (queue import/export, run canvas/focus)
- **Queue import:** palette navigates to `/queue?import=1`; page opens import dialog then strips query

## Removed

- `workspace-command-bar.tsx` — non-functional bottom “Describe what you want…” bar

## Persistence

- `jober-workspace-v1` localStorage: nav/canvas prefs only on ops-desk surfaces
- `commandPaletteOpen` and `focusMode` are ephemeral (not persisted)

## Validation

```bash
cd apps/web && pnpm typecheck && pnpm lint:strict && pnpm test && pnpm build && pnpm check:motion
pnpm test:e2e
```

Re-capture screenshots 14–23 after deploy.
