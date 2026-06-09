from __future__ import annotations

from typing import Any

from jober_api.models.generated_document import GeneratedDocument
from jober_api.models.job_target import JobTarget
from jober_api.services.documents.ats_scoring import score_keyword_coverage
from jober_api.services.documents.letter_styles import normalize_template
from jober_api.services.documents.render_docx import render_cover_letter_docx
from jober_api.services.documents.render_pdf import render_cover_letter_pdf
from jober_api.storage.keys import document_pdf_key
from jober_api.storage.minio_client import ObjectStorage


def split_paragraphs(body: str) -> list[str]:
    return [part.strip() for part in body.split("\n\n") if part.strip()]


def join_paragraphs(paragraphs: list[str]) -> str:
    return "\n\n".join(paragraphs)


def merge_paragraphs(
    *,
    original: list[str],
    updated: list[str],
    locked_indices: set[int],
) -> list[str]:
    merged: list[str] = []
    count = max(len(original), len(updated))
    for index in range(count):
        if index in locked_indices and index < len(original):
            merged.append(original[index])
        elif index < len(updated):
            merged.append(updated[index])
        elif index < len(original):
            merged.append(original[index])
    return merged


async def persist_letter_text(
    storage: ObjectStorage,
    *,
    row: GeneratedDocument,
    job: JobTarget,
    body: str,
    applicant_name: str,
    job_description: str = "",
    job_requirements: str = "",
) -> dict[str, Any]:
    meta = dict(row.keyword_coverage or {})
    template_style = normalize_template(meta.get("template_style"))
    locked = {int(i) for i in meta.get("locked_paragraphs") or [] if str(i).isdigit()}

    paragraphs = split_paragraphs(body)
    if locked and row.text:
        prior = split_paragraphs(row.text)
        paragraphs = merge_paragraphs(original=prior, updated=paragraphs, locked_indices=locked)
        body = join_paragraphs(paragraphs)

    coverage = score_keyword_coverage(body, job_description, job_requirements)
    pdf_bytes = render_cover_letter_pdf(
        body=body,
        applicant_name=applicant_name,
        company=job.company,
        role=job.role,
        template=template_style,
    )
    pdf_key = row.object_key_pdf or document_pdf_key(row.job_target_id, row.id)
    await storage.put_object(pdf_key, pdf_bytes, content_type="application/pdf")
    row.object_key_pdf = pdf_key

    if row.object_key_docx:
        docx_bytes = render_cover_letter_docx(
            body=body,
            applicant_name=applicant_name,
            company=job.company,
            role=job.role,
            template=template_style,
        )
        await storage.put_object(
            row.object_key_docx,
            docx_bytes,
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

    row.text = body
    row.ats_score = coverage.ats_score
    meta.update(
        {
            "present": coverage.present,
            "missing": coverage.missing,
            "density": coverage.density,
            "stuffing_penalty": coverage.stuffing_penalty,
            "manual_edit": True,
        }
    )
    row.keyword_coverage = meta
    return {
        "text": body,
        "ats_score": coverage.ats_score,
        "keyword_coverage": meta,
    }
