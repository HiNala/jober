# Mission 19 — Motion & Micro-Interactions System

## Task list
- [x] Central motion tokens (durations, easings, distances) in `lib/design/motion.ts` + `globals.css`
- [x] Reasoning shimmer + streaming text reveal for agent output
- [x] Status pill choreography (`StatusPill`, timeline + console)
- [x] Command bar press/hover feedback (send, Plan/Execute, attach)
- [x] Canvas cross-fade, filmstrip expand, view-mode press
- [x] Resize handle + kanban grab affordances
- [x] Checkpoint attention enter + approve/deny press feedback
- [x] Route transitions, skeleton/empty micro-animations
- [x] `prefers-reduced-motion` + `motion-safe:` across surfaces
- [x] ESLint + `check:motion` guard for hard-coded durations

## Acceptance criteria
- [x] Shared tokens; lint/check flags raw `duration-*` in feature components
- [x] Reduced-motion: global CSS override + `motion-safe:` prefixes
- [x] Micro ≤200ms, view ≤500ms (enforced in `motion.test.ts`)
- [x] Design Council ≥18/20 in `design-review.md`
- [x] Vocabulary documented in `docs/architecture/motion.md`

## Mission 99
- [x] `EventStreamRevealTracker` — historical lines static; only new SSE lines animate
- [x] `StreamingText` + `ContentReveal` wired in run console
- [x] Web gates + CI green

## Iteration clause
- Screenshot crossfade uses opacity-only keyframe to avoid jank during live SSE.
- Advance to Mission 20 after M99.
