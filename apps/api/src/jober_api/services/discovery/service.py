from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.enums import JobTargetStatus
from jober_api.models.job_list import JobListItem
from jober_api.models.job_target import JobTarget
from jober_api.models.saved_search import SavedSearch
from jober_api.repositories.company_board import CompanyBoardRepository
from jober_api.repositories.job_list import JobListRepository
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.repositories.resume_asset import ResumeAssetRepository
from jober_api.services.ats_guess import guess_ats
from jober_api.services.discovery.board_parser import (
    estimate_fit_with_reasons,
    fetch_board_html,
    parse_board_html,
)
from jober_api.services.discovery.dedupe import candidate_key
from jober_api.services.job_extraction.service import enrich_job_target_inline


def _matches_text(haystack: str | None, needle: str) -> bool:
    if not needle:
        return True
    return needle.casefold() in (haystack or "").casefold()


async def _resume_skills(session: AsyncSession, tenant_id: uuid.UUID) -> list[str]:
    resumes = ResumeAssetRepository(session, tenant_id)
    resume = await resumes.get_active()
    if resume and isinstance(resume.skills_index, dict):
        raw = resume.skills_index.get("skills")
        if isinstance(raw, list):
            return [str(skill) for skill in raw]
    return []


def _serialize_candidate(
    *,
    company: str,
    role: str,
    direct_apply_url: str | None,
    company_careers_url: str | None,
    source: str,
    source_label: str,
    stage_signal: str | None,
    location_work_style: str | None,
    fit_score: float | None,
    existing_job_target_id: uuid.UUID | None,
    priority: str | None = None,
    fit_lane: str | None = None,
    fit_reasons: list[str] | None = None,
) -> dict[str, Any]:
    url = direct_apply_url or company_careers_url
    return {
        "candidate_key": candidate_key(company, role, direct_apply_url),
        "company": company,
        "role": role,
        "direct_apply_url": direct_apply_url,
        "company_careers_url": company_careers_url,
        "source": source,
        "source_label": source_label,
        "stage_signal": stage_signal,
        "location_work_style": location_work_style,
        "fit_score": fit_score,
        "fit_reasons": list(fit_reasons or []),
        "ats_guess": guess_ats(url),
        "existing_job_target_id": str(existing_job_target_id) if existing_job_target_id else None,
        "priority": priority,
        "fit_lane": fit_lane,
    }


async def _list_keys_in_job_list(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    list_id: uuid.UUID,
) -> set[str]:
    repo = JobListRepository(session, tenant_id)
    row = await repo.get(list_id)
    if row is None:
        return set()
    keys: set[str] = set()
    for item in row.items:
        job = item.job_target
        keys.add(candidate_key(job.company, job.role, job.direct_apply_url))
    return keys


async def _existing_job_map(
    session: AsyncSession,
    tenant_id: uuid.UUID,
) -> dict[str, JobTarget]:
    repo = JobTargetRepository(session, tenant_id)
    rows = await repo.list_filtered(limit=2000)
    mapping: dict[str, JobTarget] = {}
    for row in rows:
        mapping[candidate_key(row.company, row.role, row.direct_apply_url)] = row
    return mapping


