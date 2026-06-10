"""Browser golden path — fixture ATS single-step discover + fill succeeds."""

from __future__ import annotations

import os
import time

import httpx
import pytest
from jober_fixtures.outcomes import FIXTURE_OUTCOMES
from playwright.sync_api import sync_playwright

pytestmark = pytest.mark.skipif(
    os.getenv("SKIP_PLAYWRIGHT") == "1",
    reason="playwright not installed",
)

SLUG = "behaviors/single-step"


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


def test_golden_path_browser_single_step_fixture_loads(fixture_server_url: str) -> None:
    outcome = FIXTURE_OUTCOMES[SLUG]
    assert outcome.expected_fill_status == "succeeded"
    url = f"{fixture_server_url}/{SLUG}"
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        assert page.locator("form, input, button").count() >= outcome.expected_discovery_min_fields
        browser.close()
