# Rollback

## Symptoms

- Bad deploy after push; elevated 5xx; migrations partially applied; feature regression.

## Diagnosis

1. Railway → service → Deployments — identify last **SUCCESS** deployment.
2. Check API logs for migration errors or import failures.
3. `curl -sS "$API_URL/readyz"` — which check failed?

## Fix

### Fast rollback (no schema change)

```bash
railway redeploy --service api --environment production --yes
# Pick prior deployment in dashboard if redeploy rebuilt same SHA:
# Deployments → previous SUCCESS → Redeploy
```

Repeat for `web` and `worker` if needed.

### Rollback with schema regression

If the bad deploy ran a forward-only migration:

1. **Do not** run `alembic downgrade` in production without a tested plan.
2. Roll back app images to prior deployment first.
3. If migration is backward-compatible, fix forward with a new migration.
4. If not, restore Postgres from backup — [restore-backup.md](./restore-backup.md).

### Verify

```bash
export API_URL=https://<api-domain>
export WEB_URL=https://<web-domain>
bash scripts/railway-smoke.sh
```
