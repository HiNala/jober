# Mission 26 — Analytics Dashboards & Funnels

## Task list
- [x] **Query API:** typed endpoints over rollup tables (time range, compare-previous, CSV export); 60s in-process cache; no synchronous raw-event scans
- [x] **Charting:** Recharts components — line, bar, funnel, big-number; shared `chart-theme.ts` tokens
- [x] **User analytics view:** applications sent, responses, letters, LLM cost vs budget, activity + cost series; attention notes first
- [x] **Funnels:** landing → signup → first list → first run → first submit; drop-off per step; admin-only product funnel
- [x] **Traffic view (admin):** pages, DAU series, totals from `AnalyticsDailyPage` / `AnalyticsDailyActiveUsers`
- [x] **Cost view (admin):** rollup vs `LlmCall` reconciliation, anomalies, by-day chart
- [x] **Performance:** rollup queries only; loading/empty/error states on all panels

## Acceptance criteria
- [x] Dashboards read from daily rollup tables (funnel, page, active users, cost)
- [x] Signup funnel per-step counts + drop-off match seeded rollup data (`test_admin_funnel_matches_seeded_rollups`)
- [x] Cost view reconciles with `LlmCall` totals (`test_admin_cost_reconciles_with_llm_calls`)
- [x] Charts share one visual language; Design Council Tufte ≥18/20
- [x] User analytics tenant-scoped (`test_user_analytics_scoped_to_tenant`); admin routes 403 for non-admin

## Iteration clause
- [x] CSV export on every dashboard view (`/export.csv` routes + UI links)
- [x] Compare-to-previous-period toggle on user + admin funnel panels

## API
| Route | Auth | Purpose |
|-------|------|---------|
| `GET /api/analytics/me` | User | Tenant-scoped workspace metrics |
| `GET /api/analytics/me/export.csv` | User | CSV export |
| `GET /api/analytics/admin/funnel` | Admin | Product signup funnel |
| `GET /api/analytics/admin/traffic` | Admin | Page + active-user rollups |
| `GET /api/analytics/admin/cost` | Admin | LLM cost + reconciliation |
| `GET /api/analytics/admin/*/export.csv` | Admin | CSV exports |

## Web
- `/analytics` — user workspace tab; admin tab for product funnel, traffic, cost
- Nav: Analytics in app sidebar
- Components: `apps/web/src/components/analytics/`

## CI
Green on [27186144157](https://github.com/HiNala/jober/actions/runs/27186144157) (`7fb9f47`).

## Mission 99 (post–Mission 26)
- [x] Finish leftovers — traffic detail table (bounce, time-on-page, sessions); traffic CSV export in UI
- [x] Gates green — ruff, mypy, pytest, web lint:strict/typecheck/build, CI
- [x] Full suite — traffic rollup, compare_previous, CSV export tests added
- [x] Policy invariants unchanged (analytics dashboards do not touch autofill/submit paths)
- [x] Secrets — detect-secrets clean in CI
- [x] File hygiene — per-task commits; all modules under 2000 lines
- [x] Design Council 19/20 on dashboard surfaces (unchanged; M99 polish documented)
- [x] Self-improvement — credential-based CSV download; funnel compare drop-off attention + prior column
- [x] Docs — mission M99 section, design-review improvements logged
- [x] Fixture-for-bug — `test_user_analytics_compare_previous`, `test_admin_traffic_reads_page_rollups`, `rangeFromPreset` unit test
