# Jober voice guide (Mission 27)

**Audience:** job seekers running structured, high-volume searches — technical enough to read a fill diff, allergic to spam-bot tools.

**Tone:** Confident, precise, zero hype. State what happens and what the user must do. Never blame the user ("oops"), never leak dev setup (`make seed`, env var names), never imply hidden automation.

## Principles

| Do | Don't |
|----|-------|
| Verb-first buttons: "Import spreadsheet", "Approve submit" | Vague CTAs: "Get started", "Learn more" (unless secondary) |
| Name the consequence: "Submit to Acme — this cannot be undone" | Cheerful filler without information |
| Human cause + next step on errors | Stack traces, env keys, or "contact your admin" |
| "Assisted applications", "review before submit", "you approve" | "AI agent", "auto-apply", "hands-free" |
| Honest limits: draft legal, stub LLM, email not live yet | Silent degradation or fake social proof |

## Approved positioning (audit §17)

- **Category:** assisted application autopilot — not auto-apply.
- **One-liner:** "Apply to every job on your list — at your quality bar. You review and submit. Always."
- **Pillars:** quality at volume · you stay in control · honest automation · your data stays yours.

## Microcopy patterns

- **Empty states:** name the next action ("Import your job tracker") — never dev commands.
- **Dropzones:** match file type in title and hint (`kind="resume"` → PDF/DOCX; `kind="spreadsheet"` → xlsx).
- **Checkpoints:** say what paused the run and the single action to continue.
- **Toasts:** past tense outcome + optional retry ("Import failed — check the file format and try again").

## Sweep log

| Route / surface | Issue | Fix | Status |
|-----------------|-------|-----|--------|
| `/queue` empty | `make seed` dev copy | `QUEUE_EMPTY` in `onboarding-copy.ts` (Mission 05) | Closed |
| Settings vault dropzone | Spreadsheet copy on resume upload | `FileUpload kind="resume"` (Mission 05) | Closed |
| Blog `posts.ts` | CMS scaffold comment | Neutral static-post comment | **M27** |
| Vault error | `VAULT_ENCRYPTION_KEY` dev message | User-facing retry copy | **M27** |
| Hero `/` | Off-positioning H1 | §17 one-liner + subhead constants | **M27** |
| Legal pages | No plain summary | `LegalDocument` "In short" box + draft banner | **M27** |
| `/` SEO | Missing `SoftwareApplication` JSON-LD | Added in `page.tsx` | **M27** |
| `/blog/[slug]` | Missing `BlogPosting` JSON-LD | Added in blog post page | **M27** |
| `robots.ts` | App routes crawlable | `ROBOTS_DISALLOW_PATHS` workspace prefix list | **M27** |
| Email templates | Minor clarity | Verification + reset copy pass | **M27** |
| OG images | No per-route image asset | Deferred — metadata title/description/canonical in place | Follow-up |

## Validation

- `grep -ri "make seed\|VAULT_ENCRYPTION\|CMS\|scaffold" apps/web/src` → clean (blog comment removed).
- Public routes: unique `title`/`description` via `marketingMetadata()` or `page.tsx` export.
- JSON-LD: `SoftwareApplication` `/`, `FAQPage` `/faq`, `BlogPosting` `/blog/*`.
- Re-capture `docs/screenshots/prod/` after deploy for visual proof-read.
