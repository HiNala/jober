from __future__ import annotations

import httpx
import pytest

from jober_fixtures.outcomes import FIXTURE_OUTCOMES
from jober_fixtures.server import ROUTE_MAP, FixtureServer, create_app
from fastapi.testclient import TestClient


def test_every_route_has_outcome() -> None:
    for slug in ROUTE_MAP:
        assert slug in FIXTURE_OUTCOMES, f"Missing outcome for {slug}"


def test_catalog_lists_all_routes() -> None:
    client = TestClient(create_app())
    body = client.get("/catalog").json()
    assert set(body["routes"]) == set(ROUTE_MAP.keys())


@pytest.fixture(scope="module")
def fixture_server_url() -> str:
    server = FixtureServer(port=18765)
    url = server.start()
    for _ in range(50):
        try:
            httpx.get(f"{url}/health", timeout=1.0).raise_for_status()
            break
        except Exception:
            import time

            time.sleep(0.1)
    else:
        pytest.fail("fixture server failed to start")
    yield url
    server.stop()


@pytest.mark.parametrize("slug", sorted(ROUTE_MAP.keys()))
def test_fixture_page_serves(slug: str, fixture_server_url: str) -> None:
    res = httpx.get(f"{fixture_server_url}/{slug}", timeout=5.0)
    res.raise_for_status()
    assert "<html" in res.text.lower()
