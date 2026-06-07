from __future__ import annotations

import os
import time

import httpx
import pytest
from jober_fixtures.outcomes import FIXTURE_OUTCOMES
from jober_forms.scanner import scan_multistep_form
from playwright.sync_api import sync_playwright

pytestmark = pytest.mark.skipif(
    os.getenv("SKIP_PLAYWRIGHT") == "1",
    reason="playwright not installed",
)

BEHAVIOR_SLUGS = [
    slug
    for slug in sorted(FIXTURE_OUTCOMES)
    if slug.startswith("behaviors/") and FIXTURE_OUTCOMES[slug].expected_discovery_min_fields > 0
]


@pytest.fixture(scope="module")
def fixture_server_url() -> str:
    from jober_fixtures.server import FixtureServer

    port = int(os.getenv("FIXTURE_ATS_PORT", "8766"))
    server = FixtureServer(port=port)
    url = server.start()
    for _ in range(50):
        try:
            httpx.get(f"{url}/health", timeout=1.0).raise_for_status()
            break
        except Exception:
            time.sleep(0.1)
    else:
        pytest.fail("fixture server failed to start")
    yield url
    server.stop()


@pytest.mark.parametrize("slug", BEHAVIOR_SLUGS)
def test_browser_fixture_discovery(slug: str, fixture_server_url: str) -> None:
    outcome = FIXTURE_OUTCOMES[slug]
    url = f"{fixture_server_url}/{slug}"
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        html = page.content()
        browser.close()
    fields = scan_multistep_form(html)
    assert len(fields) >= outcome.expected_discovery_min_fields


def test_shifting_selector_label_survives_id_change(fixture_server_url: str) -> None:
    url = f"{fixture_server_url}/behaviors/shifting-selector"
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        locator = page.get_by_label("Email address")
        assert locator.count() == 1
        locator.fill("ada@example.com")
        assert locator.input_value() == "ada@example.com"
        browser.close()
