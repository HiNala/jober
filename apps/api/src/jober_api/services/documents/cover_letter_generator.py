from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.config import settings
from jober_api.models.enums import DocumentType
from jober_api.models.generated_document import GeneratedDocument
from jober_api.models.job_target import JobTarget
from jober_api.repositories.cover_letter_angle import CoverLetterAngleRepository
from jober_api.repositories.generated_document import GeneratedDocumentRepository
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.repositories.resume_asset import ResumeAssetRepository
from jober_api.repositories.user_profile import UserProfileRepository
from jober_api.services.documents.ats_scoring import KeywordCoverageReport, score_keyword_coverage
from jober_api.services.documents.claims_guard import (
    ClaimsGuardResult,
    DraftLetter,
    parse_draft_payload,
    verify_draft_claims,
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
    get_llm_provider,
    log_llm_call,
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
    job_target_id: uuid.UUID,
    force: bool = False,
    include_docx: bool = True,
    job_description: str = "",
    job_requirements: str = "",
    company_summary: str = "",
) -> dict[str, Any]:
    jobs = JobTargetRepository(session)
    job = await jobs.get(job_target_id)
    if job is None:
        msg = "Job target not found"
        raise ValueError(msg)

    profiles = UserProfileRepository(session)
    profile = await profiles.get_singleton()
    resumes = ResumeAssetRepository(session)
    resume = await resumes.get_active()
    if resume is None or not resume.extracted_text:
        msg = "Upload a canonical resume before generating a cover letter"
        raise ValueError(msg)

    docs = GeneratedDocumentRepository(session)
    if not force:
        cached = await docs.find_cached_cover_letter(job_target_id, resume.id)
        if cached is not None:
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
        voice_notes="direct, founder/operator, product-minded, technically credible",
    )
    user_prompt = pack_user_prompt(ctx)
    provider = get_llm_provider()

    claims_index = _claims_index_from_resume(resume)
    guard_result: ClaimsGuardResult | None = None
    draft: DraftLetter | None = None

    for attempt in range(3):
        completion = await provider.complete(
            model=settings.llm_draft_model,
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
        )
        await assert_budget(session, completion.cost_usd)

        draft = parse_draft_payload(completion.content)
        guard_result = verify_draft_claims(draft, claims_index)
        if guard_result.ok:
            break

    if draft is None or guard_result is None or not guard_result.ok:
        unsupported = guard_result.unsupported if guard_result else []
        raise ClaimsRejectedError(unsupported)

    wc = _word_count(draft.body)
    if wc < 200 or wc > 450:
        pass  # template path may be shorter; warn in metadata only

    coverage = score_keyword_coverage(
        draft.body,
        ctx.job_description,
        ctx.job_requirements,
    )

    scoring_prompt = (
        f"Letter:\n{draft.body[:2000]}\n\nTargets present: {coverage.present}\n"
        f"Missing: {coverage.missing}"
    )
    score_completion = await provider.complete(
        model=settings.llm_scoring_model,
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
    )

    document_id = uuid.uuid4()
    applicant = profile.name if profile and profile.name else "Applicant"
    pdf_bytes = render_cover_letter_pdf(
        body=draft.body,
        applicant_name=applicant,
        company=job.company,
        role=job.role,
    )
    pdf_key = document_pdf_key(job_target_id, document_id)
    await storage.put_object(pdf_key, pdf_bytes, content_type="application/pdf")

    docx_key: str | None = None
    if include_docx:
        docx_bytes = render_cover_letter_docx(
            body=draft.body,
            applicant_name=applicant,
            company=job.company,
            role=job.role,
        )
        docx_key = document_docx_key(job_target_id, document_id)
        await storage.put_object(
            docx_key,
            docx_bytes,
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

    keyword_payload = _coverage_to_dict(coverage, draft, resume.id, variant)

    row = await docs.create(
        id=document_id,
        job_target_id=job_target_id,
        document_type=DocumentType.COVER_LETTER,
        object_key_pdf=pdf_key,
        object_key_docx=docx_key,
        text=draft.body,
        keyword_coverage=keyword_payload,
        ats_score=coverage.ats_score,
        generated_at=datetime.now(UTC),
    )
    await session.flush()
    await session.refresh(row)
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
    return ". ".join(parts)


def _coverage_to_dict(
    coverage: KeywordCoverageReport,
    draft: DraftLetter,
    resume_id: uuid.UUID,
    variant: str,
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
    }


def _serialize_document(row: GeneratedDocument, *, cached: bool) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "job_target_id": str(row.job_target_id),
        "document_type": row.document_type.value,
        "text": row.text,
        "keyword_coverage": row.keyword_coverage,
        "ats_score": row.ats_score,
        "generated_at": row.generated_at.isoformat() if row.generated_at else None,
        "object_key_pdf": row.object_key_pdf,
        "object_key_docx": row.object_key_docx,
        "cached": cached,
        "pdf_download_path": f"/api/documents/{row.id}/download/pdf",
        "docx_download_path": (
            f"/api/documents/{row.id}/download/docx" if row.object_key_docx else None
        ),
    }
