# Jober Polish Pack — Mission Index

**Created:** 2026-06-10 · **Status:** ready to execute · **Location:** `docs/polish-pack/` (self-contained)

This is the **improvement/polish mission pack** for Jober. It is fully separate from the historical build missions (`docs/missions/mission_NN_*.md`, indexed in [`docs/MISSION_INDEX.md`](../MISSION_INDEX.md)), which are complete and serve as archived records. This pack drives the *existing, deployed* product to excellence: coherent, reliable, beautiful, accessible, performant, clearly positioned, and production-certified — **without feature creep**.

```text
docs/polish-pack/
  mission_index.md        ← this file
  audits/
    00_application_audit.md
    01_product_design_positioning_audit.md
  missions/
    01_land_in_flight_changes.md … 30_release_candidate_and_launch.md
    31_continuation_self_improvement_loop.md
  notes/                  ← working notes, created by Mission 02 onward
```

## 1. Overview of the mission system

- **2 audit documents** ([`audits/`](audits/)) establish ground truth: what the app is, what works, what's broken, and the product/design/positioning direction (including the recorded design north star: Linear-style focus and typography, centered hero product preview, larger nav/type scale; Hyper Agents / Figma / 21st.dev craft; one brand signature; micro-interactions everywhere they communicate state).
- **30 sequential missions** ([`missions/01_*.md`](missions/) … `30_*.md`) move from stabilization → UX/UI execution of the production UI review (`docs/screenshots/UI-REVIEW.md`) → flow completion → hardening → performance → test depth → polish → release certification.
- **1 continuation mission** ([`missions/31_continuation_self_improvement_loop.md`](missions/31_continuation_self_improvement_loop.md)) runs **between every mission** to consolidate, re-verify, absorb necessary adjacent work, and decide deployment.
- Missions write working notes to `docs/polish-pack/notes/` (created by Mission 02); the continuation loop logs to `docs/polish-pack/notes/continuation_log.md`.

## 2. How to run the audits and missions

1. Read both audit docs fully before any mission. Their §21 acceptance-criteria sections define "done" for the whole pack.
2. Execute missions strictly in order. Each mission doc is self-contained: Purpose → Context → Scope/Out of Scope → Starting Checklist → Tasks → Self-Improvement Loop → Validation → Acceptance Criteria → Documentation → Git Workflow → Production Guidance.
3. After **every** mission, run Mission 31 before advancing.
4. Validate with each mission's exact commands; the canonical full gate set lives in `docs/polish-pack/notes/gates.md` after Mission 02.
5. Re-capture screenshots whenever a user-facing surface changes, and review them like a designer:
   `cd apps/web && PLAYWRIGHT_SKIP_WEB_SERVER=1 PLAYWRIGHT_BASE_URL=<url> API_URL=<api-url> node scripts/capture-screenshots.mjs`

## 3. Exact recommended execution order

```text
1. Read docs/polish-pack/audits/00_application_audit.md
2. Read docs/polish-pack/audits/01_product_design_positioning_audit.md
3. Run docs/polish-pack/missions/01_land_in_flight_changes.md
4. Run docs/polish-pack/missions/31_continuation_self_improvement_loop.md
5. Run docs/polish-pack/missions/02_quality_gates_baseline.md
6. Run docs/polish-pack/missions/31_continuation_self_improvement_loop.md
7. Continue alternating: 03, 31, 04, 31, 05, 31, … (every numbered mission is followed by 31)
8. End with docs/polish-pack/missions/30_release_candidate_and_launch.md
9. Run docs/polish-pack/missions/31_continuation_self_improvement_loop.md one final time
```

## 4. The 33 required documents

| # | Document | Role |
|---|----------|------|
| 1 | `audits/00_application_audit.md` | Full application audit |
| 2 | `audits/01_product_design_positioning_audit.md` | Product/design/positioning audit |
| 3–32 | `missions/01_*.md` … `30_*.md` | Sequential missions (table below) |
| 33 | `missions/31_continuation_self_improvement_loop.md` | Continuation loop (run between all missions) |

