# Mission Index — Jober

> **Post-launch improvement work lives in [`docs/polish-pack/`](polish-pack/mission_index.md)** — a self-contained pack of 2 audits + 31 polish missions for the deployed product. The missions below are the original build missions (complete; archived record).

Run **in order**. After each numbered mission, run **Mission 99 — Iteration Loop** before advancing.

| # | Mission | Builds |
|---|---------|--------|
| 00 | [Repository & Docker foundation](missions/mission_00_repository_and_docker_foundation.md) | Monorepo, Compose, git/.gitignore, CI skeleton |
| 01 | [Backend schema, migrations & storage](missions/mission_01_backend_schema_migrations_storage.md) | Postgres models, Alembic, MinIO, Redis wiring |
| 02 | [Next.js app shell & design system](missions/mission_02_next_app_shell_and_design_system.md) | Generator-scaffolded web app, shadcn + 21st.dev |
| 03 | [Job spreadsheet import](missions/mission_03_job_spreadsheet_import.md) | XLSX import → JobTargets, round-trip status |
| 04 | [Resume ingestion & profile vault](missions/mission_04_resume_ingestion_and_profile_vault.md) | Resume parse, encrypted vault, consent flags |
| 05 | [Cover letter generation & rendering](missions/mission_05_cover_letter_generation_and_rendering.md) | Document Agent, ATS coverage, PDF/DOCX |
| 06 | [Job extraction & platform detection](missions/mission_06_job_extraction_and_platform_detection.md) | Job Intelligence Agent, ATS adapters |
| 07 | [Form discovery & field mapping](missions/mission_07_form_discovery_and_field_mapping.md) | Form Understanding Agent, field schema |
| 08 | [Form filling & file uploads](missions/mission_08_form_filling_and_file_uploads.md) | Browser Action Agent, deterministic tools |
| 09 | [Readiness verification & review-and-submit](missions/mission_09_verification_and_review_submit.md) | Verification Agent, human submit checkpoint |
| 10 | [Retry, recovery & self-assessment](missions/mission_10_retry_recovery_and_self_assessment.md) | Recovery Agent, failure reports |
| 11 | [Live run console & interactive TUI](missions/mission_11_live_run_console_and_interactive_tui.md) | SSE console, Rich TUI (no flags) |
| 12 | [Test fixtures & CI hardening](missions/mission_12_test_fixtures_and_ci_hardening.md) | Mock ATS pages, full test pyramid |
| 13 | [Batch ops, scheduling & rate limits](missions/mission_13_batch_scheduling_and_rate_limits.md) | Queue control, cooldowns, idempotency |
| 14 | [Observability, security & privacy](missions/mission_14_observability_security_privacy.md) | Logs, secrets, encryption, injection defense |
| 15 | [Productionization & commercialization](missions/mission_15_productionization_and_commercialization.md) | Auth, multi-tenant, billing, export/delete |
| 16 | [World-class design pass](missions/mission_16_world_class_design_pass.md) | Design Council gate across all surfaces |
| 99 | [Iteration Loop (run between every mission)](missions/mission_99_iteration_loop.md) | Finish leftovers, self-improve, raise the bar |

**Definition of done for the whole project:** import the workbook + resume → build a profile → see the queue → select Priority A → open a job in a visible browser → extract job info → generate a tailored letter → render PDF → discover + fill the form → upload both docs → verify readiness → present review-and-submit → after you submit, capture confirmation → store screenshots/traces/logs/docs → recover from ≥3 failure classes → write a useful failure report when blocked.
