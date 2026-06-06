from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SheetColumnSpec:
    field: str
    aliases: tuple[str, ...]
    required: bool = False


@dataclass(frozen=True)
class SheetSpec:
    sheet_names: tuple[str, ...]
    columns: tuple[SheetColumnSpec, ...]
    min_matches: int = 3


JOB_LEADS_SPEC = SheetSpec(
    sheet_names=("Direct Job Leads", "Direct job leads", "Job Leads"),
    min_matches=5,
    columns=(
        SheetColumnSpec("rank", ("Rank",)),
        SheetColumnSpec("priority", ("Priority",)),
        SheetColumnSpec("company", ("Company",), required=True),
        SheetColumnSpec("role", ("Role",), required=True),
        SheetColumnSpec("fit_lane", ("Fit lane", "Fit Lane")),
        SheetColumnSpec("stage_signal", ("Stage / size signal", "Stage signal", "Stage")),
        SheetColumnSpec("location_work_style", ("Location / work style", "Location")),
        SheetColumnSpec("why_fit", ("Why this fits Brian", "Why fit", "Why this fits")),
        SheetColumnSpec("cover_letter_hook", ("Cover-letter hook", "Cover letter hook")),
        SheetColumnSpec("public_contact", ("Public email / contact", "Public contact", "Email")),
        SheetColumnSpec("direct_apply_url", ("Direct apply URL", "Apply URL")),
        SheetColumnSpec(
            "company_careers_url",
            ("Company careers / ATS URL", "Careers URL", "ATS URL"),
        ),
        SheetColumnSpec("source_note", ("Source / verification note", "Source note")),
        SheetColumnSpec("verified_date", ("Verified date",)),
        SheetColumnSpec("status", ("Status",)),
        SheetColumnSpec("applied_date", ("Applied date",)),
        SheetColumnSpec("follow_up_date", ("Follow-up date", "Follow up date")),
        SheetColumnSpec("notes", ("Notes",)),
    ),
)

COMPANY_BOARDS_SPEC = SheetSpec(
    sheet_names=("Company Boards", "Company boards"),
    min_matches=3,
    columns=(
        SheetColumnSpec("priority", ("Priority",)),
        SheetColumnSpec("company_board", ("Company / board", "Company board"), required=True),
        SheetColumnSpec(
            "representative_roles",
            ("Representative roles in tracker", "Representative roles"),
        ),
        SheetColumnSpec("stage_signal", ("Stage / size signal", "Stage signal")),
        SheetColumnSpec("why_save", ("Why save this board", "Why save")),
        SheetColumnSpec("company_careers_url", ("Company careers / ATS URL", "Careers URL")),
        SheetColumnSpec("last_checked", ("Last checked",)),
        SheetColumnSpec("notes", ("Notes",)),
    ),
)

COVER_LETTER_ANGLES_SPEC = SheetSpec(
    sheet_names=("Cover Letter Angles", "Cover letter angles"),
    min_matches=2,
    columns=(
        SheetColumnSpec("use_case", ("Use case",), required=True),
        SheetColumnSpec("template", ("Template / angle", "Template"), required=True),
    ),
)
