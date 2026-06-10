# Product Design, Positioning & Landing Page Audit — Jober

**Audit date:** 2026-06-10
**Inputs:** repository code and docs, `docs/architecture/product.md`, `docs/screenshots/UI-REVIEW.md` (23 production screenshots dated 2026-06-10), marketing routes in `apps/web/src/app/`, pricing/plan logic in `apps/api/src/jober_api/routers/billing.py`.
**Limitation:** external browsing was not used for this audit. Competitor analysis below relies on the production-screenshot review already in the repo (which explicitly benchmarks against Hyper Agents, Figma, and 21st.dev), the product doc, and standard SaaS/devtool heuristics. Where a claim about a competitor would require live verification, it is phrased as a heuristic, not a fact.

---

## 1. Product hypothesis

Jober is a **human-in-the-loop application autopilot**: it does the repetitive 95% of applying to jobs (extract, tailor, fill, attach, verify) and deliberately reserves the final submit for the human. Its bet is that *assisted* high-quality volume beats both manual application grinding and fully automated "auto-apply" bots — which ATSs increasingly detect and penalize, and which produce low-quality spray.

## 2. Target user hypothesis

- **Primary (today):** technically sophisticated job seekers in tech roles running a high-volume search from a structured tracker — the founding user (Brian, AI engineer / full-stack) is the archetype. Comfortable with spreadsheets, willing to self-serve, allergic to spam-bot tools.
- **Secondary (plan-implied):** the same persona at Pro scale (500 runs/mo), possibly career coaches or job-search "operators" running structured pipelines.
- **Not the user:** passive job seekers wanting one-click mass apply; enterprises.

## 3. Core user problem

Applying well at volume is brutal: each application means re-typing the same profile into a different ATS, tailoring a letter, attaching the right files, and tracking status — ~20–40 minutes each, ×155 tracked leads. Quality and volume trade off directly. Existing auto-apply tools solve volume by destroying quality and risking ATS penalties.

## 4. Primary value proposition

**"High-volume applications without the volume look."** Jober compresses each application to a 1–2 minute review-and-submit while *increasing* quality (tailored letter, verified completeness, fill diff you can read). The trust mechanics — watchable browser, masked diffs, never-bypass-CAPTCHA, never-fabricate-sensitive-answers — are the product, not compliance fine print.

## 5. Jobs-to-be-done

1. "When I find 20 promising roles, get me from queue to submitted with my standards intact, without 10 hours of typing."
2. "When a form asks the same 40 questions again, answer them from my vault so I never re-type them."
3. "When a letter is needed, draft one grounded in *my* resume and *this* job that I'd actually sign."
4. "When something goes wrong (login wall, weird form), tell me exactly where and what to do — don't silently fail."
5. "Keep my tracker spreadsheet alive — statuses round-trip back out."
6. "Show me what was filled before anything is submitted, so I stay accountable for every application."

## 6. Current positioning assessment

The positioning substance is **strong and genuinely differentiated** (review-before-submit, no-stealth policy, BYOK LLM, first-party-only analytics, self-hostable posture) — but the *presentation* undersells it. Per UI-REVIEW: the marketing site reads "indistinguishable from hundreds of AI SaaS landings" (Geist font, teal eyebrow, blue CTA, identical shadcn cards). The honest-automation stance — the most defensible claim — is stated in copy but not *demonstrated* visually. The product's best proof (the live run console with masked fill diffs) barely appears on the marketing site as a static mockup.

## 7. Homepage and landing page assessment

Route: `apps/web/src/app/page.tsx` + `components/marketing/`. From UI-REVIEW screenshot 01:

- **Good:** clear funnel (eyebrow → headline → dual CTA → education → conversion); the application-preview + terminal mockup is the best brand asset; "human-in-the-loop" lands without jargon.
- **Issues:** hero mockup is static (no live-typed terminal or loop); three-up feature row gives equal weight to unequal claims — "review before submit" (the differentiator) gets the same card as table-stakes features; social proof is visibly placeholder (generic titles, no avatars/logos); consent banner overlaps the footer CTA on first paint.

## 8. Messaging hierarchy

Recommended hierarchy (current site approximates 1–2 then flattens):

1. **What:** "Apply to every job on your list — at your quality bar."
2. **How it's different:** "You review and submit. Always." (the trust mechanic, elevated visually, not just textually)
3. **Proof:** live/looped run console showing extract → fill → diff → verify
4. **Mechanics:** vault, letters, batches, recovery (feature tier)
5. **Trust details:** no CAPTCHA bypass, no fabricated answers, no third-party trackers, BYOK
6. **Conversion:** Free plan with concrete limits (20 runs/mo), honest Pro waitlist

## 9. Information architecture

