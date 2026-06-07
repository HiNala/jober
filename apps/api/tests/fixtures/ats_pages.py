from __future__ import annotations

from pathlib import Path

try:
    from jober_fixtures.loaders import load_legacy_ats as _load
except ImportError:
    _load = None

FIXTURE_DIR = Path(__file__).resolve().parent / "ats"


def load_ats_fixture(name: str) -> str:
    if _load is not None:
        return _load(name)
    return (FIXTURE_DIR / f"{name}.html").read_text(encoding="utf-8")
