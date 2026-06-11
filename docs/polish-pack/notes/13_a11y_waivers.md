# Accessibility waivers — Mission 13

**Updated:** 2026-06-11

## Automated e2e disabled rules

| Rule | Impact | Rationale |
|------|--------|-----------|
| `color-contrast` | serious | Validated at **token** level (`globals.css` `--muted-foreground` darkened/lightened). Marketing specs use the same waiver since Mission 07. |
| `region` | moderate | Closed `CommandDialog` mounts sr-only header nodes in the document root; content is inside `role="dialog"` when open. Axe best-practice false positive on Base UI portal pattern. |

## Fixes landed (no waiver)

| Issue | Fix |
|-------|-----|
| `nested-interactive` on queue import | Controlled `Dialog` + plain `Button` opener (no nested trigger) |
| Unlabeled file inputs | `aria-label` on `FileUpload` + library resume input |
| Chart accessibility | `ChartAccessibleFigure` with sr-only data table |
| Run stream spam | `RunStreamAnnouncer` for checkpoints/status; log is `role="log"` without `aria-live` |
| Command palette crash on open | `CommandDialog` wraps children in `<Command>` (cmdk context required) |
| Command palette title | `DialogHeader` moved inside `DialogContent` |
| Analytics tabs | `aria-controls` + `tabpanel` ids |

## Manual follow-ups

- Full keyboard golden path with live API + fixture run (Mission 26).
- NVDA spot-check on `/queue` and `/runs/[id]` with real data.
