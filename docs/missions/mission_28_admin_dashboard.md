# Mission 28 — Admin Dashboard

## Task list
- [x] **Overview:** DAU/WAU/MAU, signups, runs/submits, LLM cost forecast, health + attention
- [x] **Acquisition:** funnel, traffic, UTM aggregates, coarse geo (`GET /api/admin/acquisition`)
- [x] **Users:** search, promote/suspend (audited), support view (audited, no vault)
- [x] **Runs:** product-wide outcomes, failure-by-platform, needs-human backlog
- [x] **Cost:** rollup + reconciliation (`GET /api/admin/cost`)
- [x] **Config:** feature flags, announcement banner, letter defaults (`product_config`)
- [x] **System:** readyz checks, queue snapshot, audit log, data-request queue
- [x] **RBAC:** `admin:ops:read`, `admin:config:manage` + existing admin permissions
- [x] **Web:** `/admin` shell with section nav; reuses M26 chart components

## Acceptance criteria
- [x] Sections render from rollups / operational aggregates (no third-party analytics)
- [x] Admin-only access; mutating actions audited (`test_admin_dashboard.py`)
- [x] User promote/suspend + support view logged
- [x] Cost reconciles via existing `get_admin_cost`
- [x] Design Council ≥18/20 (see `design-review.md`)

## API routes
| Route | Permission |
|-------|------------|
| `GET /api/admin/overview` | `admin:ops:read` |
| `GET /api/admin/runs` | `admin:ops:read` |
| `GET /api/admin/acquisition` | `admin:analytics:read` |
| `GET /api/admin/cost` | `admin:analytics:read` |
| `GET /api/admin/system` | `admin:ops:read` |
| `GET /api/admin/data-requests` | `admin:ops:read` |
| `GET /api/admin/users/{id}/operational` | `admin:users:manage` |
| `GET/PATCH /api/admin/config/*` | `admin:config:manage` |

## Iteration clause
Saved admin views and daily/weekly digest **deferred** — overview attention banners are the v1 substitute.

**CI:** [run 27225282196](https://github.com/HiNala/jober/actions/runs/27225282196) (green on `80d7f70`).

## Mission 99
- [x] Structured support view (replaces raw JSON dump)
- [x] Audit log action filter on system page + API fixture
- [x] M28 permission + privacy-boundary regression tests
- [x] Design Council addendum in `design-review.md`

**M99 CI:** [run 27229223560](https://github.com/HiNala/jober/actions/runs/27229223560) (green on `d519c4c`).
