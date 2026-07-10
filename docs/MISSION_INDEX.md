# Mission Index — Jober

> **Binding design bible for perfection work:** [`architecture/design-north-star-2030.md`](architecture/design-north-star-2030.md)  
> **Post-launch polish pack (mostly complete):** [`polish-pack/mission_index.md`](polish-pack/mission_index.md)  
> **Active perfection track:** Missions **35–45** below (plus **99** between every mission)

Run **in order** within a phase. After each numbered mission, run **Mission 99 — Iteration Loop** before advancing.

---

## Phase A — Foundation & core autopilot (00–16) · archived build record

| # | Mission | Builds | Status |
|---|---------|--------|--------|
| 00 | [Repository & Docker foundation](missions/mission_00_repository_and_docker_foundation.md) | Monorepo, Compose, git/.gitignore, CI skeleton | ✅ |
| 01 | [Backend schema, migrations & storage](missions/mission_01_backend_schema_migrations_storage.md) | Postgres models, Alembic, MinIO, Redis wiring | ✅ |
| 02 | [Next.js app shell & design system](missions/mission_02_next_app_shell_and_design_system.md) | Generator-scaffolded web app, shadcn + 21st.dev | ✅ |
| 03 | [Job spreadsheet import](missions/mission_03_job_spreadsheet_import.md) | XLSX import → JobTargets, round-trip status | ✅ |
| 04 | [Resume ingestion & profile vault](missions/mission_04_resume_ingestion_and_profile_vault.md) | Resume parse, encrypted vault, consent flags | ✅ |
| 05 | [Cover letter generation & rendering](missions/mission_05_cover_letter_generation_and_rendering.md) | Document Agent, ATS coverage, PDF/DOCX | ✅ |
| 06 | [Job extraction & platform detection](missions/mission_06_job_extraction_and_platform_detection.md) | Job Intelligence Agent, ATS adapters | ✅ |
| 07 | [Form discovery & field mapping](missions/mission_07_form_discovery_and_field_mapping.md) | Form Understanding Agent, field schema | ✅ |
| 08 | [Form filling & file uploads](missions/mission_08_form_filling_and_file_uploads.md) | Browser Action Agent, deterministic tools | ✅ |
| 09 | [Readiness verification & review-and-submit](missions/mission_09_verification_and_review_submit.md) | Verification Agent, human submit checkpoint | ✅ |
| 10 | [Retry, recovery & self-assessment](missions/mission_10_retry_recovery_and_self_assessment.md) | Recovery Agent, failure reports | ✅ |
| 11 | [Live run console & interactive TUI](missions/mission_11_live_run_console_and_interactive_tui.md) | SSE console, Rich TUI | ✅ |
| 12 | [Test fixtures & CI hardening](missions/mission_12_test_fixtures_and_ci_hardening.md) | Mock ATS pages, full test pyramid | ✅ |
| 13 | [Batch ops, scheduling & rate limits](missions/mission_13_batch_scheduling_and_rate_limits.md) | Queue control, cooldowns, idempotency | ✅ |
| 14 | [Observability, security & privacy](missions/mission_14_observability_security_privacy.md) | Logs, secrets, encryption, injection defense | ✅ |
| 15 | [Productionization & commercialization](missions/mission_15_productionization_and_commercialization.md) | Auth, multi-tenant, billing hooks, export/delete | ✅ + residual → M38 |
| 16 | [World-class design pass](missions/mission_16_world_class_design_pass.md) | Design Council gate across surfaces | ✅ + residual → M35–36 |

---

## Phase B — Product expansion (17–34) · archived build record

