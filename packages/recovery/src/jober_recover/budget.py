from __future__ import annotations

from dataclasses import dataclass

from jober_recover.taxonomy import FailureClass, is_human_only

NORMAL_ATTEMPTS = 3
ALTERNATE_ATTEMPTS = 1


@dataclass(frozen=True)
class AttemptBudget:
    normal_attempts: int = NORMAL_ATTEMPTS
    alternate_attempts: int = ALTERNATE_ATTEMPTS

    @property
    def max_attempts(self) -> int:
        return self.normal_attempts + self.alternate_attempts

    def is_alternate_attempt(self, attempt_index: int) -> bool:
        return attempt_index > self.normal_attempts

    def can_retry(
        self,
        attempt_index: int,
        *,
        failure_class: FailureClass,
    ) -> bool:
        if is_human_only(failure_class):
            return False
        return attempt_index < self.max_attempts

    def next_status(self, attempt_index: int, *, failure_class: FailureClass) -> str:
        if is_human_only(failure_class):
            return "needs_human"
        if self.can_retry(attempt_index, failure_class=failure_class):
            return "failed_retryable"
        return "failed_final"
