from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from jober_api.models.application_run import ApplicationRun
from jober_api.repositories.company_board import CompanyBoardRepository
from jober_api.repositories.cover_letter_angle import CoverLetterAngleRepository
from jober_api.repositories.job_target import JobTargetRepository
from jober_api.services.ats_guess import needs_apply_url
from jober_api.services.xlsx.column_mapping import mapping_preview
from jober_api.services.xlsx.normalize import (
    clean_text,
    normalize_priority,
    normalize_url,
    parse_date,
    parse_int,
    parse_status,
)
from jober_api.services.xlsx.parser import WorkbookParseResult, parse_workbook_bytes
from jober_api.services.xlsx.sheet_specs import (
    COMPANY_BOARDS_SPEC,
    COVER_LETTER_ANGLES_SPEC,
    JOB_LEADS_SPEC,
)


@dataclass
class ImportWarning:
    sheet: str
    row: int | None
    code: str
    message: str

    def as_dict(self) -> dict[str, object]:
        return {
            "sheet": self.sheet,
            "row": self.row,
            "code": self.code,
            "message": self.message,
        }


@dataclass
class EntityImportStats:
    created: int = 0
    updated: int = 0
    skipped: int = 0

    def as_dict(self) -> dict[str, int]:
        return {"created": self.created, "updated": self.updated, "skipped": self.skipped}


@dataclass
class ImportReport:
    import_id: str
    dry_run: bool
    mappings: dict[str, list[dict[str, object]]]
    metadata_sheets: list[str]
    job_targets: EntityImportStats = field(default_factory=EntityImportStats)
    company_boards: EntityImportStats = field(default_factory=EntityImportStats)
    cover_letter_angles: EntityImportStats = field(default_factory=EntityImportStats)
    warnings: list[ImportWarning] = field(default_factory=list)

    def as_dict(self) -> dict[str, object]:
        return {
            "import_id": self.import_id,
            "dry_run": self.dry_run,
            "mappings": self.mappings,
            "metadata_sheets": self.metadata_sheets,
            "job_targets": self.job_targets.as_dict(),
            "company_boards": self.company_boards.as_dict(),
            "cover_letter_angles": self.cover_letter_angles.as_dict(),
            "warnings": [w.as_dict() for w in self.warnings],
        }


def _upsert_key(company: str, role: str, url: str | None) -> tuple[str, str, str | None]:
    return (company.casefold(), role.casefold(), url)


def _row_num(raw: dict[str, object]) -> int:
    return int(str(raw["_row"]))


async def _has_application_runs(session: AsyncSession, job_target_id: uuid.UUID) -> bool:
    stmt = (
        select(func.count())
        .select_from(ApplicationRun)
        .where(ApplicationRun.job_target_id == job_target_id)
    )
    result = await session.execute(stmt)
    return int(result.scalar_one()) > 0


def _build_mapping_preview(parsed: WorkbookParseResult) -> dict[str, list[dict[str, object]]]:
    previews: dict[str, list[dict[str, object]]] = {}
    if parsed.job_leads:
        previews["job_targets"] = mapping_preview(JOB_LEADS_SPEC, parsed.job_leads.mapping)
    if parsed.company_boards:
        previews["company_boards"] = mapping_preview(
            COMPANY_BOARDS_SPEC, parsed.company_boards.mapping
        )
    if parsed.cover_letter_angles:
        previews["cover_letter_angles"] = mapping_preview(
            COVER_LETTER_ANGLES_SPEC, parsed.cover_letter_angles.mapping
        )
    return previews


