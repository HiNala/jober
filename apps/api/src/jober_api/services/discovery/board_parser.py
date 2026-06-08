from __future__ import annotations

import re
from dataclasses import dataclass
from html import unescape
from urllib.parse import urljoin

import httpx
from jober_extraction.intelligence import _fit_score, _keyword_harvest

JOB_HREF_PATTERN = re.compile(
    r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]{2,120})</a>',
    re.I,
)
ATS_HOST_MARKERS = (
    "lever.co",
    "greenhouse.io",
    "ashbyhq.com",
    "workday",
    "jobvite",
    "teamtailor",
    "personio",
)


@dataclass(frozen=True)
class BoardPosting:
    company: str
    role: str
    url: str


def _is_job_url(url: str) -> bool:
    lower = url.casefold()
    return any(marker in lower for marker in ATS_HOST_MARKERS)


def parse_board_html(
    *,
    html: str,
    board_name: str,
    base_url: str | None = None,
) -> list[BoardPosting]:
    postings: list[BoardPosting] = []
    seen: set[str] = set()
    for match in JOB_HREF_PATTERN.finditer(html):
        href = unescape(match.group(1).strip())
        label = unescape(re.sub(r"\s+", " ", match.group(2).strip()))
        if base_url and href.startswith("/"):
            href = urljoin(base_url, href)
        if not href.startswith("http") or not _is_job_url(href):
            continue
        if href in seen:
            continue
        seen.add(href)
        role = label or href.rstrip("/").split("/")[-1].replace("-", " ").title()
        postings.append(BoardPosting(company=board_name, role=role, url=href))
    return postings


async def fetch_board_html(url: str, *, fixture_html: str | None = None) -> str:
    if fixture_html is not None:
        return fixture_html
    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text


def estimate_fit_score(role: str, resume_skills: list[str]) -> float | None:
    keywords = _keyword_harvest(role)
    score = _fit_score(keywords, resume_skills)
    return float(score) if score is not None else None
