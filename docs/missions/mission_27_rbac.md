# Mission 27 — RBAC, Roles & Admin Bootstrap

## Task list
- [x] **Roles & permissions model:** `Permission`, `Resource`, `can()`, `ROLE_PERMISSIONS` in `auth/permissions.py`
- [x] **Enforcement:** `RBACRouter`, `@requires`, `Depends(require_permission)`, startup `validate_rbac_coverage` (default-deny)
- [x] **Tenant + role:** tenant isolation unchanged in repos; admin boundaries in `docs/architecture/rbac.md`
- [x] **Admin bootstrap:** `scripts/bootstrap_admin.py` + `ADMIN_BOOTSTRAP_SECRET` (no public escalation)
- [x] **Audit log:** `admin_audit_logs` + `record_admin_audit` on role/status changes and bootstrap
- [x] **Tests:** `test_rbac.py` — 403 for users, admin access, escalation blocked, audit rows

## Acceptance criteria
- [x] Undeclared protected routes fail startup validation
- [x] User token blocked from admin endpoints (adversarial tests)
- [x] First admin only via bootstrap CLI
- [x] Admin actions in audit log
- [x] Gates green

## API
| Route | Permission |
|-------|------------|
| `GET /api/admin/users` | `admin:users:manage` |
| `PATCH /api/admin/users/{id}/role` | `admin:users:manage` |
| `PATCH /api/admin/users/{id}/status` | `admin:users:manage` |
| `GET /api/admin/audit-log` | `admin:audit:read` |
| `GET /api/analytics/admin/*` | `admin:analytics:read` |
| Tenant routes | `authenticated` |

## Web
- `/admin/users` — guarded by `AdminRouteGuard` (server is source of truth)
- `lib/auth/permissions.ts` — UI hide only; not security

## Iteration clause
Impersonation **deferred** — documented in `docs/architecture/rbac.md` (consent + audit burden).

**CI:** [run 27196521889](https://github.com/HiNala/jober/actions/runs/27196521889) (backend + web + policy green on `0a41bb0`).

## Mission 99
- [x] `enum_value()` helper + `can()` string-role normalization
- [x] Startup coverage + string-serialization regression fixtures
- [x] Admin UI mutation error toasts
- [x] Design Council addendum in `design-review.md`

**M99 CI:** [run 27199667593](https://github.com/HiNala/jober/actions/runs/27199667593) (green on `b1504e5`).
