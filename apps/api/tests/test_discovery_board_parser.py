from __future__ import annotations

from jober_api.services.discovery.board_parser import (
    estimate_fit_with_reasons,
    parse_board_html,
)
from tests.fixtures.ats_pages import load_ats_fixture


def test_estimate_fit_with_reasons_matched_skills_and_title() -> None:
    score, reasons = estimate_fit_with_reasons(
        "Staff Python Engineer",
        ["Python", "TypeScript", "React"],
        location_work_style="Remote US",
        location_filter="Remote",
        stack=["Python"],
    )
    assert score is not None
    assert score >= 0
    joined = " ".join(reasons).casefold()
    assert "python" in joined or "matched skills" in joined or "title" in joined
    assert any("location" in r.casefold() for r in reasons)


def test_estimate_fit_with_reasons_empty_without_signals() -> None:
    score, reasons = estimate_fit_with_reasons("Mystery Role", [])
    assert score is None
    assert reasons == []


def test_parse_board_html_extracts_ats_links() -> None:
    html = load_ats_fixture("board_listing")
    postings = parse_board_html(
        html=html,
        board_name="Beacon Labs",
        base_url="https://example.com/careers/beacon",
    )
    roles = {posting.role for posting in postings}
    urls = {posting.url for posting in postings}
    assert "Staff Engineer" in roles
    assert "https://jobs.lever.co/beacon/staff-engineer" in urls
    assert all(posting.company == "Beacon Labs" for posting in postings)


def test_parse_board_html_ignores_non_ats_links() -> None:
    html = """
    <a href="https://example.com/about">About us</a>
    <a href="https://jobs.lever.co/acme/role">Engineer</a>
    """
    postings = parse_board_html(html=html, board_name="Acme")
    assert len(postings) == 1
    assert postings[0].role == "Engineer"
