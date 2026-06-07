from __future__ import annotations

import re


def normalize_label(label: str) -> str:
    return re.sub(r"\s+", " ", label.strip().casefold())


class InMemoryMappingMemory:
    """Strict mapping memory — stores (platform, label) → profile field only."""

    def __init__(self) -> None:
        self._store: dict[tuple[str, str], str] = {}

    def remember(self, platform: str, label: str, mapped_profile_field: str) -> None:
        self._store[(platform.casefold(), normalize_label(label))] = mapped_profile_field

    def lookup(self, platform: str, label: str) -> str | None:
        return self._store.get((platform.casefold(), normalize_label(label)))
