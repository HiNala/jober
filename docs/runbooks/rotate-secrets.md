# Rotate secrets

## When

- Credential leak, offboarding, periodic rotation, bucket key reset.

## Order (minimize downtime)

1. **Generate new values** locally (never commit):
   - `SECRET_KEY`, `VAULT_ENCRYPTION_KEY` (Fernet — note: rotating vault key requires re-encryption plan)
   - `MINIO_*` — `railway bucket credentials --bucket <name> --reset --yes`
   - `LLM_API_KEY`, Stripe keys, OAuth secrets

2. **Railway:** set new variables on affected services (api, worker, web build vars if needed).

3. **Redeploy** services (Railway auto-redeploys on variable change).

4. **Invalidate sessions** if `SECRET_KEY` rotated — users re-login.

5. **Vault key rotation:** production requires migration script; prefer maintenance window.

## Verify

- API boots without placeholder errors
- `/readyz` green
- Login + one fixture run
- `detect-secrets` / git history audit — no leaked values

## Never

- Commit `.env` or paste secrets in tickets/logs
- Rotate all keys at once without rollback plan
