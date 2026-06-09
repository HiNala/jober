from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.enums import DocumentType
from jober_api.models.generated_document import GeneratedDocument
from jober_api.models.job_target import JobTarget
from jober_api.repositories.cover_letter_angle import CoverLetterAngleRepository
from jober_api.repositories.generated_document import GeneratedDocumentRepository
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.repositories.resume_asset import ResumeAssetRepository
from jober_api.repositories.user_profile import UserProfileRepository
from jober_api.services.analytics.collector import emit_server_event
from jober_api.services.analytics.rollups import server_session_id
from jober_api.services.documents.ats_scoring import KeywordCoverageReport, score_keyword_coverage
from jober_api.services.documents.claims_guard import (
    ClaimsGuardResult,
    DraftLetter,
    parse_draft_payload,
    verify_draft_claims,
)
from jober_api.services.documents.generation_prefs import load_letter_defaults
from jober_api.services.documents.letter_editor import (
    join_paragraphs,
    merge_paragraphs,
    split_paragraphs,
)
from jober_api.services.documents.letter_styles import (
    normalize_template,
    normalize_voice_preset,
    voice_prompt,
)
from jober_api.services.documents.prompt_pack import (
    SYSTEM_INSTRUCTIONS,
    GenerationContext,
    pack_user_prompt,
)
from jober_api.services.documents.render_docx import render_cover_letter_docx
from jober_api.services.documents.render_pdf import render_cover_letter_pdf
from jober_api.services.documents.variant_mapping import (
    map_fit_lane_to_variant,
    match_angle_use_case,
)
from jober_api.services.llm.gateway import (
    assert_budget,
    log_llm_call,
    resolve_llm_runtime,
)
from jober_api.storage.keys import document_docx_key, document_pdf_key
from jober_api.storage.minio_client import ObjectStorage


class ClaimsRejectedError(Exception):
    def __init__(self, unsupported: list[str]) -> None:
        self.unsupported = unsupported
        super().__init__(f"Unsupported claims: {', '.join(unsupported)}")


def _word_count(text: str) -> int:
    return len(text.split())


def _claims_index_from_resume(resume: Any) -> dict[str, Any]:
    skills_index = resume.skills_index or {}
    embedded = skills_index.get("claims_index")
    if isinstance(embedded, dict):
        return embedded
    from jober_api.services.claims_index import build_claims_index

    return build_claims_index(resume.extracted_text or "", skills_index)


