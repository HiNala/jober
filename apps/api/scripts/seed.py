#!/usr/bin/env python3
"""Seed local dev data: demo UserProfile and sample JobTargets."""

from __future__ import annotations

import asyncio

from jober_api.auth.constants import DEFAULT_DEV_TENANT_ID, DEFAULT_DEV_USER_ID
from jober_api.config import settings
from jober_api.db.session import async_session_factory
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.repositories.user_profile import UserProfileRepository
from jober_api.services.onboarding.demo_workspace import DemoWorkspaceError, seed_demo_workspace


async def seed() -> None:
    async with async_session_factory() as session:
        profiles = UserProfileRepository(session, DEFAULT_DEV_TENANT_ID)
        if await profiles.get_for_tenant() is not None:
            jobs = JobTargetRepository(session, DEFAULT_DEV_TENANT_ID)
            if await jobs.list_filtered(limit=1):
                print("Seed skipped — workspace already has data.")
                return
        try:
            result = await seed_demo_workspace(
                session,
                tenant_id=DEFAULT_DEV_TENANT_ID,
                user_id=DEFAULT_DEV_USER_ID,
            )
        except DemoWorkspaceError as exc:
            print(f"Seed skipped — {exc}")
            return
        print(f"Seeded demo workspace: {result['jobs_created']} jobs.")


def main() -> None:
    if not settings.database_url:
        msg = "DATABASE_URL is required"
        raise SystemExit(msg)
    asyncio.run(seed())


if __name__ == "__main__":
    main()
