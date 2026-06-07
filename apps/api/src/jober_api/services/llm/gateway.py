from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol

import httpx
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.config import settings
from jober_api.models.llm_call import LlmCall


class BudgetExceededError(Exception):
    pass


@dataclass(frozen=True)
class LlmCompletion:
    content: str
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    latency_ms: int


class LlmProvider(Protocol):
    async def complete(
        self,
        *,
        model: str,
        system: str,
        user: str,
        temperature: float = 0.4,
    ) -> LlmCompletion: ...


def _estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    # Rough OpenAI-style estimates for budgeting in dev/CI.
    if "gpt-4" in model.lower():
        return prompt_tokens * 0.00003 + completion_tokens * 0.00006
    return prompt_tokens * 0.0000005 + completion_tokens * 0.0000015


def redact_text(text: str, limit: int = 400) -> str:
    trimmed = text.strip()
    if len(trimmed) <= limit:
        return trimmed
    return f"{trimmed[:limit]}…"


def _resume_block_from_prompt(user: str) -> str:
    marker = "=== RESUME (source of truth for claims) ==="
    if marker not in user:
        return ""
    return user.split(marker, 1)[1].strip()


def _supported_skill_labels(resume_text: str) -> list[str]:
    from jober_api.services.claims_index import build_claims_index, claim_supported

    claims = build_claims_index(resume_text, {"skills": []})
    candidates = [
        "Python",
        "FastAPI",
        "TypeScript",
        "React",
        "Next.js",
        "RAG",
        "Docker",
        "Postgres",
        "embeddings",
        "CI/CD",
    ]
    return [label for label in candidates if claim_supported(claims, label)]


class TemplateLlmProvider:
    """Deterministic provider for tests and offline dev (no API key)."""

    async def complete(
        self,
        *,
        model: str,
        system: str,
        user: str,
        temperature: float = 0.4,
    ) -> LlmCompletion:
        del system, temperature
        company = "the company"
        role = "this role"
        hook = ""
        for line in user.splitlines():
            lower = line.lower()
            if lower.startswith("company:"):
                company = line.split(":", 1)[1].strip() or company
            if lower.startswith("role:"):
                role = line.split(":", 1)[1].strip() or role
            if lower.startswith("cover-letter hook:"):
                hook = line.split(":", 1)[1].strip()

        resume_text = _resume_block_from_prompt(user)
        skills = _supported_skill_labels(resume_text)
        skill_phrase = ", ".join(skills[:4]) if skills else "the technologies in my resume"
        opener = hook or "Your mission aligns with how I build."

        evidence_1 = (
            f"In prior roles I owned delivery end-to-end with {skill_phrase}. I scoped work with "
            "product partners, wrote the interfaces and services myself, and kept feedback loops "
            "short so we could ship iteratively instead of debating hypotheticals."
        )
        evidence_2 = (
            f"Technically, I lean on {skill_phrase} where they fit the problem, not because they "
            "are fashionable. I document decisions, add observability early, and treat reliability "
            "as part of the user experience rather than a post-launch patch."
        )
        evidence_3 = (
            "I am comfortable presenting tradeoffs to leadership and mentoring teammates on "
            "execution. I step into ambiguous spaces when the roadmap is still forming. That "
            "operator posture is what I would bring to your team from day one."
        )
        evidence_4 = (
            "Across engagements I have paired with design and go-to-market partners to validate "
            "assumptions quickly, cut scope when learning demands it, and keep quality high when "
            "deadlines are real. I care about maintainable codebases and kind collaboration."
        )

        body = (
            f"Dear {company} team,\n\n"
            f"I am excited about the {role} opportunity. {opener} "
            f"I have shipped production systems using {skill_phrase}, with a founder-operator "
            "mindset focused on measurable outcomes rather than slide decks.\n\n"
            f"{evidence_1}\n\n"
            f"{evidence_2}\n\n"
            f"{evidence_3}\n\n"
            f"{evidence_4}\n\n"
            "I would welcome a conversation about how I can contribute. I am available to start "
            "after a standard notice period and happy to walk through relevant work samples. "
            "Thank you for your consideration."
        )
        payload = {
            "body": body,
            "asserted_facts": skills,
            "paragraph_grounding": [
                {
                    "paragraph_index": 0,
                    "resume_facts": skills[:2] or ["resume experience"],
                    "job_keywords": [company, role],
                },
                {
                    "paragraph_index": 1,
                    "resume_facts": skills,
                    "job_keywords": skills[:3],
                },
            ],
        }
        content = json.dumps(payload)
        prompt_tokens = max(1, len(user) // 4)
        completion_tokens = max(1, len(content) // 4)
        return LlmCompletion(
            content=content,
            provider="template",
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_usd=_estimate_cost(model, prompt_tokens, completion_tokens),
            latency_ms=5,
        )


class HttpLlmProvider:
    async def complete(
        self,
        *,
        model: str,
        system: str,
        user: str,
        temperature: float = 0.4,
    ) -> LlmCompletion:
        if not settings.llm_api_key:
            msg = "LLM_API_KEY is not configured"
            raise ValueError(msg)
        base_url = settings.llm_base_url.rstrip("/")
        started = time.perf_counter()
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {settings.llm_api_key}"},
                json={
                    "model": model,
                    "temperature": temperature,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    "response_format": {"type": "json_object"},
                },
            )
            response.raise_for_status()
            data = response.json()
        latency_ms = int((time.perf_counter() - started) * 1000)
        usage = data.get("usage", {})
        prompt_tokens = int(usage.get("prompt_tokens", 0))
        completion_tokens = int(usage.get("completion_tokens", 0))
        content = data["choices"][0]["message"]["content"]
        return LlmCompletion(
            content=content,
            provider=settings.llm_provider,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_usd=_estimate_cost(model, prompt_tokens, completion_tokens),
            latency_ms=latency_ms,
        )


def get_llm_provider() -> LlmProvider:
    if settings.llm_provider == "template" or not settings.llm_api_key:
        return TemplateLlmProvider()
    return HttpLlmProvider()


async def monthly_llm_spend(session: AsyncSession) -> float:
    month_start = datetime.now(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    stmt = select(func.coalesce(func.sum(LlmCall.cost_usd), 0.0)).where(
        LlmCall.created_at >= month_start,
    )
    result = await session.execute(stmt)
    value = result.scalar_one()
    return float(value or 0.0)


async def assert_budget(session: AsyncSession, projected_cost: float = 0.0) -> None:
    budget = settings.llm_monthly_budget_usd
    if budget <= 0:
        return
    spent = await monthly_llm_spend(session)
    if spent + projected_cost > budget:
        msg = (
            f"LLM monthly budget exceeded (${spent:.2f} spent, "
            f"${budget:.2f} cap). Generation blocked."
        )
        raise BudgetExceededError(msg)


async def log_llm_call(
    session: AsyncSession,
    *,
    agent_role: str,
    completion: LlmCompletion,
    system: str,
    user: str,
    run_id: Any = None,
) -> LlmCall:
    row = LlmCall(
        run_id=run_id,
        agent_role=agent_role,
        provider=completion.provider,
        model=completion.model,
        prompt_tokens=completion.prompt_tokens,
        completion_tokens=completion.completion_tokens,
        cost_usd=completion.cost_usd,
        latency_ms=completion.latency_ms,
        redacted_prompt=redact_text(f"{system}\n\n{user}"),
        redacted_response=redact_text(completion.content),
    )
    session.add(row)
    await session.flush()
    return row
