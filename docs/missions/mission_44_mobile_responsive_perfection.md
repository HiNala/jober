# Mission 44 — Mobile & Responsive Perfection

> **Phase:** Perfection pack  
> **Depends on:** M36, M39–M43 (or parallelize late stages carefully)  
> **Run Mission 99 after**

## Purpose

Make Jober **flawless on every screen size**: marketing, auth, and core app journeys at 375 / 390 / 768 / 1024 / 1440. Touch-first patterns, no horizontal scroll bugs, run console usable on phone, bottom navigation where needed.

## Context

Polish 14 and responsive e2e exist. 2030 redesign (M35–43) will reintroduce regressions unless mobile is a first-class gate. Hyperagent/Grok references are desktop-heavy — Jober must invent excellent mobile ops UX.

## Scope

### In scope
- Marketing mobile polish (nav sheet, hero stack, pricing cards)
- Auth mobile
- App: bottom tab bar or equivalent for primary destinations
- Run console stacked mobile layout
- Discover/queue tables → card lists on small screens
- Document studio mobile basics
- Touch targets, safe areas, virtual keyboard
- Playwright mobile project green
- Visual screenshot set for mobile/

### Out of scope
- Native iOS/Android apps
- PWA offline apply (optional stretch only if time)

## Starting checklist
- [ ] Run `e2e/mobile-smoke.mobile.spec.ts` and `responsive-smoke.spec.ts` for baseline failures
- [ ] Device toolbar pass on staging for top 10 routes

## Tasks

### 1. Navigation
- [ ] Marketing: full-screen menu, focus trap, escape
- [ ] App: bottom tabs — Home, Discover, Queue, Docs, More (Settings/Vault/Analytics/Admin)
- [ ] Sidebar hidden on small; no double-nav

### 2. Critical flows
- [ ] Signup/login complete on 375px
- [ ] Import jobs / discover accept on mobile
- [ ] Run: stream → screenshot → checkpoint → approve scrollable sections
- [ ] ApproveSendBar thumb-reachable

### 3. Components
- [ ] Tables → responsive cards or horizontal scroll with sticky first column (prefer cards for queue)
- [ ] Modals: full-screen sheet on mobile
- [ ] Command palette full-screen mobile

### 4. QA matrix
| Width | Must pass |
|-------|-----------|
| 375 | marketing, auth, dashboard, queue, run stacked |
| 768 | tablet split for run if space |
| 1024 | desktop shell |
| 1440 | full canvas |

### 5. A11y
- [ ] Focus order on mobile nav
- [ ] No off-screen focusables
- [ ] Dynamic viewport `dvh` for composers

## Validation
```bash
cd apps/web && pnpm exec playwright test e2e/mobile-smoke.mobile.spec.ts e2e/responsive-smoke.spec.ts e2e/a11y-app.spec.ts e2e/a11y-marketing.spec.ts
# capture mobile screenshots into docs/screenshots/mobile/
```

## Acceptance criteria
- [ ] Zero critical layout bugs on matrix
- [ ] Golden path completable on iPhone-class viewport (fixture)
- [ ] Design Council mobile surfaces ≥19/20
- [ ] No horizontal page scroll on marketing home

## Production guidance
- Test on real iOS Safari + Android Chrome before launch cert (M45)