Marketing IA (`/`, `/features`, `/how-it-works`, `/pricing`, `/faq`, `/blog`, legal) is conventional and fine. App IA (dashboard / queue / discover / library / search / settings / analytics / admin) matches user mental models per UI-REVIEW. Issues: `/documents` and `/vault` exist only as redirects (verify no nav or docs link them as destinations); `/search` vs `/discover` overlap needs a one-line distinction in nav tooltips or consolidation rationale; `/kitchen-sink` must not be linked or indexable in production.

## 10. Visual design assessment

From UI-REVIEW (adopted as the authoritative visual audit):

- Coherent dark navy/charcoal system with readable contrast and monospace terminal accents — a solid base.
- **Single-card-language problem:** one `Card` treatment serves marketing bento, data tables, and terminal surfaces. Needs three deliberate component families.
- No distinctive brand signature; recommendation is **one** sparing signature (mesh gradient hero, animated grid, or agent-orb) on marketing + auth only.
- Outline Lucide icons at low contrast don't anchor memory; pricing typography has no anchoring drama; auth pages float on a void with no brand moment or trust strip.

## 11. Interaction design assessment

- **Strong in-app:** ops-desk split pane on run surfaces, keyboard shortcuts, scrub timeline, checkpoint resolve actions.
- **Weak:** bottom "Describe what you want…" bar pasted onto every in-app page (should be ⌘K palette + contextual prompts); identical split layout on non-run pages dilutes the run console's specialness; motion tokens exist (`lib/design/motion.ts`) but marketing surfaces underuse them (static hero, no stagger, no chart draw-in); FAQ accordions lack open affordance animation.

## 12. Conversion path assessment

`/` → `/signup` → `/dashboard`. Friction points, in order of damage:

1. **Verification email never arrives** (not configured) — a signup-killing defect, worse than any visual issue.
2. First-run dashboard is empty with dev-flavored guidance — no "import your tracker" or sample-data moment to reach the aha (a completed dry-run) fast.
3. Consent banner interrupts before value is shown.
4. Pricing: Pro is a dead "coming soon" card with equal visual weight to Free — wasted intent; capture it with a waitlist email instead.
5. UTM attribution and CTA `feature.use` events exist (Mission 29/30) — good; verify they survive the consent redesign.

## 13. Trust, credibility, and proof assessment

Trust *mechanics* are world-class for the category; trust *signals* are weak: placeholder-looking testimonials, no usage numbers, no founder story (the "built for my own 155-lead search" origin is a genuinely credible asset — use it), draft legal pages, and no security/privacy summary page distilling the threat model into user language. The strongest available proof — real run artifacts, fill diffs, failure reports — is unused on marketing surfaces.

## 14. Competitor / inspiration analysis

*(Heuristic where live verification was unavailable; quality bars are taken from `docs/screenshots/UI-REVIEW.md`, which set them deliberately.)*

- **21st.dev (inspiration, not competitor):** the bar for distinctive component craft — bento asymmetry, border-beam accents, depth, purposeful motion. Lesson: one or two signature components, used sparingly, beat a re-theme of everything.
- **Hyper Agents (inspiration):** the bar for "agent-native premium dark product" — live terminal typing, mono eyebrows, the product visibly *doing work* on the landing page. Lesson: Jober's run console should be the hero, looping, not a static PNG.
- **Figma (inspiration):** typographic precision, confident whitespace, "try sample file" onboarding. Lesson: empty states as onboarding; pricing with a real feature table.
- **Auto-apply bots (direct competitors — LazyApply/Simplify-class tools, inferred category):** compete on volume and one-click promises. Jober must *not* out-volume them; it wins on "applications that look like you, at scale" and on ATS-safety honesty. Generic AI-SaaS styling makes Jober look like them — the visual differentiation is strategically load-bearing, not cosmetic.
- **Spreadsheet + manual (the real incumbent):** Jober's import/round-trip respects this workflow rather than replacing it — keep that front and center; it's a moat against tools that demand workflow migration.

## 15. Differentiation opportunities

1. **"Watch it work" as brand:** the live canvas (SSE screenshots, terminal) is unique demo material; loop it in the hero and the features bento.
2. **The fill diff** as a marketing artifact — no competitor shows users a redacted diff of what was entered on their behalf.
3. **Honesty stance** ("We pause at CAPTCHAs. On purpose.") as a headline, not a footnote.
4. **Privacy-first analytics** (no GA/Segment) and **BYOK LLM** for the technical persona.
5. **Founder-operator story** with real numbers from Brian's own search.

## 16. Overlap, confusion, or generic messaging risks

- Looking like an auto-apply bot (category contamination) — the #1 messaging risk.
- "AI agent" framing without specifics reads as hype to the exact persona Jober targets.
- `/search` vs `/discover` naming overlap in-app.
- "Coming soon" Pro card reads as abandonment if it persists for months.
- Generic shadcn styling signals "vibe-coded weekend project," contradicting the reliability claims.

