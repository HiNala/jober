# Mission 18 — Live Canvas

## Task list
- [x] Live browser viewer from SSE `browser.screenshot` + named event listeners
- [x] Catch up to live + timeline scrub (range input)
- [x] Artifact gallery (grid) with trace/video/screenshot/dom tiles
- [x] Document + fill-diff + review surfaces in canvas
- [x] Filmstrip bound to run artifacts and timeline versions
- [x] Corner status badge (warnings / needs human)
- [x] Review-and-submit canvas with approve/submit controls
- [x] Empty/loading/error states per surface

## Acceptance criteria
- [x] Live browser updates via shared `useRunStream` (throttled server-side)
- [x] Artifacts open in canvas; trace links open Playwright viewer
- [x] Filmstrip + layers select versions; scrub syncs screenshot
- [x] Review surface shows letter + fill diff + readiness + submit
- [x] Design Council scores in `design-review.md`

## Mission 99
- [x] `apply-stream-event.test.ts` — fixture for named SSE screenshot/state updates
- [x] `liveFollowRef` — scrub no longer snaps back when new frames arrive
- [x] Filmstrip auto-selects latest artifact when run loads
- [x] Web gates + CI green (backend, web, policy)
- [x] Design Council M99 addendum in `design-review.md`
