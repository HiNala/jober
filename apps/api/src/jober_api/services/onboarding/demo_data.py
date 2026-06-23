"""Sanitized demo data for onboarding and local seed."""

from __future__ import annotations

from typing import Any

from jober_api.models.enums import JobTargetStatus

DEMO_PROFILE: dict[str, Any] = {
    "name": "Alex Rivera",
    "email": "alex@example.com",
    "location": "Remote (US time zones)",
    "links": {
        "github": "https://github.com/example",
        "linkedin": "https://linkedin.com/in/example",
        "portfolio": "https://example.com",
    },
    "current_title": "Senior Software Engineer",
    "relocation_pref": False,
    "hybrid_pref": True,
    "onsite_pref": False,
    "notice_period": "2 weeks",
    "salary_prefs": {"target_usd": 180000, "floor_usd": 160000},
    "sensitive_eeo_answers": '{"work_authorization": "Authorized to work in the US"}',
    "profile_completeness_score": 0.72,
    "field_consent": {
        "work_authorization": {
            "consent": True,
            "never_autofill": False,
            "consented_at": "2026-01-01T00:00:00+00:00",
        },
        "veteran_status": {"consent": True, "never_autofill": True},
    },
}

DEMO_JOBS: list[dict[str, Any]] = [
    {
        "rank": 1,
        "priority": "A",
        "company": "Acme AI",
        "role": "Staff AI Engineer",
        "fit_lane": "AI platform",
        "why_fit": "Production RAG and agent systems with measurable reliability wins.",
        "cover_letter_hook": "Shipped end-to-end agent workflows with human review gates.",
        "direct_apply_url": "https://jobs.example.com/acme/staff-ai",
        "status": JobTargetStatus.QUEUED,
        "source_note": "demo_workspace",
    },
    {
        "rank": 2,
        "priority": "A",
        "company": "Nova Labs",
        "role": "Senior Full-Stack Engineer",
        "fit_lane": "Product eng",
        "why_fit": "Next.js + FastAPI depth; customer-facing features with strong UX.",
        "cover_letter_hook": "Full-stack ownership from UI polish to API contracts.",
        "direct_apply_url": "https://jobs.example.com/nova/senior-fs",
        "status": JobTargetStatus.NEW,
        "source_note": "demo_workspace",
    },
    {
        "rank": 3,
        "priority": "B",
        "company": "Orbit Health",
        "role": "AI Engineer",
        "fit_lane": "Applied ML",
        "why_fit": "Healthcare-adjacent RAG experience and compliance-aware workflows.",
        "direct_apply_url": "https://jobs.example.com/orbit/ai-engineer",
        "status": JobTargetStatus.NEW,
        "source_note": "demo_workspace",
    },
    {
        "rank": 4,
        "priority": "B",
        "company": "Summit Fintech",
        "role": "Backend Engineer",
        "fit_lane": "Platform",
        "why_fit": "Event-driven pipelines and Postgres at scale.",
        "status": JobTargetStatus.APPLIED,
        "source_note": "demo_workspace",
    },
]