async def import_jobs_workbook(
    session: AsyncSession,
    data: bytes,
    *,
    tenant_id: uuid.UUID,
    dry_run: bool = False,
    import_id: str | None = None,
) -> ImportReport:
    run_id = import_id or str(uuid.uuid4())
    parsed = parse_workbook_bytes(data)
    report = ImportReport(
        import_id=run_id,
        dry_run=dry_run,
        mappings=_build_mapping_preview(parsed),
        metadata_sheets=list(parsed.metadata.keys()),
    )

    if parsed.job_leads is None:
        report.warnings.append(
            ImportWarning(
                sheet="Direct Job Leads",
                row=None,
                code="sheet_missing",
                message="Could not locate or map Direct Job Leads sheet",
            )
        )
    if parsed.company_boards is None:
        report.warnings.append(
            ImportWarning(
                sheet="Company Boards",
                row=None,
                code="sheet_missing",
                message="Could not locate or map Company Boards sheet",
            )
        )
    if parsed.cover_letter_angles is None:
        report.warnings.append(
            ImportWarning(
                sheet="Cover Letter Angles",
                row=None,
                code="sheet_missing",
                message="Could not locate or map Cover Letter Angles sheet",
            )
        )

    if dry_run:
        if parsed.job_leads:
            report.job_targets.created = len(parsed.job_leads.records)
        if parsed.company_boards:
            report.company_boards.created = len(parsed.company_boards.records)
        if parsed.cover_letter_angles:
            report.cover_letter_angles.created = len(parsed.cover_letter_angles.records)
        return report

    job_repo = JobTargetRepository(session, tenant_id)
    board_repo = CompanyBoardRepository(session)
    angle_repo = CoverLetterAngleRepository(session)

    seen_job_keys: dict[tuple[str, str, str | None], int] = {}

    if parsed.job_leads:
        sheet = parsed.job_leads.sheet_name
        for raw in parsed.job_leads.records:
            row_num = _row_num(raw)
            company = clean_text(raw.get("company"))
            role = clean_text(raw.get("role"))
            if not company:
                report.warnings.append(
                    ImportWarning(sheet, row_num, "missing_company", "Row missing company")
                )
                report.job_targets.skipped += 1
                continue
            if not role:
                report.warnings.append(
                    ImportWarning(sheet, row_num, "missing_role", "Row missing role")
                )
                report.job_targets.skipped += 1
                continue

            direct_url, url_warn = normalize_url(raw.get("direct_apply_url"))
            careers_url, careers_warn = normalize_url(raw.get("company_careers_url"))
            for code, msg in (
                (url_warn, "Invalid direct apply URL"),
                (careers_warn, "Invalid company careers URL"),
            ):
                if code:
                    report.warnings.append(ImportWarning(sheet, row_num, code, msg))

            key = _upsert_key(company, role, direct_url)
            if key in seen_job_keys:
                report.warnings.append(
                    ImportWarning(
                        sheet,
                        row_num,
                        "duplicate_row",
                        f"Duplicate of row {seen_job_keys[key]} in file",
                    )
                )
            else:
                seen_job_keys[key] = row_num

            if not direct_url:
                report.warnings.append(
                    ImportWarning(
                        sheet,
                        row_num,
                        "ambiguous_upsert_key",
                        "No direct apply URL — upsert falls back to (company, role)",
                    )
                )

            if needs_apply_url(direct_url, careers_url):
                report.warnings.append(
                    ImportWarning(
                        sheet,
                        row_num,
                        "needs_url",
                        "Both apply and careers URLs are blank",
                    )
                )

            existing_job = await job_repo.find_by_upsert_key(company, role, direct_url)
            sheet_status = parse_status(raw.get("status"))
            fields: dict[str, object] = {
                "rank": parse_int(raw.get("rank")),
                "priority": normalize_priority(raw.get("priority")),
                "company": company,
                "role": role,
                "fit_lane": clean_text(raw.get("fit_lane")),
                "stage_signal": clean_text(raw.get("stage_signal")),
                "location_work_style": clean_text(raw.get("location_work_style")),
                "why_fit": clean_text(raw.get("why_fit")),
                "cover_letter_hook": clean_text(raw.get("cover_letter_hook")),
                "public_contact": clean_text(raw.get("public_contact")),
                "direct_apply_url": direct_url,
                "company_careers_url": careers_url,
                "source_note": clean_text(raw.get("source_note")),
                "verified_date": parse_date(raw.get("verified_date")),
                "applied_date": parse_date(raw.get("applied_date")),
                "follow_up_date": parse_date(raw.get("follow_up_date")),
                "notes": clean_text(raw.get("notes")),
                "import_id": run_id,
            }

            if existing_job is None:
                fields["status"] = sheet_status
                fields["tenant_id"] = tenant_id
                await job_repo.create(**fields)
                report.job_targets.created += 1
            else:
                has_runs = await _has_application_runs(session, existing_job.id)
                if not has_runs:
                    fields["status"] = sheet_status
                else:
                    fields["status"] = existing_job.status
                    if sheet_status != existing_job.status:
                        report.warnings.append(
                            ImportWarning(
                                sheet,
                                row_num,
                                "status_preserved",
                                "App status kept over spreadsheet (runs exist)",
                            )
                        )
                for attr, value in fields.items():
                    setattr(existing_job, attr, value)
                report.job_targets.updated += 1

    if parsed.company_boards:
        sheet = parsed.company_boards.sheet_name
        for raw in parsed.company_boards.records:
            row_num = _row_num(raw)
            name = clean_text(raw.get("company_board"))
            if not name:
                report.warnings.append(
                    ImportWarning(sheet, row_num, "missing_board", "Row missing company board")
                )
                report.company_boards.skipped += 1
                continue
            careers_url, careers_warn = normalize_url(raw.get("company_careers_url"))
            if careers_warn:
                report.warnings.append(
                    ImportWarning(sheet, row_num, careers_warn, "Invalid careers URL")
                )
            fields = {
                "priority": normalize_priority(raw.get("priority")),
                "company_board": name,
                "representative_roles": clean_text(raw.get("representative_roles")),
                "stage_signal": clean_text(raw.get("stage_signal")),
                "why_save": clean_text(raw.get("why_save")),
                "company_careers_url": careers_url,
                "last_checked": parse_date(raw.get("last_checked")),
                "notes": clean_text(raw.get("notes")),
            }
            existing_board = await board_repo.find_by_company_board(name)
            if existing_board is None:
                await board_repo.create(**fields)
                report.company_boards.created += 1
            else:
                for attr, value in fields.items():
                    setattr(existing_board, attr, value)
                report.company_boards.updated += 1

    if parsed.cover_letter_angles:
        sheet = parsed.cover_letter_angles.sheet_name
        for raw in parsed.cover_letter_angles.records:
            row_num = _row_num(raw)
            use_case = clean_text(raw.get("use_case"))
            template = clean_text(raw.get("template"))
            if not use_case or not template:
                report.warnings.append(
                    ImportWarning(
                        sheet,
                        row_num,
                        "missing_angle",
                        "Row missing use case or template",
                    )
                )
                report.cover_letter_angles.skipped += 1
                continue
            existing_angle = await angle_repo.find_by_use_case(use_case)
            if existing_angle is None:
                await angle_repo.create(use_case=use_case, template=template)
                report.cover_letter_angles.created += 1
            else:
                existing_angle.template = template
                report.cover_letter_angles.updated += 1

    await session.commit()
    return report
