from __future__ import annotations

from pathlib import Path

import pytest
from jober_fill.runner import ObservationInput, run_fill_loop
from playwright.sync_api import sync_playwright

from jober_worker.browser.typed_actions import TypedBrowserActions

FIXTURES = Path(__file__).resolve().parents[2] / "api" / "tests" / "fixtures" / "forms"


def _load(name: str) -> str:
    return (FIXTURES / f"{name}.html").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def playwright_browser():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        yield browser
        browser.close()


def test_fill_loop_uses_label_locator(playwright_browser) -> None:
    page = playwright_browser.new_page()
    page.set_content(_load("single_step"))
    actions = TypedBrowserActions(page)
    outcomes = run_fill_loop(
        [
            ObservationInput(
                field_key="email",
                label="Email address",
                field_type="email",
                mapped_profile_field="email",
                status="skipped",
            ),
            ObservationInput(
                field_key="name",
                label="Full name",
                field_type="text",
                mapped_profile_field="name",
                status="skipped",
            ),
        ],
        {"email": "test@example.com", "name": "Ada Lovelace"},
        {},
        actions,
    )
    page.close()
    assert all(o.status == "filled" for o in outcomes)
    assert all(o.locator_strategy == "label" for o in outcomes)
    assert outcomes[0].fill_diff is not None
    assert outcomes[0].fill_diff.matched is True


def test_upload_fixture_attaches_files(playwright_browser, tmp_path: Path) -> None:
    resume = tmp_path / "resume.pdf"
    cover = tmp_path / "cover.pdf"
    resume.write_bytes(b"%PDF-1.4 resume")
    cover.write_bytes(b"%PDF-1.4 cover")

    page = playwright_browser.new_page()
    page.set_content(_load("dropzone"))
    actions = TypedBrowserActions(page)
    outcomes = run_fill_loop(
        [
            ObservationInput(
                field_key="resume",
                label="Upload resume (PDF)",
                field_type="file",
                mapped_profile_field="resume_upload",
                status="needs_review",
            ),
            ObservationInput(
                field_key="cover",
                label="Attach cover letter",
                field_type="file",
                mapped_profile_field="cover_letter_upload",
                status="needs_review",
            ),
        ],
        {},
        {
            "resume_upload": str(resume),
            "cover_letter_upload": str(cover),
        },
        actions,
    )
    page.close()
    assert len([o for o in outcomes if o.status == "filled"]) == 2


def test_login_fixture_detects_gate_before_fill() -> None:
    from jober_extraction.gates import GateKind, detect_access_gates

    login_html = (
        Path(__file__).resolve().parents[2]
        / "api"
        / "tests"
        / "fixtures"
        / "ats"
        / "login_gate.html"
    )
    html = login_html.read_text(encoding="utf-8")
    gates = detect_access_gates(html, html)
    assert gates
    assert gates[0] == GateKind.LOGIN
