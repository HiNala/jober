from __future__ import annotations

import re


def extract_company_product_summary(
    visible_text: str,
    *,
    company: str,
    max_words: int = 60,
) -> str | None:
    """Lightweight opener fuel for cover letters — first substantive about blurb."""
    patterns = (
        re.compile(
            rf"{re.escape(company)}.+?(?:builds?|is|helps?|provides?).{{20,400}}?\.",
            re.I | re.S,
        ),
        re.compile(r"about\s+(?:us|the company)[:\s]+(.{40,400}?)\.", re.I | re.S),
        re.compile(r"who we are[:\s]+(.{40,400}?)\.", re.I | re.S),
    )
    for pattern in patterns:
        match = pattern.search(visible_text)
        if match:
            snippet = match.group(0) if match.lastindex is None else match.group(1)
            words = snippet.split()
            if len(words) >= 8:
                return " ".join(words[:max_words]).strip()
    return None
