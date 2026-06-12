#!/usr/bin/env python3
"""Seed tenant, user, profile, and resume for Playwright full-stack e2e."""

from __future__ import annotations

import asyncio
import json

from jober_api.auth.constants import DEFAULT_DEV_TENANT_ID, DEFAULT_DEV_USER_ID
from jober_api.config import settings
from jober_api.db.session import async_session_factory
from jober_api.models.enums import PlanTier, UserStatus
from jober_api.models.tenant import Tenant
from jober_api.models.user import User
from jober_api.repositories.resume_asset import ResumeAssetRepository
from jober_api.repositories.user_profile import UserProfileRepository
from jober_api.services.claims_index import build_claims_index  # noqa: I001


async def seed_e2e() -> None:
    async with async_session_factory() as session:
        tenant = await session.get(Tenant, DEFAULT_DEV_TENANT_ID)
        if tenant is None:
            session.add(
                Tenant(
                    id=DEFAULT_DEV_TENANT_ID,
                    name="E2E Tenant",
                    plan=PlanTier.PRO,
                    policy={
                        "default_run_policy": "review_before_submit",
                        "auto_submit_opt_in": False,
                    },
                )
            )
        user = await session.get(User, DEFAULT_DEV_USER_ID)
        if user is None:
            session.add(
                User(
                    id=DEFAULT_DEV_USER_ID,
                    tenant_id=DEFAULT_DEV_TENANT_ID,
                    email="dev@test.local",
                    display_name="E2E User",
                    status=UserStatus.ACTIVE,
                )
            )

        profiles = UserProfileRepository(session)
        profile = await profiles.get_singleton()
        if profile is None:
            profile = await profiles.create(
                name="E2E Candidate",
                email="e2e-candidate@example.com",
                sensitive_eeo_answers=json.dumps(
                    {"work_authorization": "Authorized to work in the US"},
                ),
                field_consent={
                    "work_authorization": {
                        "consent": True,
                        "never_autofill": False,
                    },
                },
            )

        resumes = ResumeAssetRepository(session, DEFAULT_DEV_TENANT_ID)
        active = await resumes.get_active()
        if active is None:
            text = (
                "E2E candidate built Python FastAPI systems with RAG, agents, "
                "and Docker in production."
            )
            skills_index = {
                "skills": ["Python", "FastAPI", "RAG", "Docker"],
                "claims_index": build_claims_index(
                    text,
                    {"skills": ["Python", "FastAPI", "RAG", "Docker"]},
                ),
            }
            resume = await resumes.create(
                object_key=f"tenants/{DEFAULT_DEV_TENANT_ID}/resumes/e2e/resume.docx",
                original_filename="e2e-resume.docx",
                extracted_text=text,
                skills_index=skills_index,
                is_active=True,
            )
            profile.default_resume_asset_id = resume.id

        await session.commit()
        print(
            f"E2E seed ready (tenant={DEFAULT_DEV_TENANT_ID}, llm_provider={settings.llm_provider})",
        )


if __name__ == "__main__":
    asyncio.run(seed_e2e())
