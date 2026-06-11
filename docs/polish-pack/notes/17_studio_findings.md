# Mission 17 — Document Studio and cover letter UX findings

**Validated:** 2026-06-10 · Capability matrix for library studio and run-canvas Documents tab.

## Capability matrix

| Capability | Library studio | Run canvas Documents | Result | Notes |
|------------|----------------|----------------------|--------|-------|
| Job picker + generate | Yes | Via run package | **Green** | Studio wired at `/library?tab=letters&view=studio` |
| Template / voice presets | Yes | Inherited from doc | **Green** | Selects in studio sidebar |
| Inline edit + save | Yes | Yes | **Green** | Save tick via `motionStatusEnter` |
| Per-paragraph lock | Yes | Yes | **Green** | Shared `ParagraphControls` + tooltip |
| Per-paragraph regen | Yes | Yes | **Green** | Locked text preserved — `mergeParagraphs` unit test |
| Full-letter regen | Yes | — | **Green** | Force regenerate respects locks (API) |
| Duplicate version | Yes | Yes | **Green** | `duplicateCoverLetter` |
| Version badge | Yes | Yes | **Green** | `v{n}` badge when present |
| ATS + keyword coverage | Yes | Yes | **Green** | Shared `KeywordCoveragePanel` + help tooltip |
| PDF download naming | Yes | Yes | **Green** | `cover-letter-{company}-{role}.pdf` |
| Stub LLM honesty | Yes | Yes | **Green** | `LlmProviderBanner` when `provider === "template"` |
| Budget exhaustion (402) | Yes | Yes | **Green** | `LlmBudgetExceeded` panel, not toast-only |
| Regen shimmer | Yes | Yes | **Green** | `motionShimmer` on textarea / paragraph row |
| Saved letters list | Yes | — | **Green** | Sub-nav Saved letters |
| `/documents` deep link | Redirect | — | **Green** | → `view=studio` (fixes empty-state loop) |

## Architecture

- **Shared components:** `paragraph-controls`, `keyword-coverage-panel`, `llm-provider-banner`, `llm-budget-exceeded`
- **Client lock mirror:** `lib/documents/merge-paragraphs.ts` (API contract in `test_cover_letter_v2.py`)
- **Parity:** `CoverLetterEditor` (canvas) and `DocumentStudio` (library) use the same controls

## Deferrals

| Item | Owner |
|------|-------|
| Re-capture screenshot `18-library-letters.png` | Operator / Mission 07 asset pass |
| Studio-in-action marketing shot | Mission 07/08 |
| Full generate→regen e2e with fixture job + letter | Mission 26 |
| Version history timeline UI | Out of scope (duplicate covers fork) |
| DOCX export polish | Out of scope |

## Gates

- Web: typecheck, lint, test (`merge-paragraphs`, `errors`), build, `check:motion`, e2e `document-studio.spec.ts`
- API: `test_cover_letter_v2.py` lock preservation (CI)
