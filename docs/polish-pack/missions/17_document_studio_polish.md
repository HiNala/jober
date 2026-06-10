# Mission 17: Document Studio and Cover Letter UX Polish

## Purpose
Cover letters are the product's most personal output — the user signs them. The studio (Library → Cover letters, run-canvas Documents tab) must feel precise and craft-oriented: editing, locking, regenerating, versioning, and downloading without friction or ambiguity, with micro-interactions that make state changes legible.

## Context From Audits
UI-REVIEW row 18 (`18-library-letters.png`) and the cross-cutting component-tiering theme. README Missions 05/24 document the surface: templates (classic/modern/compact), voice presets, paragraph locking, inline edit with re-render + ATS refresh, duplication, version history, PDF download, per-run generate/skip overrides, Settings defaults. API: `routers/documents.py`; web: `components/documents/`, `components/library/`.

## Scope
- Walk every studio capability against a fixture job and fix friction: template/voice switch previews, lock-paragraph affordance (visible lock state, hover explanation), regen with locked paragraphs (locked content provably preserved), inline edit autosave/save state visibility, version history navigation (clear current-vs-past, restore/duplicate paths), PDF download naming.
- Micro-interactions per the design direction: state transitions animated via motion tokens (lock toggle, regen shimmer/skeleton on regenerating paragraphs, save confirmation tick), never decorative-only.
- ATS keyword coverage display: legible, explains itself (what it measures, why it matters in one tooltip).
- Stub-LLM honesty: when the template provider is active (no `LLM_API_KEY`), the UI labels drafts as template output (positioning audit §19.7).
- Budget exhaustion (HTTP 402) renders a designed state with the path to resolve (settings/BYOK), not a toast error.
- Run-canvas Documents tab parity: same components, same states as the library studio.

## Out of Scope
- New templates, voices, or generation features; prompt changes.
- DOCX export or new formats (creep).
- LLM gateway changes (402 contract stays as-is).

## Starting Checklist
1. Read `apps/api/src/jober_api/routers/documents.py` and `services/documents/` (incl. `cover_letter_generator.py`, `generation_prefs.py` — both touched by the Mission 01 formatting landing).
2. Read `components/documents/` and the canvas Documents tab wiring.
3. Run the studio locally against a fixture job in both LLM modes (with and without `LLM_API_KEY`).
4. Read `apps/api/tests/test_cover_letter_v2.py` and `test_documents_api.py` for contracted behavior.
5. Review screenshot `18-library-letters.png` for current state.

## Tasks
1. Capability walkthrough table (`docs/polish-pack/notes/17_studio_findings.md`): capability × {works, friction, broken}.
2. Fix broken/friction items worst-first; verify the lock-preserve guarantee with a test (regen with locks → locked text unchanged).
3. Implement the stub-mode label and the 402 designed state.
4. Add the micro-interaction set via `lib/design/motion.ts` tokens (must pass `pnpm check:motion`).
5. ATS coverage legibility pass.
6. Parity sweep between library studio and run-canvas tab (extract shared components where duplicated — feeds Mission 10's family system).
7. Re-capture screenshot 18; capture a studio-in-action shot for marketing reuse (Mission 07/08 assets).

## Self-Improvement Loop
1. Inspect the next capability with a real generate/edit/regen cycle.
2. Identify the highest-impact friction.
3. Make the smallest coherent improvement.
4. Validate (gates + the cycle re-run); re-capture the screenshot and compare against the north-star bar (Figma-grade editor precision).
5. Document in the findings table.
6. Repeat until every capability row is "works, no friction".

## Validation
- `cd apps/api && ruff check src tests && mypy src && pytest -q tests/test_cover_letter_v2.py tests/test_documents_api.py tests/test_cover_letter_generation.py` then the full suite
- `cd apps/web && pnpm typecheck && pnpm lint:strict && pnpm test && pnpm build && pnpm check:motion`
- `pnpm test:e2e`
- Manual: full generate → edit → lock → regen → duplicate → download cycle in both LLM modes; 402 state forced via budget config.

## Acceptance Criteria
1. Findings table fully green; lock-preservation is test-enforced.
2. Stub mode and 402 are honestly, beautifully labeled.
3. Studio and canvas tab share components and behavior.
4. Micro-interactions pass `check:motion` and reduced-motion.
5. All gates green; screenshot 18 re-captured and UI-REVIEW row closed.

## Documentation Requirements
- `docs/polish-pack/notes/17_studio_findings.md`.
- README Missions 05/24 sections corrected if behavior changed.

## Git Workflow
`git status` first; commits per capability cluster; reviewed diffs; bodies with what/why/validation/follow-ups; push after gates.

## Production Guidance
Deployable after gates pass. If the API contract changed at all, deploy API + web together; verify one production letter cycle (template mode is fine) post-deploy; `bash scripts/railway-smoke.sh`.
