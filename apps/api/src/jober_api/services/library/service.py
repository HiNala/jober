from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.application_run import ApplicationRun
from jober_api.models.enums import DocumentType
from jober_api.models.generated_document import GeneratedDocument
from jober_api.models.job_list import JobList
from jober_api.models.job_target import JobTarget
from jober_api.repositories.job_list import JobListRepository
from jober_api.repositories.resume_asset import ResumeAssetRepository
from jober_api.serializers.profile import serialize_resume

DEFAULT_LIBRARY_LIMIT = 50
MAX_LIBRARY_LIMIT = 200


async def list_resumes(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    *,
    limit: int = DEFAULT_LIBRARY_LIMIT,
    offset: int = 0,
) -> list[dict[str, Any]]:
    repo = ResumeAssetRepository(session, tenant_id)
    rows = await repo.list_all(limit=min(limit, MAX_LIBRARY_LIMIT), offset=offset)
    return [serialize_resume(row) for row in rows]


async def list_cover_letters(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    *,
    query: str | None = None,
    limit: int = DEFAULT_LIBRARY_LIMIT,
    offset: int = 0,
) -> list[dict[str, Any]]:
    stmt = (
        select(GeneratedDocument, JobTarget)
        .join(JobTarget, GeneratedDocument.job_target_id == JobTarget.id)
        .where(
            JobTarget.tenant_id == tenant_id,
            GeneratedDocument.document_type == DocumentType.COVER_LETTER,
        )
        .order_by(GeneratedDocument.generated_at.desc().nulls_last())
        .limit(min(limit, MAX_LIBRARY_LIMIT))
        .offset(offset)
    )
    if query:
        pattern = f"%{query.strip()}%"
        stmt = stmt.where(
            or_(
                JobTarget.company.ilike(pattern),
                JobTarget.role.ilike(pattern),
                GeneratedDocument.text.ilike(pattern),
            )
        )
    result = await session.execute(stmt)
    items: list[dict[str, Any]] = []
    for doc, job in result.all():
        preview = (doc.text or "")[:240]
        items.append(
            {
                "id": str(doc.id),
                "job_target_id": str(job.id),
                "company": job.company,
                "role": job.role,
                "ats_score": doc.ats_score,
                "generated_at": doc.generated_at.isoformat() if doc.generated_at else None,
                "preview": preview,
                "is_template": bool((doc.keyword_coverage or {}).get("locked_template")),
            }
        )
    return items


async def list_runs(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    *,
    limit: int = DEFAULT_LIBRARY_LIMIT,
    offset: int = 0,
) -> list[dict[str, Any]]:
    stmt = (
        select(ApplicationRun, JobTarget)
        .join(JobTarget, ApplicationRun.job_target_id == JobTarget.id)
        .where(ApplicationRun.tenant_id == tenant_id)
        .order_by(ApplicationRun.updated_at.desc())
        .limit(min(limit, MAX_LIBRARY_LIMIT))
        .offset(offset)
    )
    result = await session.execute(stmt)
    return [
        {
            "id": str(run.id),
            "job_target_id": str(job.id),
            "company": job.company,
            "role": job.role,
            "status": run.status.value,
            "policy": run.policy.value,
            "updated_at": run.updated_at.isoformat(),
            "created_at": run.created_at.isoformat(),
        }
        for run, job in result.all()
    ]


async def search_library(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    query: str,
    *,
    limit: int = 30,
) -> dict[str, list[dict[str, Any]]]:
    needle = query.strip()
    if not needle:
        return {"jobs": [], "cover_letters": [], "runs": [], "lists": []}

    pattern = f"%{needle}%"
    jobs_stmt = (
        select(JobTarget)
        .where(
            JobTarget.tenant_id == tenant_id,
            or_(
                JobTarget.company.ilike(pattern),
                JobTarget.role.ilike(pattern),
                JobTarget.location_work_style.ilike(pattern),
            ),
        )
        .limit(limit)
    )
    jobs = [
        {
            "id": str(row.id),
            "company": row.company,
            "role": row.role,
            "status": row.status.value,
        }
        for row in (await session.execute(jobs_stmt)).scalars().all()
    ]

    letters = await list_cover_letters(session, tenant_id, query=needle, limit=limit)
    runs = [
        row
        for row in await list_runs(session, tenant_id, limit=limit)
        if needle.lower() in f"{row['company']} {row['role']} {row['status']}".lower()
    ]

    lists_stmt = (
        select(JobList)
        .where(
            JobList.tenant_id == tenant_id,
            JobList.user_id == user_id,
            JobList.archived.is_(False),
            JobList.name.ilike(pattern),
        )
        .limit(limit)
    )
    lists = [
        {"id": str(row.id), "name": row.name}
        for row in (await session.execute(lists_stmt)).scalars().all()
    ]

    return {
        "jobs": jobs,
        "cover_letters": letters,
        "runs": runs,
        "lists": lists,
    }


def serialize_job_list(row: JobList) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "name": row.name,
        "description": row.description,
        "archived": row.archived,
        "created_at": row.created_at.isoformat(),
        "updated_at": row.updated_at.isoformat(),
        "items": [
            {
                "id": str(item.id),
                "job_target_id": str(item.job_target_id),
                "sort_order": item.sort_order,
                "company": item.job_target.company if item.job_target else None,
                "role": item.job_target.role if item.job_target else None,
                "status": item.job_target.status.value if item.job_target else None,
            }
            for item in sorted(row.items, key=lambda i: i.sort_order)
        ],
    }


async def list_job_lists(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    *,
    include_archived: bool = False,
    limit: int = DEFAULT_LIBRARY_LIMIT,
    offset: int = 0,
) -> list[dict[str, Any]]:
    repo = JobListRepository(session, tenant_id)
    rows = await repo.list_for_user(
        user_id,
        include_archived=include_archived,
        limit=min(limit, MAX_LIBRARY_LIMIT),
        offset=offset,
    )
    return [serialize_job_list(row) for row in rows]
