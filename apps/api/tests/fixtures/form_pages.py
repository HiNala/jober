from __future__ import annotations

from pathlib import Path

FIXTURE_DIR = Path(__file__).resolve().parent / "forms"


def load_form_fixture(name: str) -> str:
    return (FIXTURE_DIR / f"{name}.html").read_text(encoding="utf-8")