(This index file does not count toward the 33.)

## 5. Missions 01–30 and intended outcomes

| # | Mission | Intended outcome | Status |
|---|---|---|---|
| 01 | [Land in-flight changes](missions/01_land_in_flight_changes.md) | Clean `main`; uncommitted work validated and landed or parked | ✅ Done |
| 02 | [Quality gates baseline](missions/02_quality_gates_baseline.md) | Every gate green locally + CI; canonical gate doc written | ✅ Done |
| 03 | [Golden path validation](missions/03_golden_path_validation.md) | Whole journey verified local + prod; master defect list produced | ✅ Done |
| 04 | [Consent & analytics UX](missions/04_consent_and_analytics_ux.md) | One-time bottom sheet; no content overlap; consent provable | ✅ Done |
| 05 | [Page states & onboarding](missions/05_page_states_and_onboarding.md) | Every empty/loading/error state onboards; zero dev copy | ✅ Done |
| 06 | [Auth surface polish](missions/06_auth_surface_polish.md) | Branded auth with trust strip; honest verification copy | ✅ Done |
| 07 | [Homepage hero & landing](missions/07_homepage_hero_and_landing.md) | Linear-style hero with centered product preview; differentiator elevated | ✅ Done |
| 08 | [Marketing subpages polish](missions/08_marketing_subpages_polish.md) | Features/how/pricing/FAQ to the same bar; Pro waitlist replaces dead card | ✅ Done |
| 09 | [Workspace layout discipline](missions/09_workspace_layout_discipline.md) | Split-pane only on run surfaces; ⌘K palette replaces bolted-on AI bar | ✅ Done |
| 10 | [Component tiering & consistency](missions/10_component_tiering_consistency.md) | Three component families; duplicates consolidated; tokens enforced | ✅ Done |
| 11 | [Email delivery completion](missions/11_email_delivery_completion.md) | Verification + reset emails work in production; CI stays offline | ✅ Done |
| 12 | [Forms & validation](missions/12_forms_and_validation.md) | Uniform validation, 422 mapping, pending states; no input loss | ✅ Done |
| 13 | [Accessibility pass](missions/13_accessibility_pass.md) | Axe green on app routes; keyboard-complete golden path | ✅ Done |
| 14 | [Responsive & mobile refinement](missions/14_responsive_mobile_refinement.md) | Marketing/auth designed at 375+; app usable; run console tablet-ready | ✅ Done |
| 15 | [Run console reliability](missions/15_run_console_reliability.md) | SSE reconnect-proof; checkpoint conflicts handled; end states designed | ✅ Done |
| 16 | [Discover → queue journey](missions/16_discover_queue_journey.md) | Seamless import/discover/batch flow; XLSX round-trip proven | ✅ Done |
| 17 | [Document studio polish](missions/17_document_studio_polish.md) | Friction-free letter cycle; honest stub/402 states; lock guarantee tested | ✅ Done |
| 18 | [API error contract](missions/18_api_error_contract.md) | One error envelope; no leaks; truthful `/readyz`; downstream mapping | ✅ Done |
| 19 | [Auth/session hardening](missions/19_auth_session_hardening.md) | Cookie/CSRF/session matrix verified; lifecycle test-enforced | ✅ Done |
| 20 | [DB & migration hygiene](missions/20_database_migration_hygiene.md) | Replay/drift/index/retention/backup all drilled with evidence | ✅ Done |
| 21 | [Security & privacy validation](missions/21_security_privacy_validation.md) | Every threat-model control probe-verified; deps audited | ✅ Done |
| 22 | [Web performance](missions/22_web_performance.md) | CWV targets met; chunks clean; budgets tightened | ✅ Done (PSI deferred post-deploy) |
| 23 | [API & worker performance](missions/23_api_worker_performance.md) | Latency baselines met; pagination everywhere; guards in load tests | ✅ Done |
| 24 | [Observability completion](missions/24_observability_completion.md) | Metrics truthful; every alert class fires; logs answer real questions | ✅ Done |
| 25 | [Test coverage critical paths](missions/25_test_coverage_critical_paths.md) | Critical paths covered; zero flakes; mutation spot-checks pass | ✅ Done |
| 26 | [E2E validation expansion](missions/26_e2e_validation_expansion.md) | Five deterministic e2e journeys in CI with traces | ✅ Done |
| 27 | [Copy, microcopy & SEO](missions/27_copy_microcopy_seo.md) | One voice everywhere; P0 copy bugs dead; full metadata/JSON-LD | ✅ Done (OG images deferred) |
| 28 | [Brand, motion & micro-interactions](missions/28_brand_motion_microinteractions.md) | One brand signature; sourced 21st.dev/v0-grade patterns on tokens; nothing reads default | ✅ Done |
| 29 | [Documentation & runbooks](missions/29_documentation_and_runbooks.md) | Every doc executed-and-verified; operator-organized README | ⏳ Ready to execute |
| 30 | [Release candidate & launch](missions/30_release_candidate_and_launch.md) | Audit §21 criteria all true; RC deployed, certified, tagged; post-launch loop | ⏳ Ready to execute |

