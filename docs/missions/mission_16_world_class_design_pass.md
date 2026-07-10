# Mission 16 — World-Class Design Pass

## Task list

### Design system
- [x] Consolidated tokens in `globals.css` + `apps/web/src/lib/design/tokens.ts`
- [x] Motion layer in `lib/design/motion.ts` with `prefers-reduced-motion` in CSS

### Surfaces
- [x] Loading / empty / error / success states (`page-states.tsx` skeletons)
- [x] Run console polish (calm screenshot, event stream, checkpoint card)
- [x] Dashboard Tufte pass (`NeedsAttentionBanner`, metric emphasis)
- [x] Profile vault Wroblewski pass (labels, fieldsets, masked sensitive values)
- [x] Review & submit five-second scan layout
- [x] Marketing hero — honest you-in-the-loop positioning

### Quality
- [x] Skip links, landmarks, table captions, `role="log"` on event stream
- [x] Run console route code-split (`next/dynamic`)
- [x] Copy pass: run, checkpoint, batch terminology

## Acceptance criteria
- [x] Design Council ≥18/20 per surface in `design-review.md`
- [x] Reduced-motion respected globally
- [x] `lint:strict` / `typecheck` / `build` green

## Mission 99
- [x] Settings panel wired to `/api/settings/policy` + `/api/billing/usage` (was stub)
- [x] Web gates green (`lint:strict`, `typecheck`, `build`, vitest 12)
- [x] API `ruff` + `mypy` green; full pytest requires CI Postgres locally
- [x] Design Council scores in `design-review.md` (incl. settings addendum 19/20)
- [x] Release tagged `v0.16.0-design`; M99 commit pushed to `origin/main`

---

## Residual perfection (2026-07) → Missions 35–36, 39

M16 established tokens, states, and Design Council discipline. **2030 bar is higher** and visually re-anchored:

| Residual gap | Owner mission |
|--------------|---------------|
| Near-black Hyperagent shell + new primitives | **M35** |
| Marketing no longer generic light AI SaaS | **M36** |
| App command center (not merely polished v1 chrome) | **M39** |
| Design Council target ≥19/20 | All perfection missions |
| Binding references: Hyperagent, Grok, Linear, 21st.dev | `design-north-star-2030.md` |
