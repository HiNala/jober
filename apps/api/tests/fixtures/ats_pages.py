from __future__ import annotations

from pathlib import Path

FIXTURE_DIR = Path(__file__).resolve().parent / "ats"


def load_ats_fixture(name: str) -> str:
    path = FIXTURE_DIR / f"{name}.html"
    return path.read_text(encoding="utf-8")
