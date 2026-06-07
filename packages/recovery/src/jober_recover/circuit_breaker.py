from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from jober_recover.taxonomy import FailureClass


@dataclass
class CircuitState:
    tripped: bool
    platform: str
    failure_class: str
    count: int
    threshold: int
    message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "tripped": self.tripped,
            "platform": self.platform,
            "failure_class": self.failure_class,
            "count": self.count,
            "threshold": self.threshold,
            "message": self.message,
        }


@dataclass
class CircuitBreaker:
    threshold: int = 5
    _counts: dict[tuple[str, str], int] = field(default_factory=lambda: defaultdict(int))
    _alerts: list[CircuitState] = field(default_factory=list)

    def record(self, platform: str, failure_class: FailureClass | str) -> CircuitState:
        key = (platform.casefold(), str(failure_class))
        self._counts[key] += 1
        count = self._counts[key]
        tripped = count >= self.threshold
        state = CircuitState(
            tripped=tripped,
            platform=platform,
            failure_class=str(failure_class),
            count=count,
            threshold=self.threshold,
            message=(
                f"Circuit breaker: {count} {failure_class} failures on {platform}"
                if tripped
                else None
            ),
        )
        if tripped and not any(
            a.platform == platform and a.failure_class == str(failure_class) for a in self._alerts
        ):
            self._alerts.append(state)
        return state

    def state_for(self, platform: str, failure_class: FailureClass | str) -> CircuitState:
        key = (platform.casefold(), str(failure_class))
        count = self._counts[key]
        tripped = count >= self.threshold
        return CircuitState(
            tripped=tripped,
            platform=platform,
            failure_class=str(failure_class),
            count=count,
            threshold=self.threshold,
            message=(
                f"Circuit breaker: {count} {failure_class} failures on {platform}"
                if tripped
                else None
            ),
        )

    def active_alerts(self) -> list[CircuitState]:
        return list(self._alerts)

    def snapshot_counts(self) -> dict[str, int]:
        return {f"{p}:{fc}": c for (p, fc), c in self._counts.items()}
