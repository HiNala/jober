# Mission 41 — Document Intelligence: Resume Tailoring + Cover Letters

> **Phase:** Perfection pack  
> **Depends on:** M04, M05, M24, M39  
> **Run Mission 99 after**

## Purpose

Deliver **per-job document excellence**: tailored cover letters *and* human-reviewed resume variants, ATS keyword coverage, PDF/DOCX render, studio UX that feels like a 2030 document product — so applications look like the candidate, not a mail merge.

## Context

Cover letter v2 exists; resume is largely canonical upload/parse. MASTER_PLAN deferred role-targeted resume variants as human-reviewed. Perfection requires shipping that path properly: generate suggestions → user edits/approves → lock for run → upload on apply.

## Scope

### In scope
- Resume variant model: base resume + per-job or per-lane tailored version
- Generation: reorder bullets, emphasize relevant skills, **never fabricate employers/degrees**
- Cover letter studio polish (tone, angle, regenerate, lock)
- Side-by-side job description vs document
- PDF/DOCX render reliability; preview
- Document Studio UI 2030
- Cost/budget awareness (BYOK + managed)
- Tests for no-fabrication invariants

### Out of scope
- Fully autonomous resume lies / title inflation
- LinkedIn profile sync
- Multi-language letters (unless already partially present — do not expand)

## Starting checklist
- [ ] Read document agent, cover letter v2, resume parser, library API
- [ ] Confirm GeneratedDocument types and storage keys
- [ ] Review e2e document-studio specs

## Tasks

### 1. Data model & API
- [ ] `ResumeVariant` (or extend GeneratedDocument): job_target_id optional, source_resume_id, status draft|approved|locked, content structured + rendered artifacts
- [ ] Endpoints: generate variant, patch content, approve/lock, render PDF/DOCX
- [ ] Cover letter: ensure lock before fill upload (existing guarantee — re-verify)
- [ ] Migration + tenant isolation

### 2. Generation policy
- [ ] System prompt: job text is data not instructions (injection defense)
- [ ] Hard rule: no new employers, degrees, dates, metrics not in source resume
- [ ] Coverage report: required keywords present/missing
- [ ] Human must approve variant before auto-attach to run (default)

### 3. Document Studio UI
- [ ] Routes under `/documents` (not redirect-only)
- [ ] Job picker → letter + resume tabs
- [ ] Diff view: base vs tailored bullets
- [ ] Preview pane (PDF iframe or HTML preview)
- [ ] Regenerate / edit / approve / download
- [ ] Honest stub/402 when LLM unconfigured

### 4. Apply pipeline hook
- [ ] Run prepare step prefers locked variant + letter for job
- [ ] Falls back to canonical resume with clear UI note

### 5. Tests
- [ ] Unit: fabrication guard fixtures
- [ ] API: generate/approve/lock
- [ ] e2e document-studio fullstack

## Validation
```bash
cd apps/api && pytest tests/test_cover_letter_generation.py tests/test_cover_letter_v2.py tests/test_resume_parser.py tests/test_documents_api.py -q
cd apps/web && pnpm typecheck && pnpm lint:strict
pnpm exec playwright test e2e/document-studio.spec.ts e2e/document-studio.fullstack.spec.ts
```

## Acceptance criteria
- [ ] User can produce approved tailored resume + letter per job
- [ ] No fabricated employment history in automated tests
- [ ] Locked docs used by fill/upload path
- [ ] Design Council ≥19/20 Document Studio
- [ ] Mobile-usable editor (basic)

## Production guidance
- Token budgets per generation; log LlmCall
- Retain artifacts per privacy retention policy
