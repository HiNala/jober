# Jober UI screenshots

Full-page captures for visual QA and design review.

## Where to look

| Folder | Contents |
|--------|----------|
| [`prod/`](prod/) | **23 PNGs** from live production (`web-production-29902.up.railway.app`) |

Open any `.png` directly in your file explorer or IDE image preview.

## File index

### Marketing & auth (01–13)

| File | Route |
|------|-------|
| `01-home.png` | `/` |
| `02-features.png` | `/features` |
| `03-how-it-works.png` | `/how-it-works` |
| `04-pricing.png` | `/pricing` |
| `05-faq.png` | `/faq` |
| `06-blog.png` | `/blog` |
| `07-blog-welcome-to-jober.png` | `/blog/welcome-to-jober` |
| `08-privacy.png` | `/privacy` |
| `09-terms.png` | `/terms` |
| `10-acceptable-use.png` | `/acceptable-use` |
| `11-login.png` | `/login` |
| `12-signup.png` | `/signup` |
| `13-forgot-password.png` | `/forgot-password` |

### In-app (14–23)

| File | Route |
|------|-------|
| `14-dashboard.png` | `/dashboard` |
| `15-queue.png` | `/queue` |
| `16-discover.png` | `/discover` |
| `17-library-resumes.png` | `/library?tab=resumes` |
| `18-library-letters.png` | `/library?tab=letters` |
| `19-library-jobs.png` | `/library?tab=jobs` |
| `20-library-runs.png` | `/library?tab=runs` |
| `21-search.png` | `/search` |
| `22-analytics.png` | `/analytics` |
| `23-settings.png` | `/settings` |

## Regenerate

```bash
cd apps/web
PLAYWRIGHT_SKIP_WEB_SERVER=1 \
PLAYWRIGHT_BASE_URL=https://web-production-29902.up.railway.app \
API_URL=https://api-production-4b5b.up.railway.app \
node scripts/capture-screenshots.mjs
```

## Design review

See **[UI-REVIEW.md](UI-REVIEW.md)** for per-screenshot UX notes and a prioritized upgrade plan (Hyper Agents / Figma / 21st.dev bar).