## 17. Recommended positioning direction

**Category:** assisted application autopilot (own the term; refuse "auto-apply").
**One-liner:** "Apply to every job on your list — at your quality bar. You review and submit. Always."
**Pillars:** (1) Quality at volume, (2) You stay in control (review-before-submit, diffs, checkpoints), (3) Honest automation (no CAPTCHA bypass, no fabricated answers), (4) Your data stays yours (vault encryption, BYOK, no trackers).
Non-direction: do not chase recruiters, enterprises, or "fully autonomous" claims.

## 18. Recommended homepage/landing page structure

**Owner design direction (recorded 2026-06-10, binding):** Linear-style focus — centered hero composition with the **product preview in the center of the hero**, larger navigation text and a generally larger, more confident type scale, calm surfaces, elegant restrained animation. Source component patterns (animated hero, border-beam CTA, bento cells) from 21st.dev, v0, and comparable high-quality libraries — always adapted onto Jober's tokens, never pasted.

1. Hero (Linear-style): centered copy — mono uppercase eyebrow, tightened H1 (-0.02em, weight 600) at a generous size, one-line subhead, dual CTA (Start free / Watch a run) — with the **looping run-console product preview centered directly beneath**, full-width-ish with subtle radial gradient/brand signature behind it; nav above uses larger, fewer, focused text items.
2. Trust strip: "Review-before-submit · No CAPTCHA bypass · No third-party trackers · BYOK".
3. Differentiator block: "review and submit" as a 2× bento cell with embedded fill-diff visual; other features 1×.
4. How-it-works: 4-step stepper with gradient connector, step 3 (watch/review) visually dominant with mini browser chrome.
5. Proof: founder story + real (anonymized) run stats; avatar stack when real testimonials exist — remove placeholders until then.
6. Pricing teaser: Free with concrete limits; Pro as inline waitlist capture.
7. FAQ (objection-ordered: "Is this a bot?", "Will ATSs flag me?", "Where does my data live?").
8. Final CTA + footer (legal, privacy, acceptable use).

## 19. Recommended product design principles

1. **Linear-grade typography and focus:** larger nav text, generous heading scale, fewer-but-bigger words per surface; whitespace does the hierarchy work. Micro-interactions on every interactive element where they communicate state — sourced from best-in-class references (21st.dev, v0, Aceternity/Magic UI patterns) and rebuilt on tokens.
2. **Three component families, never blended:** marketing bento / workspace data surfaces / terminal-live surfaces.
2. **Split-pane is earned:** only run/watch surfaces get the ops-desk layout; everything else is editorial full-width.
3. **Motion from tokens only** (`lib/design/motion.ts`, enforced by `pnpm check:motion`); every animation states purpose; reduced-motion always honored.
4. **Empty states onboard:** every empty state names the next action and offers sample data; never dev copy.
5. **Trust is shown, not told:** diffs, checkpoints, and redaction visible in-product and in marketing.
6. **One brand signature, used sparingly** on marketing + auth only.
7. **Honest states:** coming-soon, stub-LLM mode, and unverified-email states are explicitly labeled, never silently degraded.

## 20. Non-goals and feature-creep guardrails

Do **not** build during this pack: new ATS adapters, recruiter/agency features, mobile apps, public API, CMS-backed blog, A/B testing infra, additional LLM providers, Chrome extensions, job-board scraping beyond existing discovery, team/multi-seat features, or Stripe checkout *unless* the owner explicitly green-lights monetization (waitlist capture is the in-scope alternative). Any mission proposing surface-area growth must cite a broken flow or an acceptance criterion that requires it.

## 21. Acceptance criteria for a polished product experience

1. A first-time visitor can state what Jober does and how it differs from auto-apply bots after the hero + trust strip alone (validate with the 5-second test against the re-captured `01-home.png`).
2. No production surface contains placeholder testimonials, dev copy, or "coming soon" cards without a capture mechanism.
3. The run console (live or looped capture) appears on the landing page; the fill diff appears somewhere in the marketing funnel.
4. All seven "generic" patterns in `docs/screenshots/UI-REVIEW.md` are resolved, verified by re-capturing all 23 screenshots with `apps/web/scripts/capture-screenshots.mjs` and updating `UI-REVIEW.md` with a closure note per item.
5. Consent UX appears at most once per device as a bottom sheet and never overlaps primary content.
6. Auth pages carry the brand signature and a trust strip.
7. Signup → verified → first dry-run completes without leaving the product or hitting a dead end.
8. Design Council gate (MASTER_PLAN §10): every reworked surface scores ≥18/20 with no zeros.
