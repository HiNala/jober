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

_TITLE_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "at",
        "for",
        "in",
        "of",
        "on",
        "or",
        "the",
        "to",
        "with",
    }
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
    from jober_api.security.outbound_url import OutboundUrlError, validate_outbound_url

    try:
        validate_outbound_url(url)
    except OutboundUrlError as exc:
        msg = str(exc)
        raise ValueError(msg) from exc
    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text


def _role_title_tokens(role: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9+#./-]{1,}", role)
    return [t for t in tokens if t.casefold() not in _TITLE_STOPWORDS]


def _matched_skills(role_text: str, resume_skills: list[str]) -> list[str]:
    """Resume skills that appear in role text or harvested keywords."""
    haystack = role_text.casefold()
    matched: list[str] = []
    seen: set[str] = set()
    for skill in resume_skills:
        label = skill.strip()
        if not label:
            continue
        key = label.casefold()
        if key in seen:
            continue
        if key in haystack:
            seen.add(key)
            matched.append(label)
    keywords = _keyword_harvest(role_text)
    resume_set = {s.casefold(): s for s in resume_skills}
    for kw in keywords:
        k = kw.casefold()
        if k in resume_set and k not in seen:
            seen.add(k)
            matched.append(resume_set[k])
    return matched[:8]


def estimate_fit_with_reasons(
    role: str,
    resume_skills: list[str],
    *,
    location_work_style: str | None = None,
    fit_lane: str | None = None,
    location_filter: str | None = None,
    stack: list[str] | None = None,
) -> tuple[float | None, list[str]]:
    """Return (fit_score 0–100 or None, explainable reason chips).

    Reasons cover matched skills, title keywords, and location when available.
    """
    stack_tokens = [str(s).strip() for s in (stack or []) if str(s).strip()]
    role_text = f"{role} {' '.join(stack_tokens)}".strip()
    reasons: list[str] = []
    score_parts: list[float] = []

    keywords = _keyword_harvest(role_text)
    skill_score = _fit_score(keywords, resume_skills) if keywords and resume_skills else None
    matched = _matched_skills(role_text, resume_skills)
    if matched:
        reasons.append(f"Matched skills: {', '.join(matched[:4])}")
    if skill_score is not None:
        score_parts.append(float(skill_score))

    title_tokens = _role_title_tokens(role)
    if title_tokens and resume_skills:
        resume_set = {s.casefold() for s in resume_skills}
        title_hits = [t for t in title_tokens if t.casefold() in resume_set]
        if not title_hits and stack_tokens:
            title_hits = [
                s
                for s in stack_tokens
                if any(
                    s.casefold() in t.casefold() or t.casefold() in s.casefold()
                    for t in title_tokens
                )
                or s.casefold() in role.casefold()
            ]
        if title_hits:
            reasons.append(f"Title keywords: {', '.join(title_hits[:4])}")
            score_parts.append(min(100.0, 35.0 + 12.0 * len(title_hits)))
    elif title_tokens and stack_tokens:
        hits = [s for s in stack_tokens if s.casefold() in role.casefold()]
        if hits:
            reasons.append(f"Title keywords: {', '.join(hits[:4])}")
            score_parts.append(min(100.0, 40.0 + 10.0 * len(hits)))

    if fit_lane and str(fit_lane).strip():
        lane = str(fit_lane).strip()
        if lane.casefold() in role_text.casefold() or any(
            tok.casefold() in lane.casefold() for tok in title_tokens
        ):
            reasons.append(f"Fit lane: {lane[:60]}")
            score_parts.append(70.0)

    loc_hay = (location_work_style or "").strip()
    loc_filter = (location_filter or "").strip()
    if loc_filter and loc_hay and loc_filter.casefold() in loc_hay.casefold():
        reasons.append(f"Location: {loc_hay[:80]}")
        score_parts.append(75.0)
    elif loc_hay:
        for style in ("remote", "hybrid", "on-site", "onsite"):
            if style in loc_hay.casefold():
                if not loc_filter or style in loc_filter.casefold():
                    reasons.append(f"Location: {loc_hay[:80]}")
                    score_parts.append(60.0 if loc_filter else 55.0)
                break

    if not score_parts:
        fallback = _fit_score(keywords or title_tokens, resume_skills)
        if fallback is not None:
            return float(fallback), reasons
        return None, reasons

    if skill_score is not None and len(score_parts) > 1:
        blended = round(
            0.65 * float(skill_score) + 0.35 * (sum(score_parts) / len(score_parts)),
            1,
        )
    else:
        blended = round(sum(score_parts) / len(score_parts), 1)
    blended = max(0.0, min(100.0, blended))
    return blended, reasons[:6]


def estimate_fit_score(role: str, resume_skills: list[str]) -> float | None:
    keywords = _keyword_harvest(role)
    score = _fit_score(keywords, resume_skills)
    return float(score) if score is not None else None
