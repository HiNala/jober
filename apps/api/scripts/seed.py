#!/usr/bin/env python3
"""Seed local dev data: demo UserProfile and sample JobTargets."""

from __future__ import annotations

import asyncio
import json

from jober_api.config import settings
from jober_api.db.session import async_session_factory
from jober_api.models.enums import JobTargetStatus
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.repositories.user_profile import UserProfileRepository


async def seed() -> None:
    async with async_session_factory() as session:
        profiles = UserProfileRepository(session)
        jobs = JobTargetRepository(session)

        existing = await profiles.list_all(limit=1)
        if existing:
            print("Seed skipped — user profile already exists.")
            return

        await profiles.create(
            name="Brian Permut",
            email="brian@example.com",
            location="Austin, TX (remote-friendly)",
            links={
                "github": "https://github.com/HiNala",
                "linkedin": "https://linkedin.com/in/example",
                "portfolio": "https://glidedesign.com",
            },
            current_title="Founder & Engineer",
            relocation_pref=False,
            hybrid_pref=True,
            onsite_pref=False,
            notice_period="2 weeks",
            salary_prefs={"target_usd": 180000, "floor_usd": 160000},
            sensitive_eeo_answers=json.dumps(
                {"work_authorization": "Authorized to work in the US"},
            ),
            profile_completeness_score=0.72,
            field_consent={
                "work_authorization": {
                    "consent": True,
                    "never_autofill": False,
                    "consented_at": "2026-01-01T00:00:00+00:00",
                },
                "veteran_status": {"consent": True, "never_autofill": True},
            },
        )

        demo_jobs = [
            {
                "rank": 1,
                "priority": "A",
                "company": "Acme AI",
                "role": "Staff AI Engineer",
                "fit_lane": "AI platform",
                "why_fit": "Founder-operator with RAG + agents in production.",
                "cover_letter_hook": "Built Glide's agent stack end-to-end.",
                "direct_apply_url": "https://jobs.example.com/acme/staff-ai",
                "status": JobTargetStatus.QUEUED,
            },
            {
                "rank": 2,
                "priority": "A",
                "company": "Nova Labs",
                "role": "Senior Full-Stack Engineer",
                "fit_lane": "Product eng",
                "why_fit": "Next.js + FastAPI depth; shipped customer-facing AI features.",
                "cover_letter_hook": "Full-stack ownership from UI to eval harness.",
                "direct_apply_url": "https://jobs.example.com/nova/senior-fs",
                "status": JobTargetStatus.NEW,
            },
            {
                "rank": 3,
                "priority": "B",
                "company": "Orbit Health",
                "role": "AI Engineer",
                "fit_lane": "Applied ML",
                "why_fit": "Healthcare-adjacent RAG experience via prior clients.",
                "status": JobTargetStatus.NEW,
            },
        ]
        for row in demo_jobs:
            await jobs.create(**row)

        await session.commit()
        print(f"Seeded 1 profile and {len(demo_jobs)} job targets.")


def main() -> None:
    if not settings.database_url:
        msg = "DATABASE_URL is required"
        raise SystemExit(msg)
    asyncio.run(seed())


if __name__ == "__main__":
    main()
