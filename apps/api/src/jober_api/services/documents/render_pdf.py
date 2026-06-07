from __future__ import annotations

from io import BytesIO

from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def render_cover_letter_pdf(
    *,
    body: str,
    applicant_name: str,
    company: str,
    role: str,
) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=72, rightMargin=72, topMargin=72)
    styles = getSampleStyleSheet()
    body_style = ParagraphStyle(
        "LetterBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        alignment=TA_LEFT,
        spaceAfter=10,
    )
    header_style = ParagraphStyle(
        "LetterHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        spaceAfter=16,
    )

    story: list[object] = [
        Paragraph(f"{applicant_name}", header_style),
        Paragraph(f"Re: {role} at {company}", styles["Normal"]),
        Spacer(1, 12),
    ]
    for paragraph in body.split("\n\n"):
        text = paragraph.strip()
        if text:
            story.append(Paragraph(text.replace("\n", "<br/>"), body_style))

    doc.build(story)
    return buffer.getvalue()