async def generate_cover_letter(
    session: AsyncSession,
    storage: ObjectStorage,
    *,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    job_target_id: uuid.UUID,
    force: bool = False,
    include_docx: bool = True,
    job_description: str = "",
    job_requirements: str = "",
    company_summary: str = "",
    run_id: uuid.UUID | None = None,
    template_style: str | None = None,
    voice_preset: str | None = None,
    locked_paragraphs: list[int] | None = None,
    regenerate_paragraph_index: int | None = None,
    parent_document_id: uuid.UUID | None = None,
    seed_text: str | None = None,
) -> dict[str, Any]:
    jobs = JobTargetRepository(session, tenant_id)
    job = await jobs.get(job_target_id)
    if job is None:
        msg = "Job target not found"
        raise ValueError(msg)

    profiles = UserProfileRepository(session, tenant_id)
    profile = await profiles.get_singleton()
    resumes = ResumeAssetRepository(session, tenant_id)
    resume = await resumes.get_active()
    if resume is None or not resume.extracted_text:
        msg = "Upload a canonical resume before generating a cover letter"
        raise ValueError(msg)

    prefs = await load_letter_defaults(session, tenant_id=tenant_id, user_id=user_id)
    resolved_template = normalize_template(template_style or prefs["template_style"])
    resolved_voice = normalize_voice_preset(voice_preset or prefs["voice_preset"])
    locked_set = {int(i) for i in (locked_paragraphs or [])}

    docs = GeneratedDocumentRepository(session)
    if not force and regenerate_paragraph_index is None and not seed_text:
        cached = await docs.find_cached_cover_letter(job_target_id, resume.id)
        if cached is not None:
            meta = dict(cached.keyword_coverage or {})
            if (
                meta.get("template_style") == resolved_template
                and meta.get("voice_preset") == resolved_voice
            ):
                return _serialize_document(cached, cached=True)

    await assert_budget(session)

    variant = map_fit_lane_to_variant(job.fit_lane)
    angle_repo = CoverLetterAngleRepository(session)
    angle = None
    use_case = match_angle_use_case(job.fit_lane, job.cover_letter_hook)
    if use_case:
        angle = await angle_repo.find_by_use_case(use_case)
    if angle is None:
        angles = await angle_repo.list_all(limit=1)
        angle = angles[0] if angles else None

    extracted_desc, extracted_reqs, extracted_summary = _extraction_context(job)
    ctx = GenerationContext(
        job=job,
        resume=resume,
        profile=profile,
        angle=angle,
        job_description=job_description or extracted_desc or _fallback_job_description(job),
        job_requirements=job_requirements or extracted_reqs,
        company_summary=company_summary or extracted_summary,
        resume_variant=variant,
        voice_notes=voice_prompt(resolved_voice),
    )
    user_prompt = pack_user_prompt(ctx)
    if regenerate_paragraph_index is not None and seed_text:
        user_prompt += (
            f"\n\nREGENERATE ONLY paragraph index {regenerate_paragraph_index}. "
            f"Keep other paragraphs unchanged in meaning. Current letter:\n{seed_text[:4000]}"
        )
    elif seed_text:
        user_prompt += (
            "\n\nSTART FROM THIS DRAFT (preserve facts, improve flow):\n"
            f"{seed_text[:4000]}"
        )

    provider, llm_runtime = await resolve_llm_runtime(session, user_id)

    claims_index = _claims_index_from_resume(resume)
    guard_result: ClaimsGuardResult | None = None
    draft: DraftLetter | None = None

    for attempt in range(3):
        completion = await provider.complete(
            model=llm_runtime.draft_model,
            system=SYSTEM_INSTRUCTIONS,
            user=user_prompt
            if attempt == 0
            else user_prompt
            + "\n\nRETRY: Remove any unsupported claims. Resume is the only source of truth.",
        )
        await log_llm_call(
            session,
            agent_role="document_agent_draft",
            completion=completion,
            system=SYSTEM_INSTRUCTIONS,
            user=user_prompt,
            run_id=run_id,
        )
        await assert_budget(session, completion.cost_usd)

        draft = parse_draft_payload(completion.content)
        guard_result = verify_draft_claims(draft, claims_index)
        if guard_result.ok:
            break

    if draft is None or guard_result is None or not guard_result.ok:
        unsupported = guard_result.unsupported if guard_result else []
        raise ClaimsRejectedError(unsupported)

    body = draft.body
    if seed_text and (locked_set or regenerate_paragraph_index is not None):
        original = split_paragraphs(seed_text)
        updated = split_paragraphs(body)
        if regenerate_paragraph_index is not None and regenerate_paragraph_index < len(updated):
            merged = list(original)
            while len(merged) <= regenerate_paragraph_index:
                merged.append("")
            if regenerate_paragraph_index not in locked_set:
                merged[regenerate_paragraph_index] = updated[regenerate_paragraph_index]
            body = join_paragraphs(
                merge_paragraphs(
                    original=original,
                    updated=merged,
                    locked_indices=locked_set,
                )
            )
        elif locked_set:
            body = join_paragraphs(
                merge_paragraphs(
                    original=original,
                    updated=updated,
                    locked_indices=locked_set,
                )
            )

    coverage = score_keyword_coverage(
        body,
        ctx.job_description,
        ctx.job_requirements,
    )

    scoring_prompt = (
        f"Letter:\n{body[:2000]}\n\nTargets present: {coverage.present}\n"
        f"Missing: {coverage.missing}"
    )
    score_completion = await provider.complete(
        model=llm_runtime.scoring_model,
        system='Return JSON: {"notes": "brief ATS commentary"}',
        user=scoring_prompt,
        temperature=0.0,
    )
    await log_llm_call(
        session,
        agent_role="document_agent_score",
        completion=score_completion,
        system="score",
        user=scoring_prompt,
        run_id=run_id,
    )

    document_id = uuid.uuid4()
    applicant = profile.name if profile and profile.name else "Applicant"
    pdf_bytes = render_cover_letter_pdf(
        body=body,
        applicant_name=applicant,
        company=job.company,
        role=job.role,
        template=resolved_template,
    )
    pdf_key = document_pdf_key(job_target_id, document_id)
    await storage.put_object(pdf_key, pdf_bytes, content_type="application/pdf")

    docx_key: str | None = None
    if include_docx:
        docx_bytes = render_cover_letter_docx(
            body=body,
            applicant_name=applicant,
            company=job.company,
            role=job.role,
            template=resolved_template,
        )
        docx_key = document_docx_key(job_target_id, document_id)
        await storage.put_object(
            docx_key,
            docx_bytes,
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

    version = 1
    if parent_document_id:
        parent = await docs.get(parent_document_id)
        if parent is not None:
            parent_meta = parent.keyword_coverage or {}
            version = int(parent_meta.get("version") or 1) + 1

    keyword_payload = _coverage_to_dict(
        coverage,
        draft,
        resume.id,
        variant,
        template_style=resolved_template,
        voice_preset=resolved_voice,
        locked_paragraphs=sorted(locked_set),
        parent_document_id=parent_document_id,
        version=version,
        job=job,
    )

    row = await docs.create(
        id=document_id,
        job_target_id=job_target_id,
        run_id=run_id,
        document_type=DocumentType.COVER_LETTER,
        object_key_pdf=pdf_key,
        object_key_docx=docx_key,
        text=body,
        keyword_coverage=keyword_payload,
        ats_score=coverage.ats_score,
        generated_at=datetime.now(UTC),
    )
    await session.flush()
    await session.refresh(row)

    await emit_server_event(
        session,
        name="letter.generate",
        session_id=server_session_id(run_id=run_id) if run_id else server_session_id(),
        tenant_id=job.tenant_id,
        props={"document_id": str(row.id), "job_target_id": str(job_target_id)},
    )

    return _serialize_document(row, cached=False)


def _extraction_context(job: JobTarget) -> tuple[str, str, str]:
    raw = job.extracted_job_profile
    if not isinstance(raw, dict):
        return "", "", ""
    description = str(raw.get("description") or "")
    requirements_list = raw.get("requirements")
    requirements = (
        "\n".join(str(r) for r in requirements_list) if isinstance(requirements_list, list) else ""
    )
    summary = str(raw.get("company_product_summary") or "")
    return description, requirements, summary


def _fallback_job_description(job: JobTarget) -> str:
    parts = [job.role, job.company]
    if job.why_fit:
        parts.append(job.why_fit)
    if job.stage_signal:
        parts.append(job.stage_signal)
    if job.cover_letter_hook:
        parts.append(f"Hook: {job.cover_letter_hook}")
    return ". ".join(parts)


def _coverage_to_dict(
    coverage: KeywordCoverageReport,
    draft: DraftLetter,
    resume_id: uuid.UUID,
    variant: str,
    *,
    template_style: str,
    voice_preset: str,
    locked_paragraphs: list[int],
    parent_document_id: uuid.UUID | None,
    version: int,
    job: JobTarget,
) -> dict[str, Any]:
    return {
        "present": coverage.present,
        "missing": coverage.missing,
        "density": coverage.density,
        "stuffing_penalty": coverage.stuffing_penalty,
        "resume_asset_id": str(resume_id),
        "resume_variant": variant,
        "asserted_facts": draft.asserted_facts,
        "paragraph_grounding": draft.paragraph_grounding,
        "explain": draft.paragraph_grounding,
        "template_style": template_style,
        "voice_preset": voice_preset,
        "locked_paragraphs": locked_paragraphs,
        "parent_document_id": str(parent_document_id) if parent_document_id else None,
        "version": version,
        "ab_tracking": {
            "template_style": template_style,
            "voice_preset": voice_preset,
            "fit_lane": job.fit_lane,
            "company": job.company,
            "role": job.role,
        },
    }


def _serialize_document(row: GeneratedDocument, *, cached: bool) -> dict[str, Any]:
    meta = row.keyword_coverage or {}
    return {
        "id": str(row.id),
        "job_target_id": str(row.job_target_id),
        "run_id": str(row.run_id) if row.run_id else None,
        "document_type": row.document_type.value,
        "text": row.text,
        "keyword_coverage": row.keyword_coverage,
        "ats_score": row.ats_score,
        "generated_at": row.generated_at.isoformat() if row.generated_at else None,
        "object_key_pdf": row.object_key_pdf,
        "object_key_docx": row.object_key_docx,
        "cached": cached,
        "template_style": meta.get("template_style"),
        "voice_preset": meta.get("voice_preset"),
        "locked_paragraphs": meta.get("locked_paragraphs") or [],
        "version": meta.get("version", 1),
        "pdf_download_path": f"/api/documents/{row.id}/download/pdf",
        "docx_download_path": (
            f"/api/documents/{row.id}/download/docx" if row.object_key_docx else None
        ),
    }


async def duplicate_cover_letter(
    session: AsyncSession,
    storage: ObjectStorage,
    *,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    document_id: uuid.UUID,
    target_job_target_id: uuid.UUID | None = None,
) -> dict[str, Any]:
    docs = GeneratedDocumentRepository(session)
    source = await docs.get(document_id)
    if source is None or source.text is None:
        msg = "Document not found"
        raise ValueError(msg)
    jobs = JobTargetRepository(session, tenant_id)
    job_id = target_job_target_id or source.job_target_id
    job = await jobs.get(job_id)
    if job is None:
        msg = "Job target not found"
        raise ValueError(msg)
    meta = dict(source.keyword_coverage or {})
    return await generate_cover_letter(
        session,
        storage,
        tenant_id=tenant_id,
        user_id=user_id,
        job_target_id=job_id,
        force=True,
        seed_text=source.text,
        template_style=str(meta.get("template_style") or "classic"),
        voice_preset=str(meta.get("voice_preset") or "direct"),
        locked_paragraphs=list(meta.get("locked_paragraphs") or []),
        parent_document_id=source.id,
    )
