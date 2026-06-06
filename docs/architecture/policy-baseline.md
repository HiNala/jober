# Policy baseline (standing invariants)

Mission 00 does not implement application submission paths. These invariants are **documented now** and will gain automated blocking tests as features land.

| Invariant | Status |
|-----------|--------|
| No auto-fill of consent-less sensitive fields | **Schema ready** — `field_consent` JSONB on `UserProfile`; enforcement in Mission 07+ |
| CAPTCHA / login / 2FA always hand off to human | **Schema ready** — `RunStatus.NEEDS_HUMAN`, `HumanCheckpoint` types; runner in Mission 08+ |
| `auto_submit` never the default | **Verified** — `ApplicationRun.policy` defaults to `review_before_submit`; blocking test in `test_policy_baseline.py` |
| Job-page text treated as untrusted data | N/A — no LLM agents yet (Mission 06+) |
| No secrets in logs, commits, or artifacts | **Verified** — `.gitignore`, `detect-secrets` baseline, Fernet ciphertext for `sensitive_eeo_answers` |
| Redacted columns never store raw PII | **Schema ready** — `proposed_value_redacted`, `redacted_prompt`, `redacted_response`; write-time redaction in Mission 08+ |

**Blocking tests:** `apps/api/tests/test_policy_baseline.py` (run on every CI push).

Re-verify end-to-end when Missions 04–09 touch vault, browser, and submit flows.
