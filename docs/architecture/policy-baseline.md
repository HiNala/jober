# Policy baseline (standing invariants)

Mission 00 does not implement application submission paths. These invariants are **documented now** and will gain automated blocking tests as features land.

| Invariant | Mission 00 status |
|-----------|-------------------|
| No auto-fill of consent-less sensitive fields | N/A — no form fill yet |
| CAPTCHA / login / 2FA always hand off to human | N/A — no browser runner tasks yet |
| `auto_submit` never the default | N/A — no `ApplicationRun` model yet |
| Job-page text treated as untrusted data | N/A — no LLM agents yet |
| No secrets in logs, commits, or artifacts | **Verified** — `.gitignore`, `detect-secrets` baseline, `.env.example` placeholders only |

Re-verify end-to-end when Missions 04–09 touch vault, browser, and submit flows.