async def search_candidates(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    query: dict[str, Any],
    fixture_html: str | None = None,
) -> list[dict[str, Any]]:
    role_filter = str(query.get("role") or "").strip()
    stack = [str(s).strip() for s in query.get("stack") or [] if str(s).strip()]
    location = str(query.get("location") or "").strip()
    stage = str(query.get("stage") or "").strip()
    work_style = str(query.get("work_style") or "").strip()
    board_urls = [str(url).strip() for url in query.get("board_urls") or [] if str(url).strip()]
    exclude_list_id = query.get("list_id")

    skills = await _resume_skills(session, tenant_id)
    existing_jobs = await _existing_job_map(session, tenant_id)
    exclude_keys = set()
    if exclude_list_id:
        exclude_keys = await _list_keys_in_job_list(
            session,
            tenant_id,
            uuid.UUID(str(exclude_list_id)),
        )

    merged: dict[str, dict[str, Any]] = {}

    def add_candidate(**fields: Any) -> None:
        key = candidate_key(fields["company"], fields["role"], fields.get("direct_apply_url"))
        if key in exclude_keys:
            return
        existing = existing_jobs.get(key)
        role_for_fit = f"{fields['role']} {' '.join(stack)}"
        fit = fields.get("fit_score")
        fit_reasons = fields.get("fit_reasons")
        if not isinstance(fit_reasons, list):
            fit_reasons = None
        if fit is None or fit_reasons is None:
            scored, reasons = estimate_fit_with_reasons(
                role_for_fit,
                skills,
                location_work_style=fields.get("location_work_style"),
                fit_lane=fields.get("fit_lane"),
                location_filter=location or None,
                stack=stack,
            )
            if fit is None:
                fit = scored
            if fit_reasons is None:
                fit_reasons = reasons
        payload = _serialize_candidate(
            company=fields["company"],
            role=fields["role"],
            direct_apply_url=fields.get("direct_apply_url"),
            company_careers_url=fields.get("company_careers_url"),
            source=fields["source"],
            source_label=fields["source_label"],
            stage_signal=fields.get("stage_signal"),
            location_work_style=fields.get("location_work_style"),
            fit_score=fit,
            existing_job_target_id=existing.id if existing else None,
            priority=fields.get("priority"),
            fit_lane=fields.get("fit_lane"),
            fit_reasons=fit_reasons or [],
        )
        if role_filter and not _matches_text(payload["role"], role_filter):
            return
        if location and not _matches_text(payload.get("location_work_style"), location):
            return
        if stage and not _matches_text(payload.get("stage_signal"), stage):
            return
        if work_style and not _matches_text(payload.get("location_work_style"), work_style):
            return
        if (
            stack
            and not any(_matches_text(payload["role"], token) for token in stack)
            and not any(_matches_text(" ".join(skills), token) for token in stack)
        ):
            return
        merged[key] = payload

    board_repo = CompanyBoardRepository(session, tenant_id)
    boards = await board_repo.list_filtered(
        role=role_filter,
        stage=stage,
        location=location,
    )
    for board in boards:
        if board.representative_roles:
            for role_line in board.representative_roles.split(";"):
                role_name = role_line.strip()
                if not role_name:
                    continue
                add_candidate(
                    company=board.company_board,
                    role=role_name,
                    direct_apply_url=None,
                    company_careers_url=board.company_careers_url,
                    source="board",
                    source_label=board.company_board,
                    stage_signal=board.stage_signal,
                    location_work_style=None,
                    priority=board.priority,
                )
        if board.company_careers_url:
            html = await fetch_board_html(board.company_careers_url, fixture_html=fixture_html)
            for posting in parse_board_html(
                html=html,
                board_name=board.company_board,
                base_url=board.company_careers_url,
            ):
                add_candidate(
                    company=posting.company,
                    role=posting.role,
                    direct_apply_url=posting.url,
                    company_careers_url=board.company_careers_url,
                    source="board",
                    source_label=board.company_board,
                    stage_signal=board.stage_signal,
                    location_work_style=None,
                    priority=board.priority,
                )

    for board_url in board_urls:
        html = await fetch_board_html(board_url, fixture_html=fixture_html)
        label = board_url.rstrip("/").split("/")[-1].replace("-", " ").title()
        for posting in parse_board_html(html=html, board_name=label, base_url=board_url):
            add_candidate(
                company=posting.company,
                role=posting.role,
                direct_apply_url=posting.url,
                company_careers_url=board_url,
                source="board",
                source_label=label,
                stage_signal=None,
                location_work_style=None,
            )

    job_repo = JobTargetRepository(session, tenant_id)
    tracker_rows = await job_repo.list_filtered(
        role=role_filter or None,
        location=location or None,
        limit=500,
    )
    for job in tracker_rows:
        profile = job.extracted_job_profile or {}
        fit = profile.get("fit_score") if isinstance(profile, dict) else None
        add_candidate(
            company=job.company,
            role=job.role,
            direct_apply_url=job.direct_apply_url,
            company_careers_url=job.company_careers_url,
            source="tracker",
            source_label=job.source_note or "Queue",
            stage_signal=job.stage_signal,
            location_work_style=job.location_work_style,
            fit_score=float(fit) if isinstance(fit, (int, float)) else None,
            priority=job.priority,
            fit_lane=job.fit_lane,
        )

    results = list(merged.values())
    results.sort(key=lambda row: (row.get("fit_score") is None, -(row.get("fit_score") or 0)))
    return results


async def upsert_job_from_candidate(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    candidate: dict[str, Any],
    priority: str | None = None,
    fit_lane: str | None = None,
    import_id: str | None = None,
) -> JobTarget:
    repo = JobTargetRepository(session, tenant_id)
    existing_id = candidate.get("existing_job_target_id")
    if existing_id:
        row = await repo.get(uuid.UUID(str(existing_id)))
        if row is not None:
            return row

    company = str(candidate["company"])
    role = str(candidate["role"])
    direct_url = candidate.get("direct_apply_url")
    existing = await repo.find_by_upsert_key(
        company,
        role,
        str(direct_url) if direct_url else None,
    )
    if existing is not None:
        return existing

    row = JobTarget(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        company=company,
        role=role,
        direct_apply_url=str(direct_url) if direct_url else None,
        company_careers_url=candidate.get("company_careers_url"),
        stage_signal=candidate.get("stage_signal"),
        location_work_style=candidate.get("location_work_style"),
        priority=priority or candidate.get("priority"),
        fit_lane=fit_lane or candidate.get("fit_lane"),
        source_note=str(candidate.get("source_label") or candidate.get("source")),
        status=JobTargetStatus.NEW,
        import_id=import_id,
    )
    session.add(row)
    await session.flush()
    return row


