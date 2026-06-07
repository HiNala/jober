# Mission 17 — Application Shell v2 (Three-Pane)

## Task list
- [x] Three-pane layout with draggable resize handles (`react-resizable-panels`)
- [x] Collapsible left nav with sections, badges, keyboard toggle, persisted state
- [x] Center command bar with Plan/Execute toggle and model selector (`GET /api/llm/config`)
- [x] Right canvas with view-mode toggle, filmstrip, corner status badge
- [x] Responsive: narrow widths → canvas drawer; nav auto-collapses
- [x] Layout state persisted via `localStorage` (`useDefaultLayout` + `zustand/persist`)
- [x] Keyboard: ⌘/Ctrl-B nav, ⌘/Ctrl-\\ canvas, ⌘/Ctrl-/ focus command bar; Shift-⌘/Ctrl-F focus mode
- [x] Focus mode hides side panels for distraction-free center column

## Acceptance criteria
- [x] Resize handles with min/max; canvas defaults ~48% width
- [x] Nav collapse + layout survives reload
- [x] View-mode toggle + filmstrip selection
- [x] Keyboard operability; `prefers-reduced-motion` via existing motion tokens
- [x] Design Council scores in `design-review.md`

## Mission 99
- [ ] Run iteration loop after M17
