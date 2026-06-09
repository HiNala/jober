# RBAC & admin data boundaries (Mission 27)

## Roles
| Role | Purpose |
|------|---------|
| `user` | Default. Tenant-scoped read/write on own workspace data. |
| `admin` | Product operations: aggregate analytics, user directory, audit log. |

Extensible via `ROLE_PERMISSIONS` in `apps/api/src/jober_api/auth/permissions.py`.

## Permissions
| Permission | Who | Scope |
|------------|-----|--------|
| `authenticated` | All signed-in users | Own `tenant_id` only (enforced in repositories) |
| `admin:analytics:read` | Admin | Product-wide **rollup** analytics (no raw events scan) |
| `admin:users:manage` | Admin | Email, role, status — no vault/profile body |
| `admin:audit:read` | Admin | Admin audit log entries |

`can(actor, action, resource)` is the single check — routes declare a permission; `PermissionMiddleware` default-denies undeclared routes.

## Admin must NOT
- Read another tenant's job targets, vault, or documents via a blanket bypass.
- Promote themselves through a public API (bootstrap is CLI + `ADMIN_BOOTSTRAP_SECRET` only).
- Demote the last remaining admin.

## Admin MAY
- List users (operational metadata).
- Promote/demote roles and suspend accounts (audited).
- View product analytics dashboards (Mission 26 rollups).

## Impersonation (iteration clause)
**Not implemented.** Read-only impersonation would require explicit user consent, a persistent banner, and per-field audit on every vault access. For Mission 28 we prefer aggregate admin surfaces and a narrow user directory; impersonation is deferred to avoid a high-risk footgun.

## Bootstrap
```bash
ADMIN_BOOTSTRAP_SECRET=... python apps/api/scripts/bootstrap_admin.py --email you@example.com
```
Works only while zero admins exist. Further admins are promoted via `PATCH /api/admin/users/{id}/role` by an existing admin.
