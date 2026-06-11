# Threat Model (Mission 14)

Personal-mode Jober: one operator, self-hosted stack, assisted job applications.

## Assets

| Asset | Location | Sensitivity |
|-------|----------|-------------|
| Vault EEO / sensitive answers | Postgres (`sensitive_eeo_answers`, Fernet) | Critical |
| Resume PDFs / cover letters | MinIO `resumes/`, `documents/` | High |
| Playwright storage state (site sessions) | MinIO `runs/{id}/storage-state.enc` | Critical |
| Run traces / screenshots | MinIO `runs/{id}/attempts/` | High (may contain PII) |
| LLM prompts (audit) | Postgres `llm_calls.redacted_*` | Medium (scrubbed) |
| Run / browser events | Postgres `run_events`, `browser_events` | Medium (scrubbed at write) |
| LLM / MinIO / vault keys | Env / secret store only | Critical |

## Trust boundaries

```
[Browser / Next.js]  --public API-->  [FastAPI]
                                         |
                    secrets never sent --+
                                         v
                              [Worker + Playwright]
                                         |
                         untrusted ATS HTML only as delimited data
                                         v
                              [Postgres] [Redis] [MinIO]
```

- **Trusted:** Operator, local `.env`, API process, worker process.
- **Untrusted:** All job-page HTML, form labels, accessibility trees, network responses from ATS hosts.
- **Semi-trusted:** Presigned MinIO URLs (short TTL, no bucket public read).

## Controls (Mission 14)

1. **Write-time redaction** — `jober_api.privacy.redaction` scrubs secrets/PII before `RunEvent`, `BrowserEvent`, and `LlmCall` persistence.
2. **Vault encryption** — Fernet at ORM layer for sensitive EEO JSON; no plaintext site passwords in DB.
3. **Storage state** — Playwright cookies encrypted in MinIO per run; not shared across runs; excluded from git.
4. **Policy gates** — CAPTCHA/login/2FA/sensitive fill require human checkpoints; injection fixtures in blocking CI.
5. **Retention** — Purge run, cleanup filters, export-all metadata, delete-all with confirmation phrase.
6. **Startup guard** — Production refuses boot with placeholder/missing `VAULT_ENCRYPTION_KEY` and `SECRET_KEY`.

## Encryption at rest (self-host)

| Layer | Mechanism | Operator action |
|-------|-----------|-----------------|
| Postgres | Volume encryption (host/cloud) | Enable LUKS / RDS encryption / Docker volume encryption |
| MinIO | Volume encryption + private bucket | `mc anonymous set none`; rotate `MINIO_*` creds |
| App secrets | Env / Railway secrets | Set `VAULT_ENCRYPTION_KEY`, `SECRET_KEY`; never commit |

## Explicit non-goals

We do **not** defend against:

- **Compromised host** — root on the machine can read `.env`, memory, and decrypted volumes.
- **Malicious operator** — personal mode has no multi-tenant isolation.
- **Determined ATS anti-bot** — pacing reduces load; we do not evade fraud detection.
- **LLM provider breach** — prompts are redacted/truncated before audit storage; live calls still leave the trust boundary.

## Session and CSRF (Mission 19)

Production uses **cross-origin** Railway web + API (`COOKIE_SECURE=true`, `SameSite=None`) so the browser sends session cookies on `credentials: include` fetches. That widens classic CSRF exposure versus `SameSite=Lax`.

| Control | Detail |
|---------|--------|
| Session storage | Redis; opaque `jober_session` + `jober_refresh` cookies (`HttpOnly`, `Secure` in prod) |
| CSRF | `CsrfMiddleware` double-submit on all mutating `/api/*` when session cookie present; exempt list in `PUBLIC_API_PREFIXES` (auth bootstrap, webhooks, analytics collector, waitlist) |
| Client | Web attaches `X-CSRF-Token` from `jober_csrf` cookie on mutations |
| Revocation | Logout and password reset/change revoke server-side sessions (`revoke_session` / `revoke_other_sessions` / `revoke_all_sessions`) |
| Rate limits | Redis counters on login/signup/reset; lockout after repeated failures |

See `docs/polish-pack/notes/19_auth_matrix.md` for the full cookie/CSRF matrix.

## Residual risks

- Screenshots/traces may capture filled form values until purged — use **Purge run** or **Cleanup**.
- Presigned URLs are bearer URLs for ~15 minutes — do not forward in public channels.
- Debug log mode (`LOG_MODE=debug`) allows longer messages but still scrubs secrets.
- Session TTL is absolute (no separate idle timeout) — stolen session valid until expiry or revocation.
- `SameSite=None` remains required until web and API share one site; misconfigured `COOKIE_SECURE` blocks login (startup guard added).
