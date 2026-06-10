# Changelog

## [0.1.0] — 2026-06-10 — Launch

First production-ready release of Jober: assisted job-application autopilot with human-in-the-loop review.

### Highlights

- **Stack:** Next.js web, FastAPI api, Celery/Playwright worker, Postgres, Redis, S3-compatible storage
- **Railway:** Staging + production layout, migrate-on-deploy, health probes, smoke scripts
- **Ops:** Admin dashboard with budget, queue depth, circuit-breaker attention; webhook alerts
- **Safety:** Policy CI, redacted logs, production secret guards, review-before-submit default

### Deploy

See [docs/runbooks/deploy.md](docs/runbooks/deploy.md) and [docs/runbooks/launch-checklist.md](docs/runbooks/launch-checklist.md).

### Post-launch

Schedule a 7-day review: reliability (run success rate), LLM cost vs budget, signup → first batch funnel in admin analytics.
