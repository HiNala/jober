"""Synthetic ATS fixtures for offline deterministic testing."""

from jober_fixtures.loaders import load_page, pages_root
from jober_fixtures.outcomes import FIXTURE_OUTCOMES, FixtureOutcome

__all__ = ["FIXTURE_OUTCOMES", "FixtureOutcome", "load_page", "pages_root"]
