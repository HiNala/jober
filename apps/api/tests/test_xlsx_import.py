from __future__ import annotations

import os

import pytest
from sqlalchemy import func, select

from jober_api.models.company_board import CompanyBoard
from jober_api.models.cover_letter_angle import CoverLetterAngle
from jober_api.models.job_target import JobTarget
from jober_api.services.ats_guess import guess_ats
from jober_api.services.xlsx.export_service import export_jobs_workbook
from jober_api.services.xlsx.import_service import import_jobs_workbook
from jober_api.services.xlsx.parser import parse_workbook_bytes
from tests.fixtures.workbook import build_sample_workbook

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and os.getenv("RUN_DB_TESTS") != "1",
    reason="requires Postgres",
)


def test_guess_ats_from_url() -> None:
    assert guess_ats("https://jobs.lever.co/acme/role") == "lever"
    assert guess_ats("https://boards.greenhouse.io/acme/jobs/1") == "greenhouse"
    assert guess_ats("https://example.com/jobs") is None


def test_parse_workbook_mapping_preview() -> None:
    data = build_sample_workbook(job_count=2, board_count=1, angle_count=1)
    parsed = parse_workbook_bytes(data)
    assert parsed.job_leads is not None
    assert len(parsed.job_leads.records) == 2
    assert parsed.company_boards is not None
    assert parsed.cover_letter_angles is not None
    assert "Summary" in parsed.metadata


@pytest.mark.asyncio
async def test_import_upsert_and_export(db_session, truncate_tables) -> None:
    data = build_sample_workbook(job_count=3, board_count=2, angle_count=2)

    preview = await import_jobs_workbook(db_session, data, dry_run=True)
    assert preview.dry_run is True
    assert preview.job_targets.created == 3

    first = await import_jobs_workbook(db_session, data, dry_run=False)
    assert first.job_targets.created == 3
    assert first.company_boards.created == 2
    assert first.cover_letter_angles.created == 2

    job_count = await db_session.scalar(select(func.count()).select_from(JobTarget))
    assert job_count == 3

    second = await import_jobs_workbook(db_session, data, dry_run=False)
    assert second.job_targets.created == 0
    assert second.job_targets.updated == 3
    job_count_after = await db_session.scalar(select(func.count()).select_from(JobTarget))
    assert job_count_after == 3

    exported = await export_jobs_workbook(db_session)
    assert exported.startswith(b"PK")

    board_count = await db_session.scalar(select(func.count()).select_from(CompanyBoard))
    angle_count = await db_session.scalar(select(func.count()).select_from(CoverLetterAngle))
    assert board_count == 2
    assert angle_count == 2
