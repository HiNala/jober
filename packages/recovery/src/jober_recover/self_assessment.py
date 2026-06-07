from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from jober_recover.strategy import RecoveryStrategy
from jober_recover.taxonomy import FailureClass, is_human_only


@dataclass(frozen=True)
class SelfAssessment:
    attempt_index: int
    strategy_name: str
    failure_class: str
    tried: str
    happened: str
    next_change: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "attempt_index": self.attempt_index,
            "strategy_name": self.strategy_name,
            "failure_class": self.failure_class,
            "tried": self.tried,
            "happened": self.happened,
            "next_change": self.next_change,
        }


def build_self_assessment(
    *,
    attempt_index: int,
    strategy: RecoveryStrategy,
    failure_class: FailureClass,
    error_message: str,
    next_strategy: RecoveryStrategy | None,
) -> SelfAssessment:
    if is_human_only(failure_class):
        next_change = "Human handoff required — do not retry automatically"
    elif next_strategy:
        next_change = f"Switch to {next_strategy.name}: {next_strategy.description}"
    else:
        next_change = "Budget exhausted — produce failure report for human review"
    return SelfAssessment(
        attempt_index=attempt_index,
        strategy_name=strategy.name,
        failure_class=failure_class.value,
        tried=strategy.description,
        happened=error_message[:500],
        next_change=next_change,
    )
