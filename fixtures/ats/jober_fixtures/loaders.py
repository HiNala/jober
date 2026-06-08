from __future__ import annotations

from pathlib import Path

PAGES_ROOT = Path(__file__).resolve().parent / "pages"


def pages_root() -> Path:
    return PAGES_ROOT


def load_page(*parts: str) -> str:
    """Load HTML by path segments, e.g. load_page('behaviors', 'single_step')."""
    path = PAGES_ROOT.joinpath(*parts)
    if not path.suffix:
        path = path.with_suffix(".html")
    return path.read_text(encoding="utf-8")


def load_legacy_form(name: str) -> str:
    """Compatibility with Mission 07 form fixture names."""
    return load_page("behaviors", name)


_LEGACY_ATS_PATHS: dict[str, tuple[str, ...]] = {
    "greenhouse": ("jobs", "greenhouse"),
    "lever": ("jobs", "lever"),
    "ashby": ("jobs", "ashby"),
    "workday": ("jobs", "workday"),
    "login_gate": ("gates", "login_gate"),
    "captcha_gate": ("gates", "captcha_gate"),
    "injection": ("security", "injection"),
    "board_listing": ("jobs", "board_listing"),
}


def load_legacy_ats(name: str) -> str:
    """Compatibility with Mission 06 ATS job page names."""
    parts = _LEGACY_ATS_PATHS.get(name, ("jobs", name))
    return load_page(*parts)
