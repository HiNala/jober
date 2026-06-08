from jober_api.services.preferences.defaults import (
    DEFAULT_USER_PREFERENCES,
    deep_merge,
    merged_preferences,
)


def test_merged_preferences_fills_defaults() -> None:
    prefs = merged_preferences({"appearance": {"theme": "light"}})
    assert prefs["appearance"]["theme"] == "light"
    assert prefs["appearance"]["density"] == DEFAULT_USER_PREFERENCES["appearance"]["density"]
    assert prefs["notifications"]["in_app_run_attention"] is True


def test_deep_merge_nested() -> None:
    base = {"a": {"b": 1, "c": 2}}
    patch = {"a": {"c": 3, "d": 4}}
    assert deep_merge(base, patch) == {"a": {"b": 1, "c": 3, "d": 4}}
