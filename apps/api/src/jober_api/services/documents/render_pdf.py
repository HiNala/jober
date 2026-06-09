from __future__ import annotations

from io import BytesIO

from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from jober_api.services.documents.letter_styles import normalize_template


def _layout_for_template(template: str) -> tuple[float, float, float, int, int]:
    """Margins (L,R,T), body size, leading."""
    key = normalize_template(template)
    if key == "modern":
        return 60.0, 60.0, 54.0, 11, 16
    if key == "compact":
        return 72.0, 72.0, 48.0, 10, 13
    return 72.0, 72.0, 72.0, 11, 15


def render_cover_letter_pdf(
    *,
    body: str,
    applicant_name: str,
    company: str,
    role: str,
    template: str = "classic",
) -> bytes:
    left, right, top, font_size, leading = _layout_for_template(template)
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=left,
        rightMargin=right,
        topMargin=top,
    )
    styles = getSampleStyleSheet()
    body_style = ParagraphStyle(
        "LetterBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=font_size,
        leading=leading,
        alignment=TA_LEFT,
        spaceAfter=10,
    )
    header_style = ParagraphStyle(
        "LetterHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=font_size,
        spaceAfter=16,
    )

    story: list[object] = [
        Paragraph(applicant_name, header_style),
        Paragraph(f"Re: {role} at {company}", styles["Normal"]),
        Spacer(1, 12),
    ]
    for paragraph in body.split("\n\n"):
        text = paragraph.strip()
        if text:
            story.append(Paragraph(text.replace("\n", "<br/>"), body_style))

    doc.build(story)
    return buffer.getvalue()
