from __future__ import annotations

import pytest
from jober_extraction.platform import detect_platform

from tests.fixtures.ats_pages import load_ats_fixture


@pytest.mark.parametrize(
    ("fixture", "url", "expected"),
    [
        ("greenhouse", "https://boards.greenhouse.io/acme/jobs/123", "greenhouse"),
        ("lever", "https://jobs.lever.co/beacon/staff-engineer", "lever"),
        ("ashby", "https://jobs.ashbyhq.com/orbit/founding-engineer", "ashby"),
    ],
)
def test_platform_detection_matches_fixture_ats(fixture: str, url: str, expected: str) -> None:
    html = load_ats_fixture(fixture)
    result = detect_platform(url, html)
    assert result.platform == expected
    assert result.confidence >= 0.25
    assert result.evidence


def test_generic_fallback_when_signals_weak() -> None:
    result = detect_platform("https://example.com/careers", "<html><body>Hello</body></html>")
    assert result.platform == "generic"
    assert result.confidence <= 0.25
