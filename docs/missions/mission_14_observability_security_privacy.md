# Mission 14 — Observability, Security & Privacy

## Task list

### Secrets & credentials
- [x] All secrets via env/secret store; CI `detect-secrets` blocks
- [x] No plaintext site credentials — Playwright storage state encrypted in MinIO per run
- [x] LLM API key server-side only (never logged or sent to browser)

### Logging & redaction
- [x] Central redaction layer (`jober_api.privacy.redaction`) at event/LLM write boundaries
- [x] `LOG_MODE=redacted` (default) vs `debug` — debug never includes secrets

### Encryption & storage
- [x] Vault sensitive fields encrypted at rest (Mission 04 Fernet)
- [x] Encryption-at-rest notes in `docs/architecture/threat-model.md`
- [x] MinIO per-run prefixes, short presigned TTL, bucket anonymous access disabled
- [x] Per-run browser contexts; encrypted storage state not shared across runs

### Prompt-injection defense
- [x] Agent prompts mark job-page text as untrusted (Missions 05–06)
- [x] Injection fixtures in blocking policy suite (Mission 12)
- [x] CAPTCHA/login/2FA human handoff — codified and tested

### Retention
- [x] Purge run, cleanup by filters, export-all, delete-all with confirmation

### Iteration clause
- [x] `docs/architecture/threat-model.md`
- [x] Startup self-check refuses boot with placeholder secrets (production / `REQUIRE_SECRETS`)

## Acceptance criteria
- [x] Redaction test: secrets/PII never in stored run events
- [x] Vault ciphertext at rest (`test_vault_security`)
- [x] `detect-secrets` in CI
- [x] Injection + CAPTCHA/login policy tests blocking
- [x] Purge/export/delete endpoints

## Mission 99
- [x] Run full gates; push to `origin/main`