async def add_job_to_list(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    list_id: uuid.UUID,
    job_target_id: uuid.UUID,
) -> None:
    repo = JobListRepository(session, tenant_id)
    row = await repo.get(list_id)
    if row is None or row.user_id != user_id:
        msg = "Job list not found"
        raise ValueError(msg)
    if any(item.job_target_id == job_target_id for item in row.items):
        return
    sort_order = max((item.sort_order for item in row.items), default=-1) + 1
    session.add(
        JobListItem(
            id=uuid.uuid4(),
            job_list_id=list_id,
            job_target_id=job_target_id,
            sort_order=sort_order,
        )
    )


async def accept_candidates(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    list_id: uuid.UUID,
    candidates: list[dict[str, Any]],
    priority: str | None = None,
    fit_lane: str | None = None,
    enrich: bool = True,
    fixture_html: str | None = None,
) -> dict[str, Any]:
    accepted_ids: list[str] = []
    seen_keys: set[str] = set()
    skipped_duplicates = 0
    for candidate in candidates:
        key = str(
            candidate.get("candidate_key")
            or candidate_key(
                str(candidate["company"]),
                str(candidate["role"]),
                candidate.get("direct_apply_url"),
            )
        )
        if key in seen_keys:
            skipped_duplicates += 1
            continue
        seen_keys.add(key)
        job = await upsert_job_from_candidate(
            session,
            tenant_id=tenant_id,
            candidate=candidate,
            priority=priority,
            fit_lane=fit_lane,
        )
        await add_job_to_list(
            session,
            tenant_id=tenant_id,
            user_id=user_id,
            list_id=list_id,
            job_target_id=job.id,
        )
        if enrich and (job.direct_apply_url or job.company_careers_url):
            await enrich_job_target_inline(
                session,
                tenant_id=tenant_id,
                job_target_id=job.id,
                fixture_html=fixture_html,
            )
        accepted_ids.append(str(job.id))
    result: dict[str, Any] = {
        "accepted": len(accepted_ids),
        "job_target_ids": accepted_ids,
    }
    if skipped_duplicates:
        result["skipped_duplicates"] = skipped_duplicates
    return result


async def attach_import_to_list(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    list_id: uuid.UUID,
    import_id: str,
) -> dict[str, int]:
    repo = JobListRepository(session, tenant_id)
    job_list = await repo.get(list_id)
    if job_list is None or job_list.user_id != user_id:
        msg = "Job list not found"
        raise ValueError(msg)
    stmt = select(JobTarget).where(
        JobTarget.tenant_id == tenant_id,
        JobTarget.import_id == import_id,
    )
    result = await session.execute(stmt)
    attached = 0
    for job in result.scalars().all():
        await add_job_to_list(
            session,
            tenant_id=tenant_id,
            user_id=user_id,
            list_id=list_id,
            job_target_id=job.id,
        )
        attached += 1
    return {"attached": attached}


async def refresh_list_candidates(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    list_id: uuid.UUID,
    fixture_html: str | None = None,
) -> list[dict[str, Any]]:
    repo = JobListRepository(session, tenant_id)
    job_list = await repo.get(list_id)
    if job_list is None or job_list.user_id != user_id:
        msg = "Job list not found"
        raise ValueError(msg)

    query: dict[str, Any] = {"list_id": str(list_id)}
    if job_list.saved_search_id:
        saved = await session.get(SavedSearch, job_list.saved_search_id)
        if saved is not None and saved.user_id == user_id:
            query = {**saved.query, "list_id": str(list_id)}

    all_candidates = await search_candidates(
        session,
        tenant_id=tenant_id,
        query=query,
        fixture_html=fixture_html,
    )
    in_list = await _list_keys_in_job_list(session, tenant_id, list_id)
    return [row for row in all_candidates if row["candidate_key"] not in in_list]


async def list_saved_searches(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
) -> list[dict[str, Any]]:
    stmt = (
        select(SavedSearch)
        .where(SavedSearch.tenant_id == tenant_id, SavedSearch.user_id == user_id)
        .order_by(SavedSearch.updated_at.desc())
    )
    result = await session.execute(stmt)
    return [
        {
            "id": str(row.id),
            "name": row.name,
            "query": row.query,
            "created_at": row.created_at.isoformat(),
            "updated_at": row.updated_at.isoformat(),
        }
        for row in result.scalars().all()
    ]


async def create_saved_search(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    name: str,
    query: dict[str, Any],
) -> dict[str, Any]:
    row = SavedSearch(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        user_id=user_id,
        name=name.strip(),
        query=query,
    )
    session.add(row)
    await session.flush()
    return {
        "id": str(row.id),
        "name": row.name,
        "query": row.query,
        "created_at": row.created_at.isoformat(),
        "updated_at": row.updated_at.isoformat(),
    }


async def link_list_to_saved_search(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    list_id: uuid.UUID,
    saved_search_id: uuid.UUID | None,
) -> None:
    repo = JobListRepository(session, tenant_id)
    row = await repo.get(list_id)
    if row is None or row.user_id != user_id:
        msg = "Job list not found"
        raise ValueError(msg)
    if saved_search_id is not None:
        saved = await session.get(SavedSearch, saved_search_id)
        if saved is None or saved.user_id != user_id:
            msg = "Saved search not found"
            raise ValueError(msg)
    row.saved_search_id = saved_search_id
    row.updated_at = datetime.now(UTC)