## 6. Git commit and push guidance

Every mission follows the same discipline:

1. `git status` before changes; review `git diff` before staging.
2. Keep changes focused on the mission; stage only relevant files.
3. Commit messages carry the mission tag (`[pack-NN]`) and a body with: what changed, why it changed, validation performed, known follow-ups.
4. One logical change per commit; never edit applied migrations; never commit secrets (pre-commit detect-secrets is active).
5. Push to `origin main` at mission boundaries when all gates are green (repo convention, MASTER_PLAN §10). Never `--no-verify`. A red gate at push time means fix it or record a blocker — never push around it.

## 7. When production deployment is appropriate

Deploy only when **all** of: build + lint/typecheck pass (or exceptions documented); critical tests pass; the primary user journey works (e2e or manual fixture walkthrough); no open security or data-loss risk; env vars and deploy config ready; the change is coherent (no half-finished state — paired API+web contract changes deploy together); and the mission's own Production Guidance permits it. Procedure: backup first for migrations, follow `docs/runbooks/deploy.md`, then `bash scripts/railway-smoke.sh`, and record the outcome in the continuation log. Early missions mostly say "don't deploy"; Missions 11, 19, and 21 say "deploy promptly once green"; Mission 30 is the certified release. Not deploying is a decision too — record it.

## 8. Avoiding feature creep

- The binding guardrail list is positioning audit §20 (no new ATS adapters, LLM providers, mobile apps, public APIs, CMS, team features, Stripe checkout without owner sign-off, etc.).
- Additions are allowed only to complete an incomplete flow (e.g., Mission 11 email), fix a broken promise, or satisfy a written acceptance criterion — and must cite which.
- Default verbs: refine, repair, simplify, consolidate, validate. If a task idea doesn't fit one of those, it needs the citation above or it doesn't happen.
- Mission 31's Operating Rules enforce this between missions; re-read them every loop.

## 9. If a mission cannot be completed

1. Do not silently skip or fake completion. Record the blocker in the mission's notes file: what's blocked, exact repro/evidence, what was tried, what unblocks it (owner decision, external dependency, credentials…).
2. Commit all safe completed work; ensure gates are green for what landed; leave the tree clean.
3. If the blocker is external (e.g., legal counsel, a paid provider decision), mark the affected acceptance criteria "waived-pending-X" and continue to the next mission.
4. If the blocker breaks the sequence (later missions depend on it), run Mission 31, then resolve the dependency question explicitly in `continuation_log.md` before proceeding.
5. Surface every open blocker again in Mission 30 — nothing ships silently waived.
