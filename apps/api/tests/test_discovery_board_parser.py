from __future__ import annotations

from jober_api.services.discovery.board_parser import parse_board_html
from tests.fixtures.ats_pages import load_ats_fixture


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
