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


def render_resume_pdf(
    *,
    body: str,
    applicant_name: str,
    target_role: str | None = None,
    target_company: str | None = None,
) -> bytes:
    """ATS-friendly resume layout (not a cover-letter 'Re:' header)."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54.0,
        rightMargin=54.0,
        topMargin=48.0,
        bottomMargin=48.0,
    )
    styles = getSampleStyleSheet()
    name_style = ParagraphStyle(
        "ResumeName",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        spaceAfter=4,
        alignment=TA_LEFT,
    )
    meta_style = ParagraphStyle(
        "ResumeMeta",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor="#444444",
        spaceAfter=10,
    )
    section_style = ParagraphStyle(
        "ResumeSection",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        spaceBefore=10,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "ResumeBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        alignment=TA_LEFT,
        spaceAfter=4,
    )

    story: list[object] = [Paragraph(applicant_name, name_style)]
    meta_bits = [b for b in (target_role, target_company) if b]
    if meta_bits:
        # Tailored for role — not "Re: …" letter framing.
        story.append(Paragraph(" · ".join(meta_bits), meta_style))
    story.append(Spacer(1, 6))

    for block in body.split("\n\n"):
        text = block.strip()
        if not text:
            continue
        lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
        if len(lines) == 1 and lines[0].isupper() and len(lines[0]) < 48:
            story.append(Paragraph(lines[0].title(), section_style))
            continue
        # Short Title Case single line is often a section header
        title_ish = (
            len(lines) == 1
            and len(lines[0]) < 40
            and lines[0] == lines[0].title()
            and ":" not in lines[0]
        )
        if title_ish:
            story.append(Paragraph(lines[0], section_style))
            continue
        story.append(Paragraph(text.replace("\n", "<br/>"), body_style))

    doc.build(story)
    return buffer.getvalue()
