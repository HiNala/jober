# Jober Design North Star — 2030 Premium Product

**Status:** Binding for Missions 35–45  
**References:** Hyperagent app shell (thread/canvas split), Grok.com dark product surfaces, Linear typography, 21st.dev component craft, Figma whitespace discipline  
**Owner screenshots:** Hyperagent new-thread, live thread + canvas, human-checkpoint modal; Grok SuperGrok Heavy hero + unlock modal  

---

## 1. Product thesis (unchanged, elevated)

Jober is the **assisted application autopilot**: discover perfect-fit jobs, tailor resume + cover letter per role, fill every form field from the vault, verify readiness, and hand the user a one-tap **Approve / Send** — never spray-and-pray, never CAPTCHA bypass, never fabricated sensitive answers.

The UI must make that thesis *visible*: calm dark command center, live work visible, human checkpoints first-class, not buried.

---

## 2. Visual DNA — composite of references

| Source | Steal | Do not steal |
|--------|--------|--------------|
| **Hyperagent** | Near-black app chrome; left icon+label rail; recent-work list; center task stream; right live canvas; soft multi-hue ambient gradient on canvas; Plan + send composer; Live pill; human multiple-choice checkpoint cards | Generic “AI chat only” — Jober is ops + forms + docs |
| **Grok** | Centered empty-state power (“Let’s get to work” / SuperGrok); single primary input; floating beta/promo cards; cinematic unlock modal with feature cards | Cosmic art overload on every page |
| **Linear** | Focused hierarchy, larger type, confident whitespace, fewer words | Cold enterprise density without warmth |
| **21st.dev / Magic UI** | Border-beam CTAs, bento asymmetry, depth, purposeful motion | Pasted components that ignore tokens |

### Palette (app default — pure dark)

| Token | Value direction | Use |
|-------|-----------------|-----|
| `--background` | Near black `oklch(0.11–0.13 0.015 260)` | Page canvas |
| `--sidebar` | Slightly elevated `oklch(0.14–0.16 0.02 260)` | Nav rail |
| `--card` | `oklch(0.17–0.19 0.02 260)` | Panels, composer |
| `--foreground` | Soft white `oklch(0.96 0.01 260)` | Primary text |
| `--muted-foreground` | `oklch(0.62–0.68 0.02 260)` | Secondary |
| `--primary` | Soft blue-violet (not neon) | Actions, focus rings |
| `--accent-live` | Soft teal/green pulse | LIVE badges, success |
| `--canvas-ambient` | Multi-stop soft gradient (lavender → warm cream → cool blue) | Live canvas idle/loading |
| `--border` | White 8–12% | Hairlines |

Marketing may use a **dark-first** landing (matching Hyperagent/Grok) with optional light marketing variant later. Default 2030 ship: **dark marketing + dark app**.

### Typography

- **UI sans:** Geist Sans (or Inter as fallback) — larger nav (≥17px), hero H1 clamp 2.5–4.5rem, tracking -0.02em to -0.03em  
- **Mono:** Geist Mono for run IDs, terminal, ATS labels, field keys  
- **Hierarchy rule:** one primary action per viewport; secondary actions ghost/outline  

### Motion

- Tokenized only (`lib/design/motion.ts`); lint-enforced  
- Skeleton shimmer on loading panels (Hyperagent-style rounded bars)  
- Live pulse on LIVE badge  
- Canvas ambient gradient slow drift (respects `prefers-reduced-motion`)  
- Stagger on hero and empty states  
- **No** gratuitous parallax on data tables  

### Brand signature (one only)

Soft **canvas ambient orb/gradient** (lavender–peach–blue) behind live preview surfaces + marketing hero product mock. Used on: marketing hero, auth shell, run canvas idle, empty command center. Nowhere else.

---

## 3. Layout systems

### A. Marketing shell

```
[Logo]  Features  How it works  Pricing  FAQ     [Log in] [Start free]
──────────────── hero (centered or split) ────────────────
ambient gradient + product preview (run console mock)
trust strip → differentiator bento → how-it-works → proof → pricing → FAQ → CTA band → footer
```

### B. Auth shell

Full-bleed dark with brand signature; centered card; trust strip (Review-before-submit · Encrypted vault · No CAPTCHA bypass); Google + email paths honest (hide disabled Google).

### C. Workspace shell (Hyperagent-inspired)

