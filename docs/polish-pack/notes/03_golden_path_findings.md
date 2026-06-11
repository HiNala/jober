# Golden path validation findings — Mission 03

**Validated:** 2026-06-11 · **Validator:** polish pack Mission 03 · **Production URLs:** web `https://web-production-29902.up.railway.app`, api `https://api-production-4b5b.up.railway.app`

Canonical journey (from `docs/MISSION_INDEX.md`): import workbook + resume → profile → queue → Priority A job → visible browser → extract → tailored letter → PDF → discover + fill → upload docs → verify-ready → review-and-submit → confirmation → artifacts → recovery from ≥3 failure classes → failure reports.

## Journey segment results

| Segment | Local | Production | Evidence |
|---------|-------|------------|----------|
| Signup / account creation | **PASS** | **PASS** (register + session cookies) | `POST /api/auth/register` → `pending_verification`; prod login succeeds without verified email |
| Email verification | **PASS** (console/SMTP + dev header) | **Pending re-walk** | Mission 11: Celery + SMTP backend; configure Railway `EMAIL_*` and re-verify production inbox |
| Import workbook (XLSX) | **PASS** (API/tests) | **NOT WALKED** | Covered by import tests; manual UI import not re-run this mission |
| Profile / vault | **PASS** (fixtures seed profile) | **NOT WALKED** | `_seed_job` + profile repo in integration tests |
| Queue visible | **PASS** (API) | **NOT WALKED** (auth required) | Job target CRUD in test suite |
| Extract job (fixture ATS) | **PASS** | N/A (fixtures local) | `test_golden_path_integration.py` discover-form 200 |
| Generate cover letter | **PASS** (fixture/template in CI) | **NOT WALKED** | Document generation tests; prod LLM is OpenAI (see LLM section) |
| Render PDF | **PASS** (unit/integration) | **NOT WALKED** | `documents` router tests |
| Discover + fill form | **PASS** | N/A | Golden path + `test_fixture_pipeline.py` (34 passed) |
| Verify-ready → review-and-submit | **PASS** | **NOT WALKED** | `verify-ready` → `REVIEW_AND_SUBMIT`; `/review` 200 |
| Human submit + confirmation | **PASS** (fixture submit HTML) | **NOT WALKED** | Fixture pipeline; no live ATS submit (by design) |
| Artifacts in object storage | **PASS** (MinIO tests) | **NOT WALKED** | `test_storage.py` / presigned URL tests in CI |
| Recovery / gate checkpoints | **PASS** | N/A | `test_gate_fixture_raises_checkpoint_not_bypass` (policy); behavior gate verify tests |
| Failure reports | **PASS** (tests) | **NOT WALKED** | Recovery package + API tests |
| Analytics ingest + rollup | **PASS** (after harness fix) | **NOT WALKED** | Golden path rollup ≥3 events; see GP-003 |
| Admin acquisition funnel | **PASS** | **NOT WALKED** | Golden path `GET /api/admin/acquisition` |

## Production smoke (`scripts/railway-smoke.sh` equivalent)

```
==> API /healthz
{"status":"ok"}
==> API /readyz
{"status":"ready","checks":{"postgres":{"ok":true},"redis":{"ok":true},"minio":{"ok":true}}}
==> Web /api/health
{"status":"ok"}
==> Web landing + /signup
signup page renders (account/signup copy present)
```

**Result: PASS** (2026-06-11)

## Production manual signup walkthrough

1. `POST /api/auth/register` with disposable email → **200**, `status: pending_verification`, `email_verified: false`, session cookies set.
2. `POST /api/auth/login` with same credentials → **200**, session established (`last_login_at` set). **App is usable without inbox verification** — verification is a dead letter UX path, not a hard gate.
3. No verification email received *(pre–Mission 11 walk; code now dispatches via SMTP when configured)*.
4. Web `/forgot-password` page loads (200); reset email delivery *(same — re-walk after Railway `EMAIL_BACKEND=smtp`)*.

## LLM provider (production)

**Answer: OpenAI is live in production** (not template stub).

Evidence: authenticated `GET /api/llm/config` after prod login (2026-06-11):

```json
{
  "provider": "openai",
  "default_model": "gpt-4o-mini",
  "budget_usd": 25.0
}
```

`TemplateLlmProvider` activates only when `llm_provider == "template"` or `LLM_API_KEY` is empty (`gateway.py`). Production has a real key configured.

## Automated gate results (local, 2026-06-11)

| Command | Result |
|---------|--------|
| `make test-fixtures` / fixture pipeline pytest | **34 passed** (api fixture pipeline) + **23** ats catalog + **8** worker browser |
| `pytest tests/test_golden_path_integration.py` | **2 passed** (after GP-003 harness fix) |
| `scripts/railway-smoke.sh` (prod URLs) | **PASS** |

CI reference: Mission 02 run [27315598137](https://github.com/HiNala/jober/actions/runs/27315598137) backend + policy + web green (includes full api pytest + golden path in UTC CI).

---

## Findings table

| ID | Surface | Severity | Repro / evidence | Owner mission |
|----|---------|----------|------------------|---------------|
| GP-001 | Auth — email verification | **High** (code landed) | Mission 11 shipped SMTP/console dispatch; production inbox walk pending operator | **11** (landed — verify post-deploy) |
| GP-002 | Auth — password reset | **High** (code landed) | Reset email + `/reset-password?token=` wired; production inbox walk pending | **11** (landed — verify post-deploy) |
| GP-003 | Test — golden path analytics rollup | **Low** (fixed) | `date.today()` local vs UTC event timestamps failed outside UTC CI; fixed in `test_golden_path_integration.py` | **03** (landed) |
| GP-004 | Auth UX — verification not enforced | **Medium** | Users can log in and use app while `pending_verification`; misleading if UI promises verify-first | **06** (honest auth copy) |
| GP-005 | Queue empty state | **Medium** | Production screenshot + `job-data-table.tsx` shows `make seed` dev copy | **05** |
| GP-006 | UI polish / generic patterns | **Medium** | `docs/screenshots/UI-REVIEW.md` (7 patterns) | **04–10, 27–28** |
| GP-007 | Pricing — Pro plan | **Medium** | Dead card on `/pricing` | **08** |
| GP-008 | Legal pages | **Medium** | Draft acceptable-use / counsel note | **30** (launch gate) |
| GP-009 | E2E — authenticated app | **Medium** | Only marketing e2e specs; no queue/run/settings axe | **26** |
| GP-010 | LLM audit claim | **Info** | Was “maybe stub”; prod is **openai** | Audit §7 updated |
| GP-011 | Signup API path | **Info** | Wrong path `/api/auth/signup` → 500; correct is `/register` | **29** (docs) |

## Pass summary

- **Core fixture golden path (discover → fill → verify → review): PASS** locally and in CI.
- **Production infra smoke: PASS.**
- **Production LLM: OpenAI (live).**
- **Outbound email implemented (Mission 11); production inbox verification pending operator (GP-001/002).**
