import re

ATS_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("ashby", re.compile(r"ashbyhq\.com|jobs\.ashby", re.I)),
    ("lever", re.compile(r"jobs\.lever\.co|lever\.co", re.I)),
    ("greenhouse", re.compile(r"greenhouse\.io|boards\.greenhouse", re.I)),
    ("workday", re.compile(r"myworkdayjobs\.com|workday\.com", re.I)),
    ("jobvite", re.compile(r"jobvite\.com", re.I)),
    ("teamtailor", re.compile(r"teamtailor\.com", re.I)),
]


def guess_ats(url: str | None) -> str | None:
    if not url or not url.strip():
        return None
    for name, pattern in ATS_PATTERNS:
        if pattern.search(url):
            return name
    return None


def needs_apply_url(direct_apply_url: str | None, company_careers_url: str | None) -> bool:
    return not (direct_apply_url and direct_apply_url.strip()) and not (
        company_careers_url and company_careers_url.strip()
    )
