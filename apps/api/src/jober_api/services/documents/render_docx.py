from __future__ import annotations

from io import BytesIO

from docx import Document


def render_cover_letter_docx(
    *,
    body: str,
    applicant_name: str,
    company: str,
    role: str,
) -> bytes:
    document = Document()
    document.add_paragraph(applicant_name)
    document.add_paragraph(f"Re: {role} at {company}")
    document.add_paragraph("")
    for paragraph in body.split("\n\n"):
        text = paragraph.strip()
        if text:
            document.add_paragraph(text)
    buffer = BytesIO()
    document.save(buffer)
    return buffer.getvalue()
