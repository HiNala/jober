# Responsive findings — Mission 14

**Updated:** 2026-06-11

Per-surface targets: marketing/auth **fully designed** at 375/768/1024/1440; app editorial **usable ≥768**, **scrollable at 375**; run console **tabbed Work|Canvas &lt;1024**.

| Route / area | 375 | 768 | 1024 | 1440 | Resolution |
|--------------|-----|-----|------|------|------------|
| Marketing header | Was cramped, no menu | OK | OK | OK | `MarketingMobileNav` sheet; CTAs `min-h-11`; desktop links `lg:flex` |
| Home hero / bento | Body overflow | OK | OK | OK | `overflow-x-clip` on shell + `html`; `break-words` on demo terminal; fill-diff scroll |
| Pricing comparison table | Horizontal risk | OK | OK | OK | `overflow-x-auto` + `min-w` on table |
| Auth split layout | Compact brand strip | OK | Side panel | OK | Existing `lg:grid-cols-2` (Mission 06) |
| Workspace nav rail | Icon rail wasted space | Same | Full rail | Full rail | Nav panel **hidden** when `≤1023px`; `MobileNav` `lg:hidden` |
| Command palette (touch) | No ⌘K | Same | Keyboard | Keyboard | Search icon `size-11` trigger `lg:hidden` |
| Queue table | Wide columns | Usable | OK | OK | Horizontal scroll + **sticky** checkbox + company columns |
| Run console | Stack | Tabs | Side canvas | 3-pane | `RunOpsDeskShell` Work\|Canvas tabs; canvas drawer removed on narrow |
| Viewport meta | — | — | — | — | Explicit `viewport` export in root layout |
| E2e overflow | — | — | — | — | `responsive-smoke.spec.ts` at 375×812 and 768×1024 |

## Follow-ups (out of scope)

- Card-list fallback for queue at 375 (table scroll + sticky deemed sufficient).
- Pixel-perfect admin/analytics on phone.
- PWA / touch gestures.
