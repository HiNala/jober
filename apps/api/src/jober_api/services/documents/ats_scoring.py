from __future__ import annotations

import re
from dataclasses import dataclass

ROLE_KEYWORDS: tuple[str, ...] = (
    "typescript",
    "react",
    "next.js",
    "nextjs",
    "python",
    "fastapi",
    "postgres",
    "postgresql",
    "rag",
    "retrieval",
    "agents",
    "agent",
    "evals",
    "evaluation",
    "embeddings",
    "embedding",
    "vector",
    "openai",
    "claude",
    "gemini",
    "docker",
    "ci/cd",
    "cicd",
    "kubernetes",
    "llm",
    "machine learning",
)

STUFFING_DENSITY_THRESHOLD = 0.12
STUFFING_PENALTY_MAX = 25.0


@dataclass(frozen=True)
class KeywordCoverageReport:
    present: list[str]
    missing: list[str]
    density: float
    stuffing_penalty: float
    ats_score: float


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").casefold()


def extract_target_keywords(job_description: str, job_requirements: str) -> list[str]:
    corpus = _normalize(f"{job_description}\n{job_requirements}")
    found: list[str] = []
    for keyword in ROLE_KEYWORDS:
        if keyword in corpus:
            found.append(keyword)
    return found


def score_keyword_coverage(
    letter_body: str,
    job_description: str,
    job_requirements: str,
    *,
    extra_keywords: list[str] | None = None,
) -> KeywordCoverageReport:
    targets = extract_target_keywords(job_description, job_requirements)
    if extra_keywords:
        for kw in extra_keywords:
            norm = kw.casefold()
            if norm not in targets:
                targets.append(norm)

    body = _normalize(letter_body)
    words = body.split()
    word_count = max(len(words), 1)

    present: list[str] = []
    missing: list[str] = []
    hit_count = 0
    for keyword in targets:
        if keyword in body:
            present.append(keyword)
            hit_count += body.count(keyword)
        else:
            missing.append(keyword)

    density = hit_count / word_count
    stuffing_penalty = 0.0
    if density > STUFFING_DENSITY_THRESHOLD:
        stuffing_penalty = min(
            STUFFING_PENALTY_MAX,
            (density - STUFFING_DENSITY_THRESHOLD) * 200,
        )

    coverage_ratio = len(present) / max(len(targets), 1)
    base_score = coverage_ratio * 100.0
    ats_score = max(0.0, min(100.0, base_score - stuffing_penalty))

    return KeywordCoverageReport(
        present=present,
        missing=missing,
        density=round(density, 4),
        stuffing_penalty=round(stuffing_penalty, 2),
        ats_score=round(ats_score, 1),
    )
