#!/usr/bin/env python3
"""Build apps/web/e2e/fixtures/jobs.xlsx with fixture ATS apply URLs."""

from __future__ import annotations

import os
import sys
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[3] / "api"
sys.path.insert(0, str(API_ROOT))

from tests.fixtures.workbook import build_sample_workbook  # noqa: E402

FIXTURE_BASE = os.environ.get("FIXTURE_ATS_BASE", "http://127.0.0.1:8765").rstrip("/")
OUT = Path(__file__).resolve().parents[1] / "fixtures" / "jobs.xlsx"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    data = build_sample_workbook(
        job_count=2,
        board_count=1,
        angle_count=1,
        apply_url_for_row=lambda i: f"{FIXTURE_BASE}/behaviors/single-step?e2e={i}",
    )
    OUT.write_bytes(data)
    print(f"Wrote {OUT} ({len(data)} bytes) with base {FIXTURE_BASE}")


if __name__ == "__main__":
    main()
