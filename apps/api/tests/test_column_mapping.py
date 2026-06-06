from __future__ import annotations

from jober_api.services.xlsx.column_mapping import resolve_sheet_mapping
from jober_api.services.xlsx.sheet_specs import JOB_LEADS_SPEC


def test_fuzzy_header_matching_tolerates_minor_renames() -> None:
    rows = [
        ("Tracker", None, None),
        (
            "Rank",
            "Priority",
            "Employer",
            "Title",
            "Fit lane",
            "Stage / size signal",
            "Location / work style",
            "Why this fits Brian",
            "Cover-letter hook",
            "Public email / contact",
            "Apply link",
            "Company careers / ATS URL",
            "Source / verification note",
            "Verified date",
            "Status",
            "Applied date",
            "Follow-up date",
            "Notes",
        ),
        (
            1,
            "A",
            "Acme",
            "Engineer",
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        ),
    ]
    resolved = resolve_sheet_mapping("Direct Job Leads", rows, JOB_LEADS_SPEC)
    assert resolved is not None
    assert resolved.header_row == 1
    assert resolved.fields["company"] == "Employer"
    assert resolved.fields["role"] == "Title"
    assert resolved.fields["direct_apply_url"] == "Apply link"
