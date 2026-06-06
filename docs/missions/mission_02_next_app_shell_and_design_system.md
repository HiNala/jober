# Mission 02 — Next.js App Shell & Design System

## Task list
- [x] Scaffold via `create-next-app` + shadcn/ui primitives (committed separately).
- [x] Design tokens in `globals.css` + `docs/architecture/design-tokens.md`.
- [x] App shell: sidebar, top bar, worker health pill (`/readyz`), sonner toaster.
- [x] API client + TanStack Query; Zustand for UI chrome state.
- [x] `useRunStream` SSE stub (Mission 11).
- [x] Loading / empty / error shells on all app routes.
- [x] `typecheck`, `lint:strict`, `build`; CI web job.
- [x] Accessibility: landmarks, `aria-current`, keyboard focus, `prefers-reduced-motion`.
- [x] Iteration: `/kitchen-sink` component catalog.

## Acceptance criteria
- [x] `pnpm build` succeeds; typecheck + lint:strict clean; CI green.
- [x] Health pill polls live API `/readyz`.
- [x] Animations honor `prefers-reduced-motion`.
- [x] Design Council ≥18/20 on shell + landing.
