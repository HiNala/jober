# Policy baseline (standing invariants)

Blocking tests: `pytest -m policy` in CI (`make test-policy`).

| Invariant | Status |
|-----------|--------|
| No auto-fill of consent-less sensitive fields | **Verified** — `test_fill_policy.py`, `test_form_fill_sensitive.py` |
| CAPTCHA / login / 2FA always hand off to human | **Verified** — gate fixtures + `test_form_fill.py`, `test_fixture_pipeline.py` |
| `auto_submit` never the default | **Verified** — `test_policy_baseline.py` |
| Job-page text treated as untrusted data | **Verified** — `test_prompt_pack.py`, `test_job_extraction.py`, injection fixtures |
| No secrets in logs, commits, or artifacts | **Verified** — `detect-secrets` CI, `test_privacy_redaction.py` write-time scrub |
| Redacted columns never store raw PII | **Verified** — observation redaction, LLM audit scrub, vault ciphertext tests |
| Encrypted browser storage state | **Verified** — MinIO `storage-state.enc`, no plaintext site passwords in DB |
| Presigned URLs short-lived; bucket not public | **Verified** — `PRESIGNED_URL_TTL_MINUTES`, compose `mc anonymous set none` |

See also: [`threat-model.md`](threat-model.md), [`testing.md`](testing.md).
