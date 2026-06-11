# Mission 07 — Landing page notes

**Date:** 2026-06-11

## Component sourcing

21st.dev / v0 browsing was unavailable in the execution environment. Patterns adapted from named references:

- **Centered Linear-style hero** — mono eyebrow, tightened H1, product preview beneath copy (positioning audit §18).
- **Animated terminal loop** — extended existing `ProductVisual` (Hyper Agents “watch it work” pattern).
- **Bento differentiator cell** — 2× dominant cell with embedded fill-diff table (21st.dev bento layout).
- **Border-beam CTA** — not added (bundle/motion budget); primary CTA uses existing `MarketingCtaLink` + tokens.

All motion via `lib/design/motion.ts` + `globals.css` keyframes (`jober-hero-float`, `motionHeroStagger`).

## 5-second test (operator, 2026-06-11)

**Prompt:** After hero + trust strip only, what does Jober do?

**Answer:** “Assisted job applications where you watch the agent fill forms and you approve before anything submits — not a spray-and-pray bot.”

**Pass** — differentiator (review-before-submit) clear without reading below the fold.

## Screenshot

`docs/screenshots/prod/01-home.png` — refresh post-deploy via `capture-screenshots.mjs`.

## Follow-ups

- Loop hero as captured video when a fixture run recording pipeline exists.
- Customer quotes when real permissioned testimonials exist (founder story stands in until then).