| # | Mission | Builds | Status |
|---|---------|--------|--------|
| 17 | [Application shell v2](missions/mission_17_application_shell_v2.md) | Workspace chrome, nav, layout | ✅ → upgrade M39 |
| 18 | [Live canvas](missions/mission_18_live_canvas.md) | Live browser surface, SSE frames | ✅ → upgrade M39/42 |
| 19 | [Motion](missions/mission_19_motion.md) | Motion tokens, reduced-motion | ✅ → extend M35 |
| 20 | [Native auth](missions/mission_20_native_auth.md) | Email/password, sessions, CSRF | ✅ → harden M37 |
| 21 | [Google OAuth](missions/mission_21_google_oauth.md) | Google sign-in + account linking | ✅ → production M37 |
| 22 | [User settings, library, preferences](missions/mission_22_user_settings_library_preferences.md) | Settings, library, prefs | ✅ |
| 23 | [Unified job discovery](missions/mission_23_unified_job_discovery.md) | Discover + lists + batch | ✅ → perfect M40 |
| 24 | [Cover letter system v2](missions/mission_24_cover_letter_system_v2.md) | Letter studio v2 | ✅ → + resume M41 |
| 25 | [In-house analytics](missions/mission_25_in_house_analytics.md) | First-party events | ✅ → polish M43 |
| 26 | [Analytics dashboards](missions/mission_26_analytics_dashboards.md) | User analytics UI | ✅ → polish M43 |
| 27 | [RBAC](missions/mission_27_rbac.md) | Roles & permissions | ✅ |
| 28 | [Admin dashboard](missions/mission_28_admin_dashboard.md) | Ops admin surfaces | ✅ → polish M43 |
| 29 | [Marketing landing](missions/mission_29_marketing_landing.md) | Home / landing v1 | ✅ → rebuild M36 |
| 30 | [Marketing site](missions/mission_30_marketing_site.md) | Features, pricing, legal, SEO | ✅ → rebuild M36 |
| 31 | [Test suite expansion](missions/mission_31_test_suite_expansion.md) | Broader tests | ✅ → recert M45 |
| 32 | [Performance, load, resilience](missions/mission_32_performance_load_resilience.md) | Perf budgets | ✅ → recert M45 |
| 33 | [Railway production deployment](missions/mission_33_railway_production_deployment.md) | Deploy topology | ✅ |
| 34 | [Production readiness & launch](missions/mission_34_production_readiness_launch.md) | Observability, runbooks, v0.1 | ✅ → recert M45 |

---

## Phase C — Perfection pack 2030 (35–45) · **ACTIVE**

Goal: fix broken integrations and logic gaps; complete Stripe, Google auth, resume tailoring, approve/send UX; rebuild UI/UX to Hyperagent + Grok-grade 2030 premium; full mobile; zero quality debt.

| # | Mission | Outcome |
|---|---------|---------|
| 35 | [Design system 2030](missions/mission_35_design_system_2030.md) | Tokens, AmbientCanvas, SkeletonStream, CheckpointCard, CommandComposer, ApproveSendBar |
| 36 | [Marketing site v3](missions/mission_36_marketing_site_v3.md) | Dark hero, sales funnel, conversion, assets |
| 37 | [Auth & Google production](missions/mission_37_auth_google_production.md) | Honest Google, email delivery, branded auth |
| 38 | [Stripe checkout & monetization](missions/mission_38_stripe_checkout_monetization.md) | Checkout, portal, unlock modal, entitlements |
| 39 | [Workspace command center](missions/mission_39_workspace_command_center.md) | Hyperagent-inspired app shell + run console |
| 40 | [Perfect job matching](missions/mission_40_perfect_job_matching.md) | Discovery fit v2, lists, import UX |
| 41 | [Document intelligence](missions/mission_41_document_intelligence_resume_letters.md) | Resume tailoring + letter studio |
| 42 | [Apply autopilot approve/send](missions/mission_42_apply_autopilot_approve_send.md) | Review → Approve → confirmation |
| 43 | [Analytics & admin excellence](missions/mission_43_analytics_admin_ops_excellence.md) | User + admin dashboards 2030 |
| 44 | [Mobile responsive perfection](missions/mission_44_mobile_responsive_perfection.md) | All viewports, bottom nav, touch |
| 45 | [QA hardening & launch cert](missions/mission_45_qa_hardening_launch_cert.md) | Full matrix, tag, ship |

| # | Mission | Role |
|---|---------|------|
| 99 | [Iteration Loop](missions/mission_99_iteration_loop.md) | Run **between every mission** |

---

## Execution order (perfection)

```text
1. Read docs/architecture/design-north-star-2030.md
2. Read docs/MASTER_PLAN.md (updated perfection section)
3. For N in 35..45:
     run mission_N
     run mission_99
4. Optional: finish polish-pack missions 29–30 if still open, then M45 cert
```

---

## Definition of done (whole product — 2030)

1. **Discover / import** high-signal jobs with fit explanations into a named list  
2. **Tailor** resume variant + cover letter; human approve/lock  
3. **Run** apply pipeline with live watchable browser + event stream  
4. **Review** fill diff, attachments, blockers → **Approve / Send**  
5. **Archive** confirmation; update tracker status (and XLSX round-trip)  
6. **Auth** email + Google (when configured); sessions secure  
7. **Billing** Free limits + Stripe Pro checkout when configured  
8. **Analytics + admin** truthful and usable  
9. **Mobile + desktop** polished; a11y green  
10. **CI** lint/type/tests green; no critical security debt  

It removes repetitive labor while keeping the human as the one who submits — now with a UI that looks like it shipped from 2030.
