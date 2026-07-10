"""Resume layout must not look like a cover letter."""

from __future__ import annotations

from jober_api.services.documents.render_docx import render_resume_docx
from jober_api.services.documents.render_pdf import render_cover_letter_pdf, render_resume_pdf


def test_resume_pdf_is_valid_and_distinct_from_letter() -> None:
    body = (
        "SUMMARY\n\nFull-stack engineer with TypeScript and Python.\n\n"
        "EXPERIENCE\n\nAcme — Engineer\nBuilt APIs."
    )
    pdf = render_resume_pdf(
        body=body,
        applicant_name="Brian Permut",
        target_role="Staff Engineer",
        target_company="Northwind",
    )
    assert pdf[:4] == b"%PDF"
    assert len(pdf) > 200
    letter = render_cover_letter_pdf(
        body=body,
        applicant_name="Brian Permut",
        company="Northwind",
        role="Staff Engineer",
    )
    assert letter[:4] == b"%PDF"
    # Different layout → different PDF stream (not the same bytes).
    assert pdf != letter


def test_resume_docx_bytes() -> None:
    docx = render_resume_docx(
        body="SUMMARY\n\nBuilder.\n\nEXPERIENCE\n\nAcme",
        applicant_name="Brian Permut",
        target_role="Engineer",
        target_company="Acme",
    )
    # DOCX is a zip package
    assert docx[:2] == b"PK"
    assert len(docx) > 500
