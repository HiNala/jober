#!/usr/bin/env python3
"""Seed realistic volume for Mission 23 perf drills (~150 jobs, ~50 runs, ~10k events)."""

from __future__ import annotations

import argparse
import asyncio

from jober_api.config import settings
from jober_api.db.session import async_session_factory
from jober_api.services.dev.perf_volume import (
    DEFAULT_EVENT_COUNT,
    DEFAULT_JOB_COUNT,
    DEFAULT_RUN_COUNT,
    seed_perf_volume,
)


async def main(
    *,
    jobs: int,
    runs: int,
    events: int,
) -> None:
    async with async_session_factory() as session:
        stats = await seed_perf_volume(
            session,
            job_count=jobs,
            run_count=runs,
            event_count=events,
        )
    print(
        f"Seeded perf volume: {stats['job_targets']} job targets, "
        f"{stats['runs']} runs, {stats['analytics_events']} analytics events "
        f"(tenant {stats['tenant_id']})."
    )


def cli() -> None:
    parser = argparse.ArgumentParser(description="Seed Mission 23 perf volume dataset")
    parser.add_argument("--jobs", type=int, default=DEFAULT_JOB_COUNT)
    parser.add_argument("--runs", type=int, default=DEFAULT_RUN_COUNT)
    parser.add_argument("--events", type=int, default=DEFAULT_EVENT_COUNT)
    args = parser.parse_args()
    if not settings.database_url:
        raise SystemExit("DATABASE_URL is required")
    asyncio.run(main(jobs=args.jobs, runs=args.runs, events=args.events))


if __name__ == "__main__":
    cli()
