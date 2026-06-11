# Security verification matrix — Mission 21

**Date:** 2026-06-11 · **Threat model:** `docs/architecture/threat-model.md`

## Control verification

| Control | Probe | Result | Evidence |
|---------|-------|--------|----------|
| Vault Fernet at rest | Raw SQL on `sensitive_eeo_answers` after merge | **Pass** | `test_vault_security.py::test_vault_merge_writes_ciphertext_at_rest` |
| Consent before sensitive autofill | `resolve_field_fill` without consent | **Pass** | `test_security_controls.py::test_sensitive_fill_refused_without_consent`, `test_form_fill_sensitive.py` |
| Write-time redaction (events) | Plant secrets in `RunEvent.append` | **Pass** | `test_privacy_redaction.py::test_run_event_persistence_scrubs_secrets` |
| LOG_MODE redacted vs debug | `scrub_text` length + secret mask | **Pass** | `test_security_controls.py` (truncation + debug mask) |
| Browser storage state encryption | MinIO blob for run storage | **Pass** | `test_privacy_redaction.py::test_browser_storage_state_encrypted_in_minio` |
| Presigned URL TTL | GET after 1s expiry | **Pass** | `test_security_controls.py::test_presigned_url_expires_after_ttl` (CI MinIO) |
| Presigned / artifact tenant gate | Tenant B activates tenant A resume | **Pass** | `test_security_controls.py::test_cross_tenant_resume_activate_blocked` |
| Tenant isolation (core) | Cross-tenant job/run/doc/privacy | **Pass** | `test_tenant_isolation.py` |
| Tenant isolation (library) | Search must not leak other tenant jobs | **Pass** | `test_security_controls.py::test_cross_tenant_library_search_excludes_other_tenant` |
| RBAC coverage | Undeclared route fails startup validation | **Pass** | `test_rbac.py::test_validate_rbac_coverage_raises_on_undeclared_route` |
| RBAC enforcement | `user` role blocked from admin | **Pass** | `test_rbac.py::test_user_blocked_from_admin_routes` |
| Prompt injection posture | Injection fixture + system prompt | **Pass** | `test_job_extraction.py` (policy), `test_fixture_pipeline.py` |
| Production boot refusal | Placeholder secrets / dev bypass | **Pass** | `test_startup_secrets.py`, `test_auth_cookies.py` |
| CSRF on mutating routes | OpenAPI partition + 403 probe | **Pass** | `test_csrf_coverage.py` |
| Stripe webhook signature | Invalid `Stripe-Signature` | **Pass** | `test_security_controls.py::test_stripe_webhook_rejects_invalid_signature` |
| API security headers | `/healthz` response headers | **Pass** | `test_security_controls.py::test_api_responses_include_security_headers` |
| Web security headers | Next `headers()` config | **Pass** | `apps/web/next.config.ts` (CSP report-only + nosniff + referrer) |
| detect-secrets baseline | CI `detect-secrets scan` | **Pass** | `.github/workflows/ci.yml` |
| Retention / purge | DB + storage prefix removal | **Pass** | `test_purge_storage.py`, `test_artifact_retention.py` |

## Dependency audit

| Surface | Command | Result | Notes |
|---------|---------|--------|-------|
| API (CI install) | `pip-audit` on clean `pip install ./apps/api[dev]` | **Deferred to CI** | Local global site-packages includes unrelated vulns; CI installs pinned resolver set |
| Worker (CI install) | same | **Deferred to CI** | |
| Web prod | `pnpm audit --prod` | **1 moderate (accepted)** | Transitive `postcss` via `next` (<8.5.10 XSS in CSS stringify); no app-controlled PostCSS stringify path; upgrade when Next bundles patched postcss |

## Headers baseline

| Header | API | Web | HSTS |
|--------|-----|-----|------|
| `X-Content-Type-Options: nosniff` | Yes (`SecurityHeadersMiddleware`) | Yes (`next.config.ts`) | Railway platform |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | same | — |
| `X-Frame-Options` | `DENY` | `SAMEORIGIN` | — |
| CSP | — | `Content-Security-Policy-Report-Only` | Enforce after console clean |

## Accepted risks / deferrals

| Item | Rationale | Owner |
|------|-----------|-------|
| PostCSS transitive (web) | Next.js dependency; no direct CSS stringify from user input | Mission 22 / Next upgrade |
| HSTS | Terminated at Railway edge | Ops / deploy runbook |
| WAF / SIEM | Out of scope per mission | Future infra |
| Full local destroy-restore backup drill | Windows port conflicts (Mission 20) | Mission 29 |

## Router coverage note

All `/api/*` routers in `routers/__init__.py` are either public-exempt (auth bootstrap, webhooks, analytics collector, waitlist) or tenant-scoped via `require_auth` + repository `tenant_id`. Mission 21 extended isolation probes to **library search** and **resume activate** (routers added after original tenant isolation suite).
