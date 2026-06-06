from __future__ import annotations

import re
from io import BytesIO

SKILLS_HEADER = re.compile(r"^\s*skills?\b", re.I | re.M)


def extract_pdf_text(data: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(BytesIO(data))
    parts: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            parts.append(text)
    return "\n".join(parts).strip()


def extract_docx_text(data: bytes) -> str:
    from docx import Document

    document = Document(BytesIO(data))
    return "\n".join(p.text for p in document.paragraphs if p.text.strip()).strip()


def extract_resume_text(data: bytes, filename: str) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return extract_pdf_text(data)
    if lower.endswith(".docx"):
        return extract_docx_text(data)
    msg = "Unsupported resume format — upload PDF or DOCX"
    raise ValueError(msg)


def parse_skills_index(text: str) -> dict[str, list[str]]:
    if not text.strip():
        return {"skills": [], "sections": []}

    match = SKILLS_HEADER.search(text)
    skills_block = text[match.start() :] if match else text
    if match:
        skills_block = skills_block.split("\n", 1)[-1]

    stop = re.search(
        r"^\s*(experience|education|projects|certifications|summary)\b",
        skills_block,
        re.I | re.M,
    )
    if stop:
        skills_block = skills_block[: stop.start()]

    skills: list[str] = []
    for line in skills_block.splitlines():
        cleaned = line.strip("•·-* \t")
        if not cleaned or len(cleaned) < 2:
            continue
        if cleaned.lower().startswith("skills"):
            continue
        if "," in cleaned:
            skills.extend(s.strip() for s in cleaned.split(",") if s.strip())
        else:
            skills.append(cleaned)

    deduped: list[str] = []
    seen: set[str] = set()
    for skill in skills:
        key = skill.casefold()
        if key not in seen:
            seen.add(key)
            deduped.append(skill)
    return {"skills": deduped, "sections": ["skills"] if deduped else []}
