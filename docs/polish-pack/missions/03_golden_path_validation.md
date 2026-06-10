# Mission 03: Golden Path Validation (Prove the Product Works Before Changing It)

## Purpose
The pack's operating principle is "validate existing features before adding or changing scope." This mission walks the entire primary journey — signup → import → vault → batch → run → review → submit → artifacts — locally against fixtures and against production, and produces a defect list that later missions consume. No fixes here except trivial blockers; the deliverable is verified truth.

## Context From Audits
Application audit §4 (journeys), §7.2–7.3 (email dead-end, possibly-stub LLM in prod), §19 risks #2/#4/#11. Recent commits show production hotfix churn (cookies, SSL), so the deployed state needs re-verification, not assumption. The repo provides purpose-built tools: `bash scripts/staging-golden-path.sh`, `bash scripts/railway-smoke.sh`, the fixture pipeline (`make test-fixtures`), and `apps/api/tests/test_golden_path_integration.py`.

## Scope
- Execute the golden path end-to-end locally (full stack via `make up`, fixture ATS via `make fixture-serve`).
- Execute the production smoke + manual walkthrough on the live Railway URLs.
- Verify the LLM provider actually in use in production (template stub vs OpenAI) via `/api/admin/overview` or `LlmCall` evidence.
- Record every defect, dead end, and rough edge in `docs/polish-pack/notes/03_golden_path_findings.md` with severity and the pack mission that should fix it.

## Out of Scope
- Fixing anything beyond a one-line blocker that prevents continuing the walkthrough (and only with a commit explaining it).
- UI polish observations (already cataloged in `docs/screenshots/UI-REVIEW.md` — link, don't duplicate).

## Starting Checklist
1. Read `docs/runbooks/launch-checklist.md` and `scripts/staging-golden-path.sh` to learn the existing definition of "golden path."
2. Read the MISSION_INDEX "Definition of done for the whole project" paragraph — it is the canonical journey list.
3. `make up`, `make migrate`, `make seed`; confirm `curl http://localhost:8000/healthz` and `/readyz`.
4. Start the fixture server: `make fixture-serve` (port 8765).
5. Have a test XLSX ready (see `fixtures/` and `apps/api/tests/fixtures/` for sample workbooks).

## Tasks
1. **Local walkthrough:** signup at `/signup` (with `AUTH_MODE=native`; note what happens at the verification step), import workbook at `/queue`, complete vault at `/settings`, upload resume, extract a fixture job, generate a letter, discover + fill the form via fixture HTML, verify-ready, resolve the review checkpoint at `/runs/[id]`, submit, confirm artifacts in MinIO console (`:9001`).
2. **Recovery check:** force one failure class (e.g., fixture login page) and confirm a checkpoint + failure report appears.
3. **Local automated equivalents:** `make test-fixtures`, `cd apps/api && pytest -q tests/test_golden_path_integration.py`.
4. **Production:** `API_URL=https://api-production-4b5b.up.railway.app WEB_URL=https://web-production-29902.up.railway.app bash scripts/railway-smoke.sh`; then manually sign up with a disposable email and record exactly where the journey stops (expected: verification email never arrives — capture the precise UX shown).
5. **LLM truth:** determine whether production letters are stub/template output; record evidence.
6. Write `docs/polish-pack/notes/03_golden_path_findings.md`: table of findings (id, surface, severity, repro, owning pack mission).

## Self-Improvement Loop
1. Inspect the next journey segment.
2. Identify the highest-impact unverified behavior.
3. Execute and observe it (smallest possible probe).
4. Validate by capturing evidence (response body, screenshot, DB row).
5. Document the finding.
6. Repeat until every segment of the journey has a recorded pass/fail.

## Validation
- `make test-fixtures` and `pytest -q tests/test_golden_path_integration.py` pass.
- `bash scripts/railway-smoke.sh` output captured in the findings file.
- Findings file lists every journey segment with explicit PASS/FAIL/BLOCKED.

## Acceptance Criteria
1. Every segment of the MISSION_INDEX definition-of-done journey has a recorded local result.
2. Production smoke result and the manual signup walkthrough result are recorded with evidence.
3. The LLM-provider question is answered definitively.
4. Findings file exists, each finding mapped to a later pack mission (or flagged "unowned" for the index to resolve).
5. No code changes beyond documented trivial blockers.

## Documentation Requirements
- `docs/polish-pack/notes/03_golden_path_findings.md` (new) — the master defect list for this pack.
- Update `docs/polish-pack/audits/00_application_audit.md` §7 with a one-line confirmation/correction per audit claim this mission tested.

## Git Workflow
`git status` before starting. Commit the findings file and any audit corrections as `docs(validation): golden path findings [pack-03]` with a body summarizing pass/fail counts. Any blocker fix gets its own `fix(...)` commit with repro and validation. Push after gates pass.

## Production Guidance
Do not deploy. This mission only observes production. If the walkthrough reveals a severity-critical live defect (data loss, auth bypass), stop and fix it immediately under Mission 31 rules before continuing the pack.
