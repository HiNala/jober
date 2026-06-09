from __future__ import annotations

from io import BytesIO

from docx import Document
from docx.shared import Pt

from jober_api.services.documents.letter_styles import normalize_template


def _font_size_for_template(template: str) -> int:
    key = normalize_template(template)
    if key == "compact":
        return 10
    if key == "modern":
        return 11
    return 11


def render_cover_letter_docx(
    *,
    body: str,
    applicant_name: str,
    company: str,
    role: str,
    template: str = "classic",
) -> bytes:
    document = Document()
    size = _font_size_for_template(template)
    name_para = document.add_paragraph(applicant_name)
    if name_para.runs:
        name_para.runs[0].bold = True
        name_para.runs[0].font.size = Pt(size)
    document.add_paragraph(f"Re: {role} at {company}")
    document.add_paragraph("")
    for paragraph in body.split("\n\n"):
        text = paragraph.strip()
        if text:
            para = document.add_paragraph(text)
            if para.runs:
                para.runs[0].font.size = Pt(size)
    buffer = BytesIO()
    document.save(buffer)
    return buffer.getvalue()
