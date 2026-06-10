# Mission 21: Security and Privacy Validation Sweep

## Purpose
Jober stores resumes, EEO answers, and browser session state — a breach would be personal, not abstract. The security architecture is unusually complete on paper (vault encryption, redaction, RBAC, prompt-injection posture, threat model). This mission *validates* each documented control against the running system and closes verified gaps. Validation, not invention.

## Context From Audits
Application audit §14 (controls in place; re-verify list) and §19 risk #7. Documents of record: `docs/architecture/threat-model.md`, `rbac.md`, `policy-baseline.md`; controls: `VAULT_ENCRYPTION_KEY` field encryption, `LOG_MODE=redacted` write-time redaction, presigned URL TTL 15 min, tenant-prefixed MinIO keys, production boot refusal on placeholder secrets / `DEV_AUTH_BYPASS`, `.secrets.baseline` + pre-commit detect-secrets, encrypted Playwright `browser-storage-state`.

## Scope
- **Control-by-control verification** against the threat model: for each documented control, design a probe that would catch its failure, run it, record evidence.
  - Vault: read raw DB rows for a seeded profile → EEO fields unreadable; consent-flag bypass attempt via API → refused.
  - Redaction: emit run/browser/LLM events containing planted secrets/PII → stored rows are masked; check both `LOG_MODE` values.
  - Presigned URLs: fetch after TTL → rejected; URL for tenant A artifact with tenant B session → rejected.
  - Tenant isolation: re-run `test_tenant_isolation.py` and extend to any router added after it was written (cross-check against the router list).
  - RBAC: startup validation actually fails on an undeclared route (add a temp route in a test to prove it); admin endpoints reject `user` role.
  - Prompt injection: fixture job page containing instruction-shaped text → extraction/letter output treats it as data (assert no instruction-following in the policy suite; add a fixture case if missing).
  - Boot refusal: production-mode boot with placeholder `SECRET_KEY` / `DEV_AUTH_BYPASS=true` → refuses.
- **Dependency audit:** `pip-audit` (or `pip list` against advisories) for api/worker; `pnpm audit` for web; upgrade or document each finding.
- **Headers:** security headers on web + API responses (CSP report-only baseline for the web if absent, X-Content-Type-Options, Referrer-Policy, HSTS at the platform level).
- Stripe webhook signature verification probe (`routers/webhooks.py`).

## Out of Scope
- New security infrastructure (WAF, SIEM, secret managers) — note recommendations only.
- Pen-testing third-party ATSs.
- Rewriting the threat model (update deltas only).

## Starting Checklist
1. Read `docs/architecture/threat-model.md` end to end; extract the control list into the verification matrix.
2. Read `services/privacy/`, the redaction implementation, and `services/auth/` crypto usage.
3. Read `tests/test_encryption.py`, `test_form_fill_sensitive.py`, `test_tenant_isolation.py`, and the policy markers (`pytest -m policy --collect-only`).
4. Confirm local stack with production-like flags is possible (`JOBER_ENV=production`, `REQUIRE_SECRETS=true`) for boot-refusal probes.
5. Check pre-commit config (`.pre-commit-config.yaml`) is actually installed locally (`pre-commit run --all-files`).

## Tasks
1. Build the verification matrix (`docs/polish-pack/notes/21_security_matrix.md`): control × probe × result × evidence.
2. Execute every probe; fix verified gaps with the smallest change; add a regression test per gap.
3. Run dependency audits; apply safe upgrades; document accepted risks with versions and rationale.
4. Header audit + additions (report-only CSP first; tighten only after console is clean across routes).
5. Webhook signature probe (invalid signature → rejected, logged redacted).
6. Update `threat-model.md` with any architecture deltas since build-mission 14 (e.g., SameSite change from Mission 19, email sender from Mission 11).

## Self-Improvement Loop
1. Inspect the next matrix control.
2. Identify the highest-impact unverified or failed control.
3. Make the smallest coherent fix.
4. Validate by re-running the probe + the policy/security test files.
5. Record evidence in the matrix.
6. Repeat until every control is verified with evidence.

## Validation
- `cd apps/api && ruff check src tests && mypy src && pytest -q && cd ../.. && make test-policy`
- `pip-audit` (api+worker envs), `cd apps/web && pnpm audit --prod`
- `pre-commit run --all-files`
- Matrix complete with evidence links/snippets.

## Acceptance Criteria
1. Every threat-model control has a recorded probe result; all failures fixed + regression-tested or documented as accepted risk with owner-visible rationale.
2. Dependency audits clean or explicitly waived per finding.
3. Security headers present per the decided baseline; CSP at least report-only with a clean console.
4. Policy suite green; no redaction regressions.
5. `threat-model.md` current.

## Documentation Requirements
- `docs/polish-pack/notes/21_security_matrix.md`.
- `docs/architecture/threat-model.md` delta update.
- CHANGELOG entry for any dependency upgrades.

## Git Workflow
`git status` first; one commit per control fix or upgrade batch; **extra care:** probe code with planted secrets must use obvious fakes (`sk-FAKE…`) so detect-secrets and the redaction tests don't conflict; push after gates.

## Production Guidance
Security fixes deploy promptly after gates pass. Anything touching cookies, headers, or CSP gets verified against production immediately post-deploy (login, console errors, artifact downloads). `bash scripts/railway-smoke.sh` after.
