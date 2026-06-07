from __future__ import annotations

import re
from dataclasses import dataclass

from jober_schemas.job_profile import PlatformDetectionRead

ADAPTER_ORDER = (
    "ashby",
    "lever",
    "greenhouse",
    "workday",
    "jobvite",
    "personio",
    "teamtailor",
    "generic",
)


@dataclass(frozen=True)
class AdapterSignature:
    name: str
    url_patterns: tuple[re.Pattern[str], ...]
    dom_patterns: tuple[re.Pattern[str], ...]
    weight: float = 0.35


ADAPTERS: tuple[AdapterSignature, ...] = (
    AdapterSignature(
        "ashby",
        (re.compile(r"ashbyhq\.com|jobs\.ashby", re.I),),
        (
            re.compile(r"ashby-job-posting|data-testid=[\"']job-posting", re.I),
            re.compile(r"class=[\"'][^\"']*ashby", re.I),
        ),
        weight=0.4,
    ),
    AdapterSignature(
        "lever",
        (re.compile(r"jobs\.lever\.co|lever\.co", re.I),),
        (
            re.compile(r"class=[\"'][^\"']*posting-header", re.I),
            re.compile(r"lever-job|data-qa=[\"']posting", re.I),
        ),
        weight=0.4,
    ),
    AdapterSignature(
        "greenhouse",
        (re.compile(r"greenhouse\.io|boards\.greenhouse", re.I),),
        (
            re.compile(r"id=[\"']content[\"']|class=[\"'][^\"']*content", re.I),
            re.compile(r"greenhouse|#job-description|job__description", re.I),
        ),
        weight=0.4,
    ),
    AdapterSignature(
        "workday",
        (re.compile(r"myworkdayjobs\.com|\.wd\d+\.myworkdayjobs", re.I),),
        (
            re.compile(r"data-automation-id", re.I),
            re.compile(r"workday|wd-popup|css-\w+", re.I),
        ),
        weight=0.35,
    ),
    AdapterSignature(
        "jobvite",
        (re.compile(r"jobvite\.com", re.I),),
        (
            re.compile(r"jv-|jobvite", re.I),
            re.compile(r"class=[\"'][^\"']*jv-", re.I),
        ),
        weight=0.35,
    ),
    AdapterSignature(
        "personio",
        (re.compile(r"personio\.(de|com)|jobs\.personio", re.I),),
        (re.compile(r"personio|data-personio", re.I),),
        weight=0.35,
    ),
    AdapterSignature(
        "teamtailor",
        (re.compile(r"teamtailor\.com", re.I),),
        (re.compile(r"teamtailor|data-teamtailor", re.I),),
        weight=0.35,
    ),
)


def _score_adapter(adapter: AdapterSignature, url: str, html: str) -> tuple[float, list[str]]:
    evidence: list[str] = []
    score = 0.0
    for pattern in adapter.url_patterns:
        if pattern.search(url):
            evidence.append(f"url:{pattern.pattern}")
            score += adapter.weight
            break
    for pattern in adapter.dom_patterns:
        if pattern.search(html):
            evidence.append(f"dom:{pattern.pattern[:48]}")
            score += adapter.weight
    return min(score, 1.0), evidence


def detect_platform(url: str, html: str) -> PlatformDetectionRead:
    best_name = "generic"
    best_score = 0.0
    best_evidence: list[str] = []

    for adapter in ADAPTERS:
        score, evidence = _score_adapter(adapter, url, html)
        if score > best_score:
            best_score = score
            best_name = adapter.name
            best_evidence = evidence

    if best_score < 0.25:
        return PlatformDetectionRead(
            platform="generic",
            confidence=0.2,
            evidence=["fallback:no strong ATS signature"],
        )

    return PlatformDetectionRead(
        platform=best_name,
        confidence=round(best_score, 2),
        evidence=best_evidence,
    )