```
┌──────── sidebar ────┬──────── main ──────────────────────┬── optional canvas ──┐
│ Logo                │ Breadcrumb / title / Live pill     │ Ambient or live UI  │
│ New apply / search  │                                    │                     │
│ ───────────────     │ Content OR chat-like run stream    │ Screenshots / docs  │
│ Dashboard           │                                    │                     │
│ Discover            │                                    │                     │
│ Queue               │                                    │                     │
│ Documents           │                                    │                     │
│ Library / Vault     │                                    │                     │
│ Analytics           │                                    │                     │
│ ───────────────     │ Composer: “What’s the task?”       │                     │
│ Settings            │ [+] [attach]  [Plan ▾]  [↑ send]   │                     │
│ Admin (rbac)        │                                    │                     │
│ User pill           │                                    │                     │
└─────────────────────┴────────────────────────────────────┴─────────────────────┘
```

**Rules:**

1. **Split canvas is earned** — only `/runs/[id]`, review-and-submit, and document side-by-side preview. Elsewhere: editorial full-width.  
2. **Command palette (⌘K)** is global; optional contextual composer on dashboard/discover only (not a fake AI bar on every page).  
3. **Human checkpoints** use Hyperagent-style modal cards: clear question, radio options, Skip / Send response.  
4. **Empty states** are Grok-power moments: large headline, single input or primary CTA, 3–5 suggestion chips.

### D. Mobile

- Collapsible sidebar → bottom tab bar (Dashboard, Discover, Queue, Docs, More)  
- Run console: stacked (stream → screenshot → actions); landscape tablet restores split  
- Touch targets ≥44px; no hover-only critical actions  
- Marketing hamburger + full-screen sheet  

---

## 4. Component families (three tiers — keep)

| Family | Surfaces | Feel |
|--------|----------|------|
| **Marketing** | Landing, pricing, features | Bento, border-beam, larger type, ambient |
| **Workspace** | Tables, settings, admin, library | Dense, quiet borders, calm |
| **Terminal / Live** | Event stream, screenshots, fill log | Mono, inset, LIVE pulse |

New 2030 components to introduce (M35+):

- `CommandComposer` — Plan dropdown + send (Hyperagent)  
- `AmbientCanvas` — soft gradient loading/idle  
- `CheckpointCard` — multi-option human handoff  
- `UnlockModal` — post-upgrade / Pro success (Grok-style feature cards)  
- `SkeletonStream` — message-shaped loading bars  
- `StatusLivePill` — Live / Opus-style model tier display (show plan or “Review mode”)  
- `SuggestionChips` — empty-state quick starts  
- `ApproveSendBar` — sticky review footer: Approve & submit / Edit / Pause  

---

## 5. Core user loops (product perfection)

### Loop 1 — Discover perfect jobs
Search boards + upload XLSX → fit score → accept to list → library  

### Loop 2 — Prepare materials
Per job: tailored resume variant (human-reviewed) + cover letter → PDF/DOCX  

### Loop 3 — Apply with control
Open run → extract → fill → upload → verify → **diff** → Approve/Send → confirmation archive  

### Loop 4 — Operate
Batch queue, cooldowns, recovery, analytics, admin health  

Every loop must work on mobile, with empty/loading/error states that onboard, and zero “coming soon” dead ends for promised features.

---

## 6. Quality bar (non-negotiable)

- Design Council ≥19/20 per surface (raise from 18)  
- Zero lint / typecheck / mypy / ruff failures  
- Axe clean on marketing, auth, core app routes  
- Lighthouse: marketing LCP < 2.5s on broadband; CLS < 0.1  
- Golden path e2e green in CI  
- No fake buttons (Google disabled → hidden; Pro → checkout or honest waitlist, not both)  
- Full responsive matrix: 375, 768, 1024, 1440  

---

## 7. Copy voice

- Confident, short, human.  
- Prefer “You review and submit. Always.” over “AI-powered automation.”  
- Never sound like LazyApply/mass-apply bots.  
- Error copy names the next action.

---

## 8. Explicit non-goals (still)

No CAPTCHA bypass, no stealth fingerprinting, no mass scrape beyond user-selected boards, no enterprise multi-seat v1, no public API v1, no mobile native apps (responsive web only).

---

## 9. Asset inventory (generate or build in code)

| Asset | Method | Mission |
|-------|--------|---------|
| Hero ambient abstract | `image_gen` | 36 |
| Product preview still (decorative) | code preferred (component) | 35–36 |
| Pro unlock modal illustration | `image_gen` | 38 |
| Empty-state ambient | `image_gen` | 39 |
| OG/social share image | code or gen | 36 |

Prefer **code-built UI chrome** for any mock that must show real product copy (run console, fill diff). Use generated art only for ambient/atmosphere.
