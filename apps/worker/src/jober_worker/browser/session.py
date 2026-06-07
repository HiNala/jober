from __future__ import annotations

import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from jober_worker.browser.actions import BrowserActions
from jober_worker.config import settings


@dataclass
class BrowserSession:
    playwright: Playwright
    browser: Browser
    context: BrowserContext
    page: Page
    actions: BrowserActions
    trace_path: Path | None
    video_dir: Path | None


@contextmanager
def browser_session(
    *,
    run_id: uuid.UUID,
    attempt_index: int,
    storage_state: dict[str, Any] | None = None,
) -> Iterator[BrowserSession]:
    artifacts = Path("/tmp/jober-artifacts") / str(run_id) / str(attempt_index)
    artifacts.mkdir(parents=True, exist_ok=True)
    trace_path = artifacts / "trace.zip"
    video_dir = artifacts / "video"

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=not settings.playwright_headed,
            slow_mo=settings.playwright_slow_mo_ms,
        )
        video_dir.mkdir(parents=True, exist_ok=True)
        context = browser.new_context(
            storage_state=storage_state,
            record_video_dir=str(video_dir),
        )
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        page = context.new_page()
        actions = BrowserActions(page)
        session = BrowserSession(
            playwright=playwright,
            browser=browser,
            context=context,
            page=page,
            actions=actions,
            trace_path=trace_path,
            video_dir=video_dir,
        )
        try:
            yield session
        finally:
            context.tracing.stop(path=str(trace_path))
            context.close()
            browser.close()
